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
ARCH=$(uname -m)
case "$ARCH" in
    arm64|x86_64) ;;
    *) echo "Unsupported macOS architecture: $ARCH" >&2; exit 1 ;;
esac
VERSION=$("$BUNDLE_DIR/exordos" --silent --no-check-updates version)
# pkgbuild requires a numeric package version, including for prereleases.
PACKAGE_VERSION=$(printf '%s\n' "$VERSION" | sed 's/[^0-9.].*$//; s/\.$//')
PACKAGE_ROOT=$(mktemp -d)
trap 'rm -rf "$PACKAGE_ROOT"' EXIT

mkdir -p "$PACKAGE_ROOT/root/usr/local/lib/exordos" "$PACKAGE_ROOT/root/usr/local/bin"
ditto "$BUNDLE_DIR" "$PACKAGE_ROOT/root/usr/local/lib/exordos/pkg"
ln -s ../lib/exordos/pkg/exordos "$PACKAGE_ROOT/root/usr/local/bin/exordos"

mkdir -p "$PACKAGE_ROOT/scripts"
cp "$(dirname "$0")/macos-preinstall.sh" "$PACKAGE_ROOT/scripts/preinstall"
chmod +x "$PACKAGE_ROOT/scripts/preinstall"

set -- --root "$PACKAGE_ROOT/root" --scripts "$PACKAGE_ROOT/scripts" --identifier "com.exordos.cli.$ARCH" \
    --version "$PACKAGE_VERSION" --install-location / --ownership recommended
pkgbuild "$@" "$PACKAGE_PATH"
printf '%s\n' "$VERSION" > "$PACKAGE_PATH.version"
