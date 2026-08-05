#!/bin/sh
#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

set -eu

REPOSITORY_ROOT=$(CDPATH='' cd -- "$(dirname "$0")/../.." && pwd)
TEST_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/exordos-installer-test.XXXXXX")

cleanup() {
    case "$TEST_ROOT" in
        */exordos-installer-test.*) rm -rf "$TEST_ROOT" ;;
    esac
}
trap cleanup EXIT

fail() {
    echo "FAIL: $*" >&2
    exit 1
}

FAKE_BIN="$TEST_ROOT/bin"
FAKE_REPO="$TEST_ROOT/repo"
PREFIX="$TEST_ROOT/prefix"
mkdir -p "$FAKE_BIN" "$FAKE_REPO/latest" "$TEST_ROOT/home"

cat > "$FAKE_BIN/uname" <<'EOF'
#!/bin/sh
case "$1" in
    -s) printf '%s\n' Darwin ;;
    -m) printf '%s\n' "${FAKE_ARCH:-arm64}" ;;
    *) exit 2 ;;
esac
EOF

cat > "$FAKE_BIN/ditto" <<'EOF'
#!/bin/sh
if [ "$1" = "-x" ] && [ "$2" = "-k" ]; then
    SOURCE=$3
    DESTINATION=$4
elif [ "$#" -eq 2 ]; then
    SOURCE=$1
    DESTINATION=$2
else
    exit 2
fi
python3 - "$SOURCE" "$DESTINATION" <<'PY'
import pathlib
import shutil
import sys
import zipfile

source = pathlib.Path(sys.argv[1])
destination = pathlib.Path(sys.argv[2])
if source.is_dir():
    shutil.copytree(source, destination, symlinks=True)
else:
    with zipfile.ZipFile(source) as zip_file:
        zip_file.extractall(destination)
PY
EOF

cat > "$FAKE_BIN/codesign" <<'EOF'
#!/bin/sh
case " $* " in
    *' -dvvv '*)
        if [ "${FAKE_SIGNATURE_MODE:-developer}" = "adhoc" ]; then
            echo 'Signature=adhoc' >&2
            echo 'TeamIdentifier=not set' >&2
        else
            echo 'Authority=Developer ID Application: Exordos Test (TESTTEAM)' >&2
            echo 'TeamIdentifier=TESTTEAM' >&2
        fi
        ;;
esac
exit 0
EOF

cat > "$FAKE_BIN/file" <<'EOF'
#!/bin/sh
case "$1" in
    */exordos) echo "$1: Mach-O 64-bit executable" ;;
    *) /usr/bin/file "$@" ;;
esac
EOF

chmod +x \
    "$FAKE_BIN/uname" \
    "$FAKE_BIN/ditto" \
    "$FAKE_BIN/codesign" \
    "$FAKE_BIN/file"

create_release() {
    VERSION=$1
    ARCH=$2
    RELEASE_DIR="$FAKE_REPO/$VERSION"
    FIXTURE_DIR="$TEST_ROOT/fixture-$VERSION-$ARCH"
    ARCHIVE="$RELEASE_DIR/exordos-macos-$ARCH.zip"
    mkdir -p "$RELEASE_DIR" "$FIXTURE_DIR/exordos/_internal"
    printf '#!/bin/sh\nprintf "%%s\\n" "%s"\n' "$VERSION" \
        > "$FIXTURE_DIR/exordos/exordos"
    printf '%s\n' runtime > "$FIXTURE_DIR/exordos/_internal/marker"
    chmod +x "$FIXTURE_DIR/exordos/exordos"
    python3 - "$FIXTURE_DIR" "$ARCHIVE" <<'PY'
import pathlib
import sys
import zipfile

source = pathlib.Path(sys.argv[1])
archive = pathlib.Path(sys.argv[2])
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zip_file:
    for path in source.rglob("*"):
        if path.is_file():
            zip_file.write(path, path.relative_to(source))
PY
    HASH=$(shasum -a 256 "$ARCHIVE")
    HASH=${HASH%% *}
    printf '%s\n' "$HASH" > "$ARCHIVE.sha256"
}

install_version() {
    env \
        PATH="$FAKE_BIN:$PATH" \
        HOME="$TEST_ROOT/home" \
        EXORDOS_INSTALL_PREFIX="$PREFIX" \
        EXORDOS_REPO_URL="file://$FAKE_REPO" \
        FAKE_ARCH="${FAKE_ARCH:-arm64}" \
        FAKE_SIGNATURE_MODE="${FAKE_SIGNATURE_MODE:-developer}" \
        ${EXORDOS_VERSION_OVERRIDE:+EXORDOS_VERSION=$EXORDOS_VERSION_OVERRIDE} \
        sh "$REPOSITORY_ROOT/etc/install.sh"
}

assert_active_version() {
    EXPECTED=$1
    [ -L "$PREFIX/bin/exordos" ] || fail "launcher is not a symlink"
    ACTUAL=$("$PREFIX/bin/exordos" --silent --no-check-updates version)
    [ "$ACTUAL" = "$EXPECTED" ] || \
        fail "active version is $ACTUAL, expected $EXPECTED"
}

create_release 3.1.14 arm64
printf '%s\n' 3.1.14 > "$FAKE_REPO/latest/VERSION"

# Preserve an existing one-file installation before activating the bundle.
mkdir -p "$PREFIX/bin"
printf '#!/bin/sh\nprintf "%%s\\n" "legacy"\n' > "$PREFIX/bin/exordos"
chmod +x "$PREFIX/bin/exordos"
LEGACY_HASH=$(shasum -a 256 "$PREFIX/bin/exordos")
LEGACY_HASH=${LEGACY_HASH%% *}
install_version
assert_active_version 3.1.14
[ -f "$PREFIX/lib/exordos/versions/3.1.14/.complete" ] || \
    fail "completion marker is missing"
[ -x "$PREFIX/lib/exordos/legacy/exordos-onefile-$LEGACY_HASH" ] || \
    fail "legacy one-file binary was not preserved"

# Reinstalling an immutable version must reuse the existing directory.
FIRST_MARKER=$(stat -c %i "$PREFIX/lib/exordos/versions/3.1.14/.complete")
install_version
SECOND_MARKER=$(stat -c %i "$PREFIX/lib/exordos/versions/3.1.14/.complete")
[ "$FIRST_MARKER" = "$SECOND_MARKER" ] || fail "reinstall replaced the version"

create_release 3.1.15 arm64
printf '%s\n' 3.1.15 > "$FAKE_REPO/latest/VERSION"
install_version
assert_active_version 3.1.15
[ -x "$PREFIX/lib/exordos/versions/3.1.14/exordos" ] || \
    fail "previous version was removed"

# Explicit rollback reuses an installed version without downloading it again.
EXORDOS_VERSION_OVERRIDE=3.1.14 install_version
assert_active_version 3.1.14
unset EXORDOS_VERSION_OVERRIDE

# A checksum failure must not switch the active launcher.
create_release 3.1.16 arm64
printf '%064d\n' 0 > "$FAKE_REPO/3.1.16/exordos-macos-arm64.zip.sha256"
printf '%s\n' 3.1.16 > "$FAKE_REPO/latest/VERSION"
if install_version; then
    fail "checksum mismatch unexpectedly succeeded"
fi
assert_active_version 3.1.14

# Ad-hoc signatures are rejected before the downloaded launcher is executed.
create_release 3.1.17 arm64
printf '%s\n' 3.1.17 > "$FAKE_REPO/latest/VERSION"
if FAKE_SIGNATURE_MODE=adhoc install_version; then
    fail "ad-hoc signature unexpectedly succeeded"
fi
assert_active_version 3.1.14

# Intel uses its own artifact.
create_release 3.1.14 x86_64
INTEL_PREFIX="$TEST_ROOT/intel-prefix"
PREFIX="$INTEL_PREFIX" FAKE_ARCH=x86_64 EXORDOS_VERSION_OVERRIDE=3.1.14 \
    install_version
PREFIX="$INTEL_PREFIX" assert_active_version 3.1.14

# Unsupported architectures fail before mutating the prefix.
UNKNOWN_PREFIX="$TEST_ROOT/unknown-prefix"
if PREFIX="$UNKNOWN_PREFIX" FAKE_ARCH=ppc64 install_version; then
    fail "unsupported architecture unexpectedly succeeded"
fi
[ ! -e "$UNKNOWN_PREFIX/bin/exordos" ] || \
    fail "unsupported architecture mutated the install prefix"

echo "macOS installer tests passed"
