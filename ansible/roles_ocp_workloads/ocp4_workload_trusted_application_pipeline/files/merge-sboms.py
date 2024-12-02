#!/bin/python3
import hashlib
import json
import os
import re

### load SBOMs ###

with open(os.getenv("TEMP_DIR") + "/files/sbom-image.json") as f:
  image_sbom = json.load(f)

with open(os.getenv("TEMP_DIR") + "/files/sbom-source.json") as f:
  source_sbom = json.load(f)


### attempt to deduplicate components ###

component_list = image_sbom.get("components", [])
existing_purls = [c["purl"] for c in component_list if "purl" in c]

for component in source_sbom.get("components", []):
  if "purl" in component:
    if component["purl"] not in existing_purls:
      component_list.append(component)
      existing_purls.append(component["purl"])
  else:
    # We won't try to deduplicate components that lack a purl.
    # This should only happen with operating-system type components,
    # which are only reported in the image SBOM.
    component_list.append(component)

component_list.sort(key=lambda c: c["type"] + c["name"])
image_sbom["components"] = component_list


### write the CycloneDX unified SBOM ###

with open(os.getenv("TEMP_DIR") + "/files/sbom-cyclonedx.json", "w") as f:
  json.dump(image_sbom, f, indent=4)


### write the SBOM blob URL result ###

with open(os.getenv("TEMP_DIR") + "/files/sbom-cyclonedx.json", "rb") as f:
  sbom_digest = hashlib.file_digest(f, "sha256").hexdigest()

# https://github.com/opencontainers/distribution-spec/blob/main/spec.md?plain=1#L160
tag_regex = "[a-zA-Z0-9_][a-zA-Z0-9._-]{0,127}"

# the tag must be after a colon, but always at the end of the string
# this avoids conflict with port numbers
image_without_tag = re.sub(f":{tag_regex}\$", "", os.getenv("IMAGE"))

sbom_blob_url = f"{image_without_tag}@sha256:{sbom_digest}"

with open(os.getenv("RESULT_PATH"), "w") as f:
  f.write(sbom_blob_url)