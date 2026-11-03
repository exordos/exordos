#!/bin/sh
#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

set -eu

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 COMPONENT_DIR PACKAGE_PATH" >&2
    exit 2
fi

COMPONENT_DIR=$1
PACKAGE_PATH=$2
for ARCH in arm64 x86_64; do
    [ -f "$COMPONENT_DIR/macos-$ARCH.pkg" ]
    [ -s "$COMPONENT_DIR/macos-$ARCH.pkg.version" ]
done
cmp "$COMPONENT_DIR/macos-arm64.pkg.version" "$COMPONENT_DIR/macos-x86_64.pkg.version"
[ ! -e "$PACKAGE_PATH" ]

set -- --distribution "$(dirname "$0")/macos-distribution.xml" \
    --package-path "$COMPONENT_DIR"
if [ -n "${MACOS_INSTALLER_IDENTITY:-}" ]; then
    set -- "$@" --sign "$MACOS_INSTALLER_IDENTITY" --timestamp
fi
productbuild "$@" "$PACKAGE_PATH"
