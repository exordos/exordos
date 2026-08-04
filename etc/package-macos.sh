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

[ -d "$BUNDLE_DIR/_internal" ] || {
    echo "Missing runtime directory: $BUNDLE_DIR/_internal" >&2
    exit 1
}
[ -x "$BUNDLE_DIR/exordos" ] || {
    echo "Missing executable launcher: $BUNDLE_DIR/exordos" >&2
    exit 1
}
[ ! -e "$ARCHIVE_PATH" ] || {
    echo "Archive already exists: $ARCHIVE_PATH" >&2
    exit 1
}

/usr/bin/ditto -c -k --keepParent --norsrc --noextattr --noqtn --noacl \
    "$BUNDLE_DIR" "$ARCHIVE_PATH"

ARCHIVE_HASH=$(shasum -a 256 "$ARCHIVE_PATH")
ARCHIVE_HASH=${ARCHIVE_HASH%% *}
printf '%s\n' "$ARCHIVE_HASH" > "$ARCHIVE_PATH.sha256"
