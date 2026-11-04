#!/bin/sh
#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

set -eu

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 BUNDLE_DIR ARCHIVE_PATH" >&2
    exit 2
fi

BUNDLE_DIR=$1
ARCHIVE_PATH=$2
[ -d "$BUNDLE_DIR/_internal" ] && [ -x "$BUNDLE_DIR/exordos" ] || {
    echo "Missing executable or runtime in $BUNDLE_DIR" >&2
    exit 1
}
[ "$(basename "$BUNDLE_DIR")" = exordos ] || exit 1
[ ! -e "$ARCHIVE_PATH" ] || {
    echo "Archive already exists: $ARCHIVE_PATH" >&2
    exit 1
}

tar -cJf "$ARCHIVE_PATH" -C "$(dirname "$BUNDLE_DIR")" exordos
ARCHIVE_HASH=$(sha256sum "$ARCHIVE_PATH")
printf '%s\n' "${ARCHIVE_HASH%% *}" > "$ARCHIVE_PATH.sha256"
