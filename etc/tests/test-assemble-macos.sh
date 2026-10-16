#!/bin/sh
#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

set -eu

REPOSITORY_ROOT=$(CDPATH='' cd -- "$(dirname "$0")/../.." && pwd)
TEST_ROOT=$(mktemp -d)
trap 'rm -rf "$TEST_ROOT"' EXIT
mkdir -p "$TEST_ROOT/bin" "$TEST_ROOT/components"

# Assert that invalid components never reach productbuild.
cat > "$TEST_ROOT/bin/productbuild" <<'EOF'
#!/bin/sh
printf '%s\n' "$@" > "$PRODUCTBUILD_ARGUMENTS"
EOF
chmod +x "$TEST_ROOT/bin/productbuild"
export PATH="$TEST_ROOT/bin:$PATH"
export PRODUCTBUILD_ARGUMENTS="$TEST_ROOT/arguments"

assemble() {
    sh "$REPOSITORY_ROOT/etc/assemble-macos-pkg.sh" \
        "$TEST_ROOT/components" "$TEST_ROOT/exordos-macos.pkg"
}

if assemble; then
    echo "Missing components unexpectedly succeeded" >&2
    exit 1
fi
[ ! -e "$PRODUCTBUILD_ARGUMENTS" ]

for ARCH in arm64 x86_64; do
    : > "$TEST_ROOT/components/macos-$ARCH.pkg"
    printf '%s\n' 3.2.21 > "$TEST_ROOT/components/macos-$ARCH.pkg.version"
done
printf '%s\n' 3.2.22 > "$TEST_ROOT/components/macos-x86_64.pkg.version"
if assemble; then
    echo "Mismatched versions unexpectedly succeeded" >&2
    exit 1
fi
[ ! -e "$PRODUCTBUILD_ARGUMENTS" ]

printf '%s\n' 3.2.21 > "$TEST_ROOT/components/macos-x86_64.pkg.version"
assemble
grep -Fx -- "$REPOSITORY_ROOT/etc/macos-distribution.xml" "$PRODUCTBUILD_ARGUMENTS"
! grep -Fx -- --sign "$PRODUCTBUILD_ARGUMENTS"

MACOS_INSTALLER_IDENTITY='Developer ID Installer: Test (TEAM)' assemble
grep -Fx -- --sign "$PRODUCTBUILD_ARGUMENTS"
grep -Fx -- 'Developer ID Installer: Test (TEAM)' "$PRODUCTBUILD_ARGUMENTS"
grep -Fx -- --timestamp "$PRODUCTBUILD_ARGUMENTS"

echo "macOS package assembly tests passed"
