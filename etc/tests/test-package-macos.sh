#!/bin/sh
#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

set -eu

REPOSITORY_ROOT=$(CDPATH='' cd -- "$(dirname "$0")/../.." && pwd)
TEST_ROOT=$(mktemp -d)
trap 'rm -rf "$TEST_ROOT"' EXIT
mkdir -p "$TEST_ROOT/bin" "$TEST_ROOT/bundle/_internal"

cat > "$TEST_ROOT/bundle/exordos" <<'EOF'
#!/bin/sh
printf '%s\n' "$MOCK_CLI_VERSION"
EOF
cat > "$TEST_ROOT/bin/uname" <<'EOF'
#!/bin/sh
echo arm64
EOF
cat > "$TEST_ROOT/bin/ditto" <<'EOF'
#!/bin/sh
cp -R "$1" "$2"
EOF
cat > "$TEST_ROOT/bin/pkgbuild" <<'EOF'
#!/bin/sh
set -eu
while [ "$#" -gt 1 ]; do
    case "$1" in
        --root) ROOT=$2 ;;
        --scripts) SCRIPTS=$2 ;;
        --version) VERSION=$2 ;;
    esac
    shift 2
done
[ -x "$ROOT/usr/local/lib/exordos/pkg/exordos" ]
[ -L "$ROOT/usr/local/bin/exordos" ]
[ -x "$SCRIPTS/preinstall" ]
printf '%s\n' "$VERSION" > "$1"
cp "$SCRIPTS/preinstall" "$1.preinstall"
EOF
chmod +x "$TEST_ROOT/bundle/exordos" "$TEST_ROOT/bin/"*
export PATH="$TEST_ROOT/bin:$PATH"

for MOCK_CLI_VERSION in 3.2.21 3.2.21.dev4 3.2.21rc1 3.2.21a1 3.2.21b2 \
    3.2.21.post1 3.2.21-dev4 3.2.21+gabcdef; do
    export MOCK_CLI_VERSION
    PACKAGE="$TEST_ROOT/$MOCK_CLI_VERSION.pkg"
    sh "$REPOSITORY_ROOT/etc/package-macos-pkg.sh" "$TEST_ROOT/bundle" "$PACKAGE"
    [ "$(cat "$PACKAGE")" = 3.2.21 ]
    [ "$(cat "$PACKAGE.version")" = "$MOCK_CLI_VERSION" ]
done

# Upgrade cleanup removes only the package-managed bundle on the target volume.
TARGET="$TEST_ROOT/volume"
mkdir -p "$TARGET/usr/local/lib/exordos/pkg/_internal" \
    "$TARGET/usr/local/lib/exordos/versions/3.2.20"
: > "$TARGET/usr/local/lib/exordos/pkg/_internal/obsolete"
: > "$TARGET/usr/local/lib/exordos/versions/3.2.20/retained"
sh "$PACKAGE.preinstall" ignored ignored "$TARGET"
[ ! -e "$TARGET/usr/local/lib/exordos/pkg" ]
[ -e "$TARGET/usr/local/lib/exordos/versions/3.2.20/retained" ]
[ -x "$TEST_ROOT/bundle/exordos" ]

echo "macOS component packaging tests passed"
