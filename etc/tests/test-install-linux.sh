#!/bin/sh
#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

set -eu

REPOSITORY_ROOT=$(CDPATH='' cd -- "$(dirname "$0")/../.." && pwd)
TEST_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/exordos-linux-test.XXXXXX")
LOCK_PID=''
cleanup() {
    if [ -n "$LOCK_PID" ]; then
        kill "$LOCK_PID" 2>/dev/null || :
        wait "$LOCK_PID" 2>/dev/null || :
    fi
    rm -rf "$TEST_ROOT"
}
trap cleanup EXIT
FAKE_BIN="$TEST_ROOT/bin"
FAKE_REPO="$TEST_ROOT/repo"
PREFIX="$TEST_ROOT/install 'prefix"
mkdir -p "$FAKE_BIN" "$FAKE_REPO/latest" "$TEST_ROOT/home"

fail() { echo "FAIL: $*" >&2; exit 1; }

cat > "$FAKE_BIN/uname" <<'EOF'
#!/bin/sh
case "$1" in
    -s) echo Linux ;;
    -m) echo "${FAKE_ARCH:-x86_64}" ;;
    -r) echo 7.0 ;;
    *) exit 2 ;;
esac
EOF
cat > "$FAKE_BIN/getconf" <<'EOF'
#!/bin/sh
echo "${FAKE_GLIBC:-glibc 2.28}"
EOF
cat > "$FAKE_BIN/id" <<'EOF'
#!/bin/sh
if [ "$1" = -u ]; then echo "${FAKE_UID:-1000}"; else /usr/bin/id "$@"; fi
EOF
cat > "$FAKE_BIN/stat" <<'EOF'
#!/bin/sh
if [ "${FAKE_UID:-1000}" = 0 ] && [ "$1" = -c ] && [ "$2" = %u ]; then
    echo 0
else
    /usr/bin/stat "$@"
fi
EOF
printf '#!/bin/sh\necho unrelated\n' > "$FAKE_BIN/exordos"
chmod +x "$FAKE_BIN/uname" "$FAKE_BIN/getconf" "$FAKE_BIN/id" "$FAKE_BIN/stat" "$FAKE_BIN/exordos"
cat > "$FAKE_BIN/mkdir" <<'EOF'
#!/bin/sh
if [ -n "${FAKE_PROTECTED_PREFIX:-}" ]; then
    for ARG in "$@"; do
        case "$ARG" in
            "$FAKE_PROTECTED_PREFIX"|"$FAKE_PROTECTED_PREFIX"/*) exit 1 ;;
        esac
    done
fi
exec /usr/bin/mkdir "$@"
EOF
chmod +x "$FAKE_BIN/mkdir"

create_release() {
    VERSION=$1
    ARCH=$2
    FIXTURE="$TEST_ROOT/fixture-$VERSION-$ARCH"
    ARCHIVE="$FAKE_REPO/$VERSION/exordos-linux-$ARCH.tar.xz"
    mkdir -p "$FAKE_REPO/$VERSION" "$FIXTURE/exordos/_internal"
    printf '#!/bin/sh\nprintf "%%s\\n" "%s"\n' "$VERSION" > "$FIXTURE/exordos/exordos"
    chmod +x "$FIXTURE/exordos/exordos"
    echo runtime > "$FIXTURE/exordos/_internal/marker"
    sh "$REPOSITORY_ROOT/etc/package-linux.sh" "$FIXTURE/exordos" "$ARCHIVE"
}

rehash() {
    HASH=$(sha256sum "$ARCHIVE")
    printf '%s\n' "${HASH%% *}" > "$ARCHIVE.sha256"
}

install_version() {
    env PATH="$FAKE_BIN:$PATH" HOME="$TEST_ROOT/home" \
        EXORDOS_INSTALL_PREFIX="$PREFIX" EXORDOS_REPO_URL="file://$FAKE_REPO" \
        FAKE_ARCH="${FAKE_ARCH:-x86_64}" FAKE_GLIBC="${FAKE_GLIBC:-glibc 2.28}" \
        FAKE_UID="${FAKE_UID:-1000}" \
        ${EXORDOS_VERSION_OVERRIDE:+EXORDOS_VERSION=$EXORDOS_VERSION_OVERRIDE} \
        sh "$REPOSITORY_ROOT/etc/install.sh"
}

assert_active_version() {
    [ -f "$PREFIX/bin/exordos" ] && [ ! -L "$PREFIX/bin/exordos" ] || fail "launcher is not a regular file"
    ACTUAL=$("$PREFIX/bin/exordos" --silent --no-check-updates version)
    [ "$ACTUAL" = "$1" ] || fail "active version is $ACTUAL, expected $1"
}

create_release 3.2.1 x86_64
echo 3.2.1 > "$FAKE_REPO/latest/VERSION"
mkdir -p "$PREFIX/bin"
printf '#!/bin/sh\necho legacy\n' > "$PREFIX/bin/exordos"
chmod +x "$PREFIX/bin/exordos"
LEGACY_HASH=$(sha256sum "$PREFIX/bin/exordos")
LEGACY_HASH=${LEGACY_HASH%% *}
install_version
assert_active_version 3.2.1
[ -x "$PREFIX/lib/exordos/legacy/exordos-onefile-$LEGACY_HASH" ] || fail "missing legacy backup"
FIRST_MARKER=$(stat -c %i "$PREFIX/lib/exordos/versions/3.2.1/.complete")
install_version
[ "$FIRST_MARKER" = "$(stat -c %i "$PREFIX/lib/exordos/versions/3.2.1/.complete")" ] || \
    fail "reinstall replaced the immutable version"

create_release 3.2.2 x86_64
echo 3.2.2 > "$FAKE_REPO/latest/VERSION"
install_version
assert_active_version 3.2.2
EXORDOS_VERSION_OVERRIDE=3.2.1 install_version
assert_active_version 3.2.1

# Direct writes by a legacy installer must not corrupt the cached version.
CACHED_HASH=$(sha256sum "$PREFIX/lib/exordos/versions/3.2.1/exordos")
printf '#!/bin/sh\necho legacy-update\n' > "$PREFIX/bin/exordos"
[ "$CACHED_HASH" = "$(sha256sum "$PREFIX/lib/exordos/versions/3.2.1/exordos")" ] || \
    fail "legacy update modified a cached version"
EXORDOS_VERSION_OVERRIDE=3.2.1 install_version
assert_active_version 3.2.1

# A broken download or runtime must preserve the active installation.
create_release 3.2.3 x86_64
echo 3.2.3 > "$FAKE_REPO/latest/VERSION"
printf '%064d\n' 0 > "$ARCHIVE.sha256"
if install_version; then fail "checksum mismatch succeeded"; fi
assert_active_version 3.2.1
rehash
printf '#!/bin/sh\nexit 42\n' > "$FIXTURE/exordos/exordos"
tar -cJf "$ARCHIVE" -C "$FIXTURE" exordos
rehash
if install_version; then fail "unrunnable bundle succeeded"; fi
assert_active_version 3.2.1

# Checksummed archives still require a matching version and safe paths.
printf '#!/bin/sh\necho 9.9.9\n' > "$FIXTURE/exordos/exordos"
tar -cJf "$ARCHIVE" -C "$FIXTURE" exordos
rehash
if install_version; then fail "wrong bundle version succeeded"; fi
ln -s /tmp "$FIXTURE/exordos/_internal/unsafe"
tar -cJf "$ARCHIVE" -C "$FIXTURE" exordos
rehash
if install_version; then fail "escaping symlink succeeded"; fi
rm "$FIXTURE/exordos/_internal/unsafe"
echo unexpected > "$FIXTURE/outside"
tar -cJf "$ARCHIVE" -C "$FIXTURE" exordos outside
rehash
if install_version; then fail "unexpected archive entry succeeded"; fi
assert_active_version 3.2.1

# Stale locks and a public directory lock cannot block atomic publication.
create_release 3.2.4 x86_64
echo 3.2.4 > "$FAKE_REPO/latest/VERSION"
mkdir "$PREFIX/lib/exordos/versions/.exordos-install.3.2.4.lock"
mkdir "$PREFIX/lib/exordos/versions/.exordos-install.3.2.4.abandoned"
python3 - "$PREFIX/lib/exordos/versions" "$TEST_ROOT/locked" <<'PY' &
import fcntl
import os
from pathlib import Path
import sys
import time

fd = os.open(sys.argv[1], os.O_RDONLY)
fcntl.flock(fd, fcntl.LOCK_EX)
Path(sys.argv[2]).touch()
time.sleep(30)
PY
LOCK_PID=$!
while [ ! -f "$TEST_ROOT/locked" ]; do sleep 0.01; done
install_version > "$TEST_ROOT/concurrent-1.log" 2>&1 &
FIRST_PID=$!
install_version > "$TEST_ROOT/concurrent-2.log" 2>&1 &
SECOND_PID=$!
FIRST_STATUS=0
SECOND_STATUS=0
wait "$FIRST_PID" || FIRST_STATUS=$?
wait "$SECOND_PID" || SECOND_STATUS=$?
[ "$FIRST_STATUS" -eq 0 ] || [ "$SECOND_STATUS" -eq 0 ] || fail "both publishers failed"
assert_active_version 3.2.4
kill -KILL "$LOCK_PID"
wait "$LOCK_PID" 2>/dev/null || :
LOCK_PID=''
install_version
assert_active_version 3.2.4

# ARM64 selects its own artifact; platform failures do not mutate the prefix.
create_release 3.2.1 aarch64
ARM_PREFIX="$TEST_ROOT/arm"
PREFIX="$ARM_PREFIX" FAKE_ARCH=aarch64 EXORDOS_VERSION_OVERRIDE=3.2.1 install_version
PREFIX="$ARM_PREFIX" assert_active_version 3.2.1
UNKNOWN_PREFIX="$TEST_ROOT/unsupported"
if PREFIX="$UNKNOWN_PREFIX" FAKE_ARCH=ppc64 install_version; then fail "unsupported architecture succeeded"; fi
if PREFIX="$UNKNOWN_PREFIX" FAKE_GLIBC='glibc 2.27' install_version; then fail "old glibc succeeded"; fi
if PREFIX="$UNKNOWN_PREFIX" FAKE_GLIBC=musl install_version; then fail "musl succeeded"; fi
[ ! -e "$UNKNOWN_PREFIX" ] || fail "unsupported platform mutated the prefix"
if EXORDOS_VERSION_OVERRIDE='../outside' install_version; then fail "invalid version succeeded"; fi

# Default installs preserve an existing user launcher and support a fresh HOME.
rm "$FAKE_BIN/exordos"
USER_HOME="$TEST_ROOT/user-home"
mkdir -p "$USER_HOME/bin"
printf '#!/bin/sh\necho legacy\n' > "$USER_HOME/bin/exordos"
chmod +x "$USER_HOME/bin/exordos"
env PATH="$FAKE_BIN:/usr/bin:/bin" HOME="$USER_HOME" \
    EXORDOS_REPO_URL="file://$FAKE_REPO" EXORDOS_VERSION=3.2.1 \
    sh "$REPOSITORY_ROOT/etc/install.sh"
PREFIX="$USER_HOME" assert_active_version 3.2.1
USER_HOME="$TEST_ROOT/fresh-home"
env PATH="$FAKE_BIN:/usr/bin:/bin" HOME="$USER_HOME" \
    EXORDOS_REPO_URL="file://$FAKE_REPO" EXORDOS_VERSION=3.2.1 \
    sh "$REPOSITORY_ROOT/etc/install.sh"
PREFIX="$USER_HOME/.local" assert_active_version 3.2.1

# Preserve an existing launcher in a custom directory on PATH.
CUSTOM_BIN="$TEST_ROOT/custom/tools"
mkdir -p "$CUSTOM_BIN"
printf '#!/bin/sh\necho legacy\n' > "$CUSTOM_BIN/exordos"
chmod +x "$CUSTOM_BIN/exordos"
env PATH="$CUSTOM_BIN:$FAKE_BIN:/usr/bin:/bin" HOME="$TEST_ROOT/home" \
    EXORDOS_REPO_URL="file://$FAKE_REPO" EXORDOS_VERSION=3.2.1 \
    sh "$REPOSITORY_ROOT/etc/install.sh"
[ "$("$CUSTOM_BIN/exordos" version)" = 3.2.1 ] || fail "custom launcher was not updated"
[ -f "$CUSTOM_BIN/lib/exordos/versions/3.2.1/.complete" ] || fail "custom bundle is missing"

# An unwritable system launcher must not prevent a user installation.
SYSTEM_PREFIX="$TEST_ROOT/system/usr"
mkdir -p "$SYSTEM_PREFIX/bin"
printf '#!/bin/sh\necho system-version\n' > "$SYSTEM_PREFIX/bin/exordos"
chmod +x "$SYSTEM_PREFIX/bin/exordos"
SYSTEM_HASH=$(sha256sum "$SYSTEM_PREFIX/bin/exordos")
chmod 0555 "$SYSTEM_PREFIX/bin" "$SYSTEM_PREFIX"
FALLBACK_HOME="$TEST_ROOT/fallback-home"
env PATH="$SYSTEM_PREFIX/bin:$FAKE_BIN:/usr/bin:/bin" HOME="$FALLBACK_HOME" \
    FAKE_PROTECTED_PREFIX="$SYSTEM_PREFIX" EXORDOS_REPO_URL="file://$FAKE_REPO" \
    EXORDOS_VERSION=3.2.1 sh "$REPOSITORY_ROOT/etc/install.sh"
PREFIX="$FALLBACK_HOME/.local" assert_active_version 3.2.1
[ "$SYSTEM_HASH" = "$(sha256sum "$SYSTEM_PREFIX/bin/exordos")" ] || fail "system launcher was changed"
if env PATH="$SYSTEM_PREFIX/bin:$FAKE_BIN:/usr/bin:/bin" HOME="$FALLBACK_HOME" \
    FAKE_PROTECTED_PREFIX="$SYSTEM_PREFIX" EXORDOS_INSTALL_PREFIX="$SYSTEM_PREFIX" \
    EXORDOS_REPO_URL="file://$FAKE_REPO" EXORDOS_VERSION=3.2.1 \
    sh "$REPOSITORY_ROOT/etc/install.sh"; then
    fail "an explicit unwritable prefix silently fell back"
fi
chmod 0755 "$SYSTEM_PREFIX" "$SYSTEM_PREFIX/bin"

# Root must reject a writable cached payload before executing its version check.
find "$PREFIX" -type d -exec chmod go-w {} +
CACHED_BINARY="$PREFIX/lib/exordos/versions/3.2.1/exordos"
printf '#!/bin/sh\ntouch "%s"\necho 3.2.1\n' "$TEST_ROOT/executed" > "$CACHED_BINARY"
chmod 0777 "$CACHED_BINARY"
if FAKE_UID=0 EXORDOS_VERSION_OVERRIDE=3.2.1 install_version; then
    fail "root accepted an untrusted cached payload"
fi
[ ! -e "$TEST_ROOT/executed" ] || fail "root executed an untrusted cached payload"

echo "Linux installer tests passed"
