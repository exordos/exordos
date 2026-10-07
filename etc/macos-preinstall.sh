#!/bin/sh
#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

set -eu

# Remove the previous package-managed bundle so upgrades cannot retain stale code.
# Installer supplies the target volume as its third argument.
rm -rf "${3:?Missing installation target}/usr/local/lib/exordos/pkg"
