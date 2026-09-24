#!/bin/bash
# Hotfix script to install Ansible collections from local .tar.gz files
# This bypasses Ansible Galaxy during the Galaxy outage

set -e

COLLECTIONS_DIR="/tmp/hotfix-collections"
COLLECTIONS_PATH="/usr/share/ansible/collections"

echo "=== Hotfix: Installing collections from local tar.gz files ==="
echo "Collections directory: ${COLLECTIONS_DIR}"
echo "Target path: ${COLLECTIONS_PATH}"

if [ ! -d "${COLLECTIONS_DIR}" ]; then
    echo "ERROR: Collections directory ${COLLECTIONS_DIR} does not exist"
    exit 1
fi

# Count tar.gz files
TAR_COUNT=$(find "${COLLECTIONS_DIR}" -name "*.tar.gz" -type f | wc -l)
echo "Found ${TAR_COUNT} collection archive(s) to install"

if [ "${TAR_COUNT}" -eq 0 ]; then
    echo "WARNING: No .tar.gz files found in ${COLLECTIONS_DIR}"
    exit 0
fi

# Install each collection
# Using --offline to prevent Galaxy API calls for dependency resolution
# Using --no-deps since we have all dependencies as separate tarballs
for tarball in "${COLLECTIONS_DIR}"/*.tar.gz; do
    if [ -f "${tarball}" ]; then
        echo "Installing: $(basename "${tarball}")"
        ansible-galaxy collection install "${tarball}" \
            --collections-path "${COLLECTIONS_PATH}" \
            --force \
            --offline \
            --no-deps
    fi
done

echo "=== Hotfix installation complete ==="
ansible-galaxy collection list --collections-path "${COLLECTIONS_PATH}"
