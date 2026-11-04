#!/bin/sh
#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")
# Run inside a disposable Linux container as root.

set -eu
umask 022
: "${EXORDOS_REPO_URL:?EXORDOS_REPO_URL must point to the test release repository}"
[ "$(id -u)" -eq 0 ] || exit 1
REPOSITORY_ROOT=$(CDPATH='' cd -- "$(dirname "$0")/../.." && pwd)
TEST_ROOT=$(mktemp -d /tmp/exordos-root-test.XXXXXX)
trap 'rm -rf "$TEST_ROOT"' EXIT
chmod 0755 "$TEST_ROOT"
VERSION=$(curl -fsSL "$EXORDOS_REPO_URL/latest/VERSION")
case "$VERSION" in
    ''|*[!0-9A-Za-z.+-]*|*..*) exit 1 ;;
esac
mkdir -p "$TEST_ROOT/repo/latest" "$TEST_ROOT/repo/$VERSION"
printf '%s\n' "$VERSION" > "$TEST_ROOT/repo/latest/VERSION"
ARTIFACT="exordos-linux-$(uname -m).tar.xz"
for FILE in "$ARTIFACT" "$ARTIFACT.sha256"; do
    curl -fsSL "$EXORDOS_REPO_URL/$VERSION/$FILE" -o "$TEST_ROOT/repo/$VERSION/$FILE"
done
cp "$REPOSITORY_ROOT/etc/install.sh" "$TEST_ROOT/install.sh"
export EXORDOS_REPO_URL="file://$TEST_ROOT/repo"
TEST_USER=exordos-installer-test
useradd -m "$TEST_USER"
printf '%s ALL=(ALL) NOPASSWD: ALL\n' "$TEST_USER" > "/etc/sudoers.d/$TEST_USER"
chmod 0440 "/etc/sudoers.d/$TEST_USER"

# A read-only system launcher must allow an ordinary user's default install.
printf '#!/bin/sh\necho system-version\n' > /usr/bin/exordos
chmod 0755 /usr/bin/exordos
sudo -u "$TEST_USER" env -u EXORDOS_INSTALL_PREFIX HOME="/home/$TEST_USER" \
    EXORDOS_REPO_URL="$EXORDOS_REPO_URL" sh "$TEST_ROOT/install.sh"
[ "$("/home/$TEST_USER/.local/bin/exordos" --silent --no-check-updates version)" = "$VERSION" ]
[ "$(/usr/bin/exordos)" = system-version ]

sudo -u "$TEST_USER" env EXORDOS_INSTALL_PREFIX=/usr/local \
    EXORDOS_REPO_URL="$EXORDOS_REPO_URL" sh "$TEST_ROOT/install.sh"
TARGET_DIR="/usr/local/lib/exordos/versions/$VERSION"
TARGET_BINARY="$TARGET_DIR/exordos"
[ "$(stat -c %u "$TARGET_BINARY")" -eq 0 ]
[ -z "$(find "$TARGET_DIR" ! -type l \( ! -user root -o -perm /022 \) -print -quit)" ]
if sudo -u "$TEST_USER" test -w "$TARGET_BINARY"; then
    echo "The installing user can modify the privileged payload" >&2
    exit 1
fi
EXORDOS_INSTALL_PREFIX=/usr/local sh "$TEST_ROOT/install.sh"

# Root must reject a payload whose ownership was changed after installation.
MARKER=$(mktemp)
rm "$MARKER"
chown "$TEST_USER" "$TARGET_BINARY"
printf '#!/bin/sh\ntouch "%s"\necho "%s"\n' "$MARKER" "$VERSION" > "$TARGET_BINARY"
if EXORDOS_INSTALL_PREFIX=/usr/local sh "$TEST_ROOT/install.sh"; then
    echo "Root accepted a user-owned cached executable" >&2
    exit 1
fi
[ ! -e "$MARKER" ] || {
    echo "Root executed a user-owned cached executable" >&2
    exit 1
}
echo "Privileged Linux installer tests passed"
