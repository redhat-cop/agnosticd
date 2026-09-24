#!/usr/bin/env python
"""
Download Ansible collections as tar.gz files for offline installation.
Bypasses Galaxy API issues by using direct download links.
"""

import argparse
import os
import sys
import yaml
import requests
from pathlib import Path

# Galaxy API endpoints
GALAXY_API_BASE = "https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index"
GALAXY_DOWNLOAD_BASE = "https://galaxy.ansible.com/download"

# Red Hat Automation Hub endpoints (require tokens from console.redhat.com)
CERTIFIED_API_BASE = "https://console.redhat.com/api/automation-hub/v3/plugin/ansible/content/published/collections/index"
VALIDATED_API_BASE = "https://console.redhat.com/api/automation-hub/v3/plugin/ansible/content/validated/collections/index"

# Red Hat SSO endpoint for token exchange
REDHAT_SSO_URL = "https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token"

# Cache for exchanged access tokens
_access_token_cache: dict[str, str] = {}

def get_access_token(offline_token: str) -> str | None:
    """Exchange an offline token for an access token via Red Hat SSO."""
    if offline_token in _access_token_cache:
        return _access_token_cache[offline_token]

    try:
        resp = requests.post(
            REDHAT_SSO_URL,
            data={
                "grant_type": "refresh_token",
                "client_id": "cloud-services",
                "refresh_token": offline_token,
            },
            timeout=30,
        )
        resp.raise_for_status()
        access_token = resp.json().get("access_token")
        if access_token:
            _access_token_cache[offline_token] = access_token
            return access_token
    except Exception as e:
        print(f"  ERROR: Failed to exchange token: {e}")
    return None


# Collections that require Red Hat Automation Hub CERTIFIED token
# These are NOT available on public galaxy.ansible.com
REDHAT_CERTIFIED_COLLECTIONS = {
    "ansible.controller",
    "ansible.platform",
    "redhat.artifact_signer",
    "redhat.insights",
    "redhat.openshift",
    "redhat.openshift_virtualization",
    "redhat.rhbk",
    "redhat.rhel_system_roles",
    "redhat.satellite",
    "redhat.trusted_profile_analyzer",
}

# Collections that require Red Hat Automation Hub VALIDATED token
# Currently empty since infra.* collections are on public Galaxy
# But keeping for future use if needed
REDHAT_VALIDATED_COLLECTIONS: set[str] = set()


def get_latest_version_galaxy(namespace: str, name: str) -> str | None:
    """Get the latest version of a collection from Galaxy."""
    url = f"{GALAXY_API_BASE}/{namespace}/{name}/versions/"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("data"):
            return data["data"][0]["version"]
    except Exception as e:
        print(f"  WARNING: Could not get version info for {namespace}.{name}: {e}")
    return None


def get_latest_version_redhat(namespace: str, name: str, offline_token: str, validated: bool = False) -> str | None:
    """Get the latest version of a collection from Red Hat Automation Hub."""
    # Exchange offline token for access token
    access_token = get_access_token(offline_token)
    if not access_token:
        print(f"  ERROR: Could not get access token for Red Hat API")
        return None

    base = VALIDATED_API_BASE if validated else CERTIFIED_API_BASE
    url = f"{base}/{namespace}/{name}/versions/"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("data"):
            return data["data"][0]["version"]
    except Exception as e:
        print(f"  WARNING: Could not get version info for {namespace}.{name}: {e}")
    return None


def download_collection_galaxy(namespace: str, name: str, version: str, output_dir: Path) -> bool:
    """Download a collection tarball from Galaxy."""
    filename = f"{namespace}-{name}-{version}.tar.gz"
    output_path = output_dir / filename

    if output_path.exists():
        print(f"  SKIP: {filename} already exists")
        return True

    url = f"{GALAXY_DOWNLOAD_BASE}/{filename}"
    try:
        print(f"  Downloading: {url}")
        resp = requests.get(url, timeout=120, stream=True)
        resp.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"  OK: {filename} ({output_path.stat().st_size / 1024:.1f} KB)")
        return True
    except Exception as e:
        print(f"  ERROR downloading {filename}: {e}")
        return False


def download_collection_redhat(namespace: str, name: str, version: str, offline_token: str,
                                output_dir: Path, validated: bool = False) -> bool:
    """Download a collection tarball from Red Hat Automation Hub."""
    filename = f"{namespace}-{name}-{version}.tar.gz"
    output_path = output_dir / filename

    if output_path.exists():
        print(f"  SKIP: {filename} already exists")
        return True

    # Exchange offline token for access token
    access_token = get_access_token(offline_token)
    if not access_token:
        print(f"  ERROR: Could not get access token for Red Hat API")
        return False

    base = VALIDATED_API_BASE if validated else CERTIFIED_API_BASE
    url = f"{base}/{namespace}/{name}/versions/{version}/"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        # First get the download URL from the version endpoint
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        download_url = data.get("download_url")

        if not download_url:
            print(f"  ERROR: No download URL found for {namespace}.{name}")
            return False

        print(f"  Downloading: {download_url}")
        resp = requests.get(download_url, headers=headers, timeout=120, stream=True)
        resp.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"  OK: {filename} ({output_path.stat().st_size / 1024:.1f} KB)")
        return True
    except Exception as e:
        print(f"  ERROR downloading {filename}: {e}")
        return False


def process_collection(collection: dict, output_dir: Path,
                       certified_token: str | None, validated_token: str | None) -> tuple[str, bool]:
    """Process a single collection entry."""
    name = collection.get("name", "")
    if not name or name.startswith("https://"):
        return name, False

    parts = name.split(".")
    if len(parts) != 2:
        print(f"  SKIP: Invalid collection name format: {name}")
        return name, False

    namespace, coll_name = parts
    full_name = f"{namespace}.{coll_name}"

    print(f"\nProcessing: {full_name}")

    # Determine source and get version
    if full_name in REDHAT_CERTIFIED_COLLECTIONS:
        if not certified_token:
            print(f"  SKIP: {full_name} requires --certified-token")
            return full_name, False
        version = get_latest_version_redhat(namespace, coll_name, certified_token, validated=False)
        if version:
            return full_name, download_collection_redhat(
                namespace, coll_name, version, certified_token, output_dir, validated=False
            )
    elif full_name in REDHAT_VALIDATED_COLLECTIONS:
        if not validated_token:
            print(f"  SKIP: {full_name} requires --validated-token")
            return full_name, False
        version = get_latest_version_redhat(namespace, coll_name, validated_token, validated=True)
        if version:
            return full_name, download_collection_redhat(
                namespace, coll_name, version, validated_token, output_dir, validated=True
            )
    else:
        # Community Galaxy
        version = get_latest_version_galaxy(namespace, coll_name)
        if version:
            return full_name, download_collection_galaxy(namespace, coll_name, version, output_dir)

    return full_name, False


def main():
    parser = argparse.ArgumentParser(description="Download Ansible collections for offline use")
    parser.add_argument(
        "-r", "--requirements",
        default="requirements.yml",
        help="Path to requirements.yml file"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="hotfix-collections",
        help="Output directory for downloaded tarballs"
    )
    parser.add_argument(
        "--certified-token",
        help="Token for Red Hat Automation Hub certified content"
    )
    parser.add_argument(
        "--validated-token",
        help="Token for Red Hat Automation Hub validated content"
    )
    parser.add_argument(
        "--galaxy-only",
        action="store_true",
        help="Only download from community Galaxy (skip Red Hat collections)"
    )
    args = parser.parse_args()

    # Load requirements
    req_path = Path(args.requirements)
    if not req_path.exists():
        print(f"ERROR: Requirements file not found: {req_path}")
        sys.exit(1)

    with open(req_path) as f:
        requirements = yaml.safe_load(f)

    collections = requirements.get("collections", [])
    if not collections:
        print("No collections found in requirements.yml")
        sys.exit(0)

    print(f"Found {len(collections)} collections in {req_path}")

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir.absolute()}")

    # Get tokens from args or environment
    certified_token = args.certified_token or os.environ.get("AAP_CERTIFIED_TOKEN") or os.environ.get("ANSIBLE_GALAXY_SERVER_CERTIFIED_TOKEN")
    validated_token = args.validated_token or os.environ.get("AAP_VALIDATED_TOKEN") or os.environ.get("ANSIBLE_GALAXY_SERVER_VALIDATED_TOKEN")

    # Process collections
    success = []
    failed = []
    skipped = []

    for coll in collections:
        name = coll.get("name", "")
        full_name = name

        # Skip git-based collections
        if name.startswith("https://"):
            print(f"\nSKIP: Git-based collection: {name}")
            skipped.append(name)
            continue

        parts = name.split(".")
        if len(parts) == 2:
            full_name = f"{parts[0]}.{parts[1]}"

            # Skip Red Hat collections if --galaxy-only
            if args.galaxy_only and (full_name in REDHAT_CERTIFIED_COLLECTIONS or
                                      full_name in REDHAT_VALIDATED_COLLECTIONS):
                print(f"\nSKIP: Red Hat collection (--galaxy-only): {full_name}")
                skipped.append(full_name)
                continue

        coll_name, ok = process_collection(coll, output_dir, certified_token, validated_token)
        if ok:
            success.append(coll_name)
        else:
            failed.append(coll_name)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Success: {len(success)}")
    print(f"Failed:  {len(failed)}")
    print(f"Skipped: {len(skipped)}")

    if failed:
        print("\nFailed collections:")
        for name in failed:
            print(f"  - {name}")

    if skipped:
        print("\nSkipped collections:")
        for name in skipped:
            print(f"  - {name}")

    print(f"\nDownloaded files in: {output_dir.absolute()}")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
