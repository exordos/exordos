#!/bin/sh
#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

set -eu

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 BUNDLE_DIR PACKAGE_PATH" >&2
    exit 2
fi

BUNDLE_DIR=$1
PACKAGE_PATH=$2
[ -d "$BUNDLE_DIR/_internal" ]
[ -x "$BUNDLE_DIR/exordos" ]
[ ! -e "$PACKAGE_PATH" ]
VERSION=$("$BUNDLE_DIR/exordos" --silent --no-check-updates version)
# pkgbuild requires a numeric package version, including for prereleases.
PACKAGE_VERSION=${VERSION%%[-+]*}
PACKAGE_ROOT=$(mktemp -d)
trap 'rm -rf "$PACKAGE_ROOT"' EXIT

mkdir -p "$PACKAGE_ROOT/usr/local/lib/exordos" "$PACKAGE_ROOT/usr/local/bin"
/usr/bin/ditto "$BUNDLE_DIR" "$PACKAGE_ROOT/usr/local/lib/exordos/pkg"
ln -s ../lib/exordos/pkg/exordos "$PACKAGE_ROOT/usr/local/bin/exordos"

set -- --root "$PACKAGE_ROOT" --identifier com.exordos.cli \
    --version "$PACKAGE_VERSION" --install-location / --ownership recommended
if [ -n "${MACOS_INSTALLER_IDENTITY:-}" ]; then
    set -- "$@" --sign "$MACOS_INSTALLER_IDENTITY" --timestamp
fi
pkgbuild "$@" "$PACKAGE_PATH"
