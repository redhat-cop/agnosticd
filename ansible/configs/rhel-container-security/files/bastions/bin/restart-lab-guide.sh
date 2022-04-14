#!/bin/bash
#
podman rm -f lab-guide

podman run --restart=always -d -p 8080:10080 --name=lab-guide quay.io/bkozdemb/labguide
