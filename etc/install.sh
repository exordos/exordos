#!/bin/sh
# This script installs exordos on Linux and macOS.
# It detects the current operating system architecture and installs the appropriate version of exordos.

# Wrap script in main function so that a truncated partial download doesn't end
# up executing half a script.
main() {

set -eu

red="$( (/usr/bin/tput bold || :; /usr/bin/tput setaf 1 || :) 2>&-)"
plain="$( (/usr/bin/tput sgr0 || :) 2>&-)"

status() { echo ">>> $*" >&2; }
error() { echo "${red}ERROR:${plain} $*"; exit 1; }
warning() { echo "${red}WARNING:${plain} $*"; }

TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/exordos-install.XXXXXX")
INSTALL_STAGE=''
INSTALL_LOCK=''
NEED_SUDO=0
cleanup() {
    if [ -n "$INSTALL_STAGE" ]; then
        case "$INSTALL_STAGE" in
            */.exordos-install.*)
                if [ "$NEED_SUDO" -eq 1 ]; then
                    sudo -n rm -rf "$INSTALL_STAGE" 2>/dev/null || :
                else
                    rm -rf "$INSTALL_STAGE" 2>/dev/null || :
                fi
                ;;
        esac
    fi
    if [ -n "$INSTALL_LOCK" ]; then
        case "$INSTALL_LOCK" in
            */.exordos-install.*.lock)
                if [ "$NEED_SUDO" -eq 1 ]; then
                    sudo -n rmdir "$INSTALL_LOCK" 2>/dev/null || :
                else
                    rmdir "$INSTALL_LOCK" 2>/dev/null || :
                fi
                ;;
        esac
    fi
    case "$TEMP_DIR" in
        */exordos-install.*)
            rm -rf "$TEMP_DIR"
            ;;
    esac
}
trap cleanup EXIT

available() { command -v "$1" >/dev/null; }
require() {
    local MISSING=''
    for TOOL in "$@"; do
        if ! available "$TOOL"; then
            MISSING="$MISSING $TOOL"
        fi
    done

    echo "$MISSING"
}

privileged() {
    if [ "$NEED_SUDO" -eq 1 ]; then
        sudo "$@"
    else
        "$@"
    fi
}

OS="$(uname -s)"
ARCH=$(uname -m)
case "$ARCH" in
    x86_64) ARCH="amd64" ;;
    aarch64|arm64) ARCH="arm64" ;;
    *) error "Unsupported architecture: $ARCH" ;;
esac

###########################################
# macOS
###########################################

if [ "$OS" = "Darwin" ]; then
    NEEDS=$(require awk codesign curl ditto file find grep shasum)
    if [ -n "$NEEDS" ]; then
        status "ERROR: The following tools are required but missing:"
        for NEED in $NEEDS; do
            echo "  - $NEED"
        done
        exit 1
    fi

    INSTALL_PREFIX="${EXORDOS_INSTALL_PREFIX:-/usr/local}"
    REPO_URL="${EXORDOS_REPO_URL:-https://repo.exordos.com/exordos}"
    case "$INSTALL_PREFIX" in
        /|//*|*//*|*/./*|*/.|*/../*|*/..)
            error "EXORDOS_INSTALL_PREFIX must be a canonical path below /"
            ;;
        /*) ;;
        *) error "EXORDOS_INSTALL_PREFIX must be an absolute directory" ;;
    esac
    INSTALL_ROOT="$INSTALL_PREFIX/lib/exordos"
    VERSIONS_DIR="$INSTALL_ROOT/versions"
    BINDIR="$INSTALL_PREFIX/bin"

    MACHINE_ARCH=$(uname -m)
    if [ "$MACHINE_ARCH" = "x86_64" ] && \
        [ -x /usr/sbin/sysctl ] && \
        [ "$(/usr/sbin/sysctl -in sysctl.proc_translated 2>/dev/null || :)" = "1" ]; then
        MACHINE_ARCH="arm64"
    fi
    case "$MACHINE_ARCH" in
        arm64) MACOS_ARCH="arm64" ;;
        x86_64) MACOS_ARCH="x86_64" ;;
        *) error "Unsupported macOS architecture: $MACHINE_ARCH" ;;
    esac

    VERSION="${EXORDOS_VERSION:-}"
    if [ -z "$VERSION" ]; then
        status "Resolving the latest exordos version..."
        curl --fail --show-error --location --silent \
            "$REPO_URL/latest/VERSION" --output "$TEMP_DIR/VERSION"
        VERSION=$(cat "$TEMP_DIR/VERSION")
    fi
    case "$VERSION" in
        [0-9]*) ;;
        *) error "Invalid exordos version: $VERSION" ;;
    esac
    case "$VERSION" in
        *[!0-9A-Za-z.+-]*|*..*) error "Invalid exordos version: $VERSION" ;;
    esac

    if ! mkdir -p "$VERSIONS_DIR" "$BINDIR" 2>/dev/null || \
        [ ! -w "$VERSIONS_DIR" ] || [ ! -w "$BINDIR" ]; then
        [ "$INSTALL_PREFIX" = "/usr/local" ] || \
            error "A custom EXORDOS_INSTALL_PREFIX must be writable without sudo"
        available sudo || error "sudo is required to install exordos to $INSTALL_PREFIX"
        status "Administrator access is required to install exordos to $INSTALL_PREFIX."
        sudo -v
        NEED_SUDO=1
        privileged mkdir -p "$VERSIONS_DIR" "$BINDIR"
    fi

    TARGET_DIR="$VERSIONS_DIR/$VERSION"
    TARGET_BINARY="$TARGET_DIR/exordos"
    if [ -e "$TARGET_DIR" ] || [ -L "$TARGET_DIR" ]; then
        [ -d "$TARGET_DIR" ] && [ ! -L "$TARGET_DIR" ] || \
            error "Installed version path is not a directory: $TARGET_DIR"
        [ -f "$TARGET_DIR/.complete" ] && [ -x "$TARGET_BINARY" ] || \
            error "Installed version is incomplete: $TARGET_DIR"
        INSTALLED_VERSION=$("$TARGET_BINARY" --silent --no-check-updates version)
        [ "$INSTALLED_VERSION" = "$VERSION" ] || \
            error "Installed version at $TARGET_DIR is corrupt"
        status "Using the existing exordos $VERSION installation."
    else
        ARTIFACT="exordos-macos-$MACOS_ARCH.zip"
        RELEASE_URL="$REPO_URL/$VERSION"
        ARCHIVE="$TEMP_DIR/$ARTIFACT"
        CHECKSUM_FILE="$ARCHIVE.sha256"

        status "Downloading exordos $VERSION for macOS $MACOS_ARCH..."
        curl --fail --show-error --location --progress-bar \
            "$RELEASE_URL/$ARTIFACT" --output "$ARCHIVE"
        curl --fail --show-error --location --silent \
            "$RELEASE_URL/$ARTIFACT.sha256" --output "$CHECKSUM_FILE"

        EXPECTED_HASH=$(tr 'A-F' 'a-f' < "$CHECKSUM_FILE")
        case "$EXPECTED_HASH" in
            *[!0-9a-f]*)
                error "Invalid SHA-256 checksum for $ARTIFACT"
                ;;
        esac
        [ "${#EXPECTED_HASH}" -eq 64 ] || \
            error "Invalid SHA-256 checksum for $ARTIFACT"
        ACTUAL_HASH=$(shasum -a 256 "$ARCHIVE")
        ACTUAL_HASH=${ACTUAL_HASH%% *}
        [ "$ACTUAL_HASH" = "$EXPECTED_HASH" ] || \
            error "SHA-256 checksum mismatch for $ARTIFACT"

        UNPACKED="$TEMP_DIR/unpacked"
        mkdir -p "$UNPACKED"
        ditto -x -k "$ARCHIVE" "$UNPACKED"
        if find "$UNPACKED" -mindepth 1 -maxdepth 1 ! -name exordos | grep -q .; then
            error "Unexpected top-level entry in $ARTIFACT"
        fi
        [ -d "$UNPACKED/exordos" ] && [ ! -L "$UNPACKED/exordos" ] || \
            error "Invalid archive layout in $ARTIFACT"
        [ -d "$UNPACKED/exordos/_internal" ] && \
            [ ! -L "$UNPACKED/exordos/_internal" ] || \
            error "Missing runtime directory in $ARTIFACT"
        [ -f "$UNPACKED/exordos/exordos" ] && \
            [ ! -L "$UNPACKED/exordos/exordos" ] || \
            error "Missing launcher in $ARTIFACT"
        chmod +x "$UNPACKED/exordos/exordos"
        verify_macos_code() {
            CANDIDATE=$1
            shift
            codesign --verify --strict "$@" "$CANDIDATE"
            SIGNATURE=$(codesign -dvvv "$CANDIDATE" 2>&1)
            if printf '%s\n' "$SIGNATURE" | grep -q '^Signature=adhoc$'; then
                [ "${EXORDOS_INSTALL_ALLOW_ADHOC:-0}" = "1" ] || \
                    error "Ad-hoc signature found in $ARTIFACT"
            else
                printf '%s\n' "$SIGNATURE" | \
                    grep -q '^Authority=Developer ID Application:' || \
                    error "Unexpected signing authority in $ARTIFACT"
                CANDIDATE_TEAM=$(printf '%s\n' "$SIGNATURE" | \
                    awk -F= '/^TeamIdentifier=/ {print $2; exit}')
                [ -n "$CANDIDATE_TEAM" ] && \
                    [ "$CANDIDATE_TEAM" != "not set" ] || \
                    error "Missing TeamIdentifier in $ARTIFACT"
                if [ -z "$SIGNING_TEAM" ]; then
                    SIGNING_TEAM=$CANDIDATE_TEAM
                else
                    [ "$CANDIDATE_TEAM" = "$SIGNING_TEAM" ] || \
                        error "Mixed signing teams in $ARTIFACT"
                fi
            fi
            SIGNED_CODE_COUNT=$((SIGNED_CODE_COUNT + 1))
        }

        SIGNED_CODE_COUNT=0
        SIGNING_TEAM=''
        MACHO_LIST="$TEMP_DIR/macho-files"
        find "$UNPACKED/exordos" -type f > "$MACHO_LIST"
        while IFS= read -r CANDIDATE; do
            if file "$CANDIDATE" | grep -q 'Mach-O'; then
                case "$CANDIDATE" in
                    *.framework/*)
                        verify_macos_code "$CANDIDATE" --ignore-resources
                        ;;
                    *) verify_macos_code "$CANDIDATE" ;;
                esac
            fi
        done < "$MACHO_LIST"
        [ "$SIGNED_CODE_COUNT" -gt 0 ] || \
            error "No signed code found in $ARTIFACT"
        ARCHIVE_VERSION=$(
            "$UNPACKED/exordos/exordos" --silent --no-check-updates version
        )
        [ "$ARCHIVE_VERSION" = "$VERSION" ] || \
            error "Archive contains exordos $ARCHIVE_VERSION, expected $VERSION"
        printf '%s\n' "$ACTUAL_HASH" > "$UNPACKED/exordos/.archive-sha256"
        : > "$UNPACKED/exordos/.complete"

        INSTALL_LOCK="$VERSIONS_DIR/.exordos-install.$VERSION.lock"
        privileged mkdir "$INSTALL_LOCK" 2>/dev/null || \
            error "Another exordos $VERSION installation is in progress"
        [ ! -e "$TARGET_DIR" ] && [ ! -L "$TARGET_DIR" ] || \
            error "Another installer created $TARGET_DIR"

        INSTALL_STAGE="$VERSIONS_DIR/.exordos-install.$VERSION.$$"
        [ ! -e "$INSTALL_STAGE" ] && [ ! -L "$INSTALL_STAGE" ] || \
            error "Installation staging path already exists: $INSTALL_STAGE"
        privileged ditto "$UNPACKED/exordos" "$INSTALL_STAGE"
        STAGED_VERSION=$(
            "$INSTALL_STAGE/exordos" --silent --no-check-updates version
        )
        [ "$STAGED_VERSION" = "$VERSION" ] || \
            error "Staged exordos version validation failed"
        privileged mv -n "$INSTALL_STAGE" "$TARGET_DIR"
        [ ! -e "$INSTALL_STAGE" ] || \
            error "Another installer created $TARGET_DIR"
        INSTALL_STAGE=''
        privileged rmdir "$INSTALL_LOCK"
        INSTALL_LOCK=''
    fi

    if [ -e "$BINDIR/exordos" ] && [ ! -L "$BINDIR/exordos" ]; then
        [ -f "$BINDIR/exordos" ] || \
            error "$BINDIR/exordos is not a regular file or symlink"
        LEGACY_HASH=$(shasum -a 256 "$BINDIR/exordos")
        LEGACY_HASH=${LEGACY_HASH%% *}
        LEGACY_DIR="$INSTALL_ROOT/legacy"
        LEGACY_BINARY="$LEGACY_DIR/exordos-onefile-$LEGACY_HASH"
        privileged mkdir -p "$LEGACY_DIR"
        if [ ! -f "$LEGACY_BINARY" ]; then
            privileged cp -p "$BINDIR/exordos" "$LEGACY_BINARY"
        fi
        BACKUP_HASH=$(shasum -a 256 "$LEGACY_BINARY")
        BACKUP_HASH=${BACKUP_HASH%% *}
        [ "$BACKUP_HASH" = "$LEGACY_HASH" ] || \
            error "Failed to verify the legacy exordos backup"
        status "Preserved the previous one-file binary at $LEGACY_BINARY."
    fi

    LINK_STAGE="$BINDIR/.exordos-install.$$"
    [ ! -e "$LINK_STAGE" ] && [ ! -L "$LINK_STAGE" ] || \
        error "Launcher staging path already exists: $LINK_STAGE"
    privileged ln -s "$TARGET_BINARY" "$LINK_STAGE"
    privileged mv -f "$LINK_STAGE" "$BINDIR/exordos"

    ACTIVE_VERSION=$("$BINDIR/exordos" --silent --no-check-updates version)
    [ "$ACTIVE_VERSION" = "$VERSION" ] || \
        error "Installed exordos version validation failed"
    status "exordos $VERSION was successfully installed."
    exit 0
fi

###########################################
# Linux
###########################################

[ "$OS" = "Linux" ] || error 'This script is intended to run on Linux and macOS only.'

umask 022
KERN=$(uname -r)
case "$KERN" in
    *icrosoft*WSL2 | *icrosoft*wsl2) ;;
    *icrosoft) error "Microsoft WSL1 is not supported. Please use WSL2." ;;
esac

NEEDS=$(require awk chmod cp curl find getconf id install readlink sed sha256sum stat tar xz)
[ -z "$NEEDS" ] || error "Required tools are missing:$NEEDS"
GLIBC=$(getconf GNU_LIBC_VERSION 2>/dev/null || :)
case "$GLIBC" in
    'glibc '*) GLIBC_VERSION=${GLIBC#glibc } ;;
    *) error "exordos requires Linux with glibc 2.28 or newer" ;;
esac
awk -v version="$GLIBC_VERSION" 'BEGIN {
    split(version, parts, ".")
    exit !(parts[1] > 2 || (parts[1] == 2 && parts[2] >= 28))
}' || error "exordos requires glibc 2.28 or newer; found $GLIBC_VERSION"
case "$ARCH" in
    amd64) LINUX_ARCH=x86_64 ;;
    arm64) LINUX_ARCH=aarch64 ;;
esac

OLD_BINARY=$(command -v exordos || :)
if [ -z "$OLD_BINARY" ]; then
    for CANDIDATE in "$HOME/bin/exordos" "$HOME/.local/bin/exordos"; do
        if [ -x "$CANDIDATE" ]; then
            OLD_BINARY="$CANDIDATE"
            break
        fi
    done
fi
DEFAULT_PREFIX="$HOME/.local"
[ "$(id -u)" -ne 0 ] || DEFAULT_PREFIX=/usr/local
DEFAULT_BINDIR=''
case "$OLD_BINARY" in
    /*/exordos)
        DEFAULT_BINDIR=$(dirname "$OLD_BINARY")
        case "$DEFAULT_BINDIR" in
            */bin|*/sbin) DEFAULT_PREFIX=$(dirname "$DEFAULT_BINDIR") ;;
            *) DEFAULT_PREFIX="$DEFAULT_BINDIR" ;;
        esac
        ;;
esac
INSTALL_PREFIX="${EXORDOS_INSTALL_PREFIX:-$DEFAULT_PREFIX}"
case "$INSTALL_PREFIX" in
    /|//*|*//*|*/./*|*/.|*/../*|*/..)
        error "EXORDOS_INSTALL_PREFIX must be a canonical path below /" ;;
    /*) ;;
    *) error "EXORDOS_INSTALL_PREFIX must be an absolute directory" ;;
esac
INSTALL_ROOT="$INSTALL_PREFIX/lib/exordos"
VERSIONS_DIR="$INSTALL_ROOT/versions"
BINDIR="$INSTALL_PREFIX/bin"
if [ -z "${EXORDOS_INSTALL_PREFIX:-}" ] && [ -n "$DEFAULT_BINDIR" ]; then
    BINDIR="$DEFAULT_BINDIR"
elif [ "$INSTALL_PREFIX" = /usr/local ] && [ "$OLD_BINARY" = /usr/local/sbin/exordos ]; then
    BINDIR=/usr/local/sbin
fi
REPO_URL="${EXORDOS_REPO_URL:-https://repo.exordos.com/exordos}"
VERSION="${EXORDOS_VERSION:-}"
if [ -z "$VERSION" ]; then
    curl --fail --show-error --location --silent \
        "$REPO_URL/latest/VERSION" --output "$TEMP_DIR/VERSION"
    VERSION=$(cat "$TEMP_DIR/VERSION")
fi
case "$VERSION" in
    [0-9]*) ;;
    *) error "Invalid exordos version: $VERSION" ;;
esac
case "$VERSION" in
    *[!0-9A-Za-z.+-]*|*..*) error "Invalid exordos version: $VERSION" ;;
esac

if ! mkdir -p "$VERSIONS_DIR" "$BINDIR" 2>/dev/null || \
    [ ! -w "$VERSIONS_DIR" ] || [ ! -w "$BINDIR" ]; then
    if [ -z "${EXORDOS_INSTALL_PREFIX:-}" ] && [ "$(id -u)" -ne 0 ] && \
        [ "$INSTALL_PREFIX" != /usr/local ]; then
        INSTALL_PREFIX="$HOME/.local"
        INSTALL_ROOT="$INSTALL_PREFIX/lib/exordos"
        VERSIONS_DIR="$INSTALL_ROOT/versions"
        BINDIR="$INSTALL_PREFIX/bin"
        status "The existing launcher cannot be updated; installing to $BINDIR."
        mkdir -p "$VERSIONS_DIR" "$BINDIR"
        [ -w "$VERSIONS_DIR" ] && [ -w "$BINDIR" ] || error "User installation prefix is not writable"
    else
        [ "$INSTALL_PREFIX" = /usr/local ] || \
            error "EXORDOS_INSTALL_PREFIX must be writable without sudo"
        available sudo || error "sudo is required to install exordos to $INSTALL_PREFIX"
        sudo -v
        NEED_SUDO=1
        privileged mkdir -p "$VERSIONS_DIR" "$BINDIR"
    fi
fi

ROOT_INSTALL=0
if [ "$(id -u)" -eq 0 ] || [ "$NEED_SUDO" -eq 1 ]; then
    ROOT_INSTALL=1
    BINDIR=$(readlink -f "$BINDIR")
    INSTALL_ROOT=$(readlink -f "$INSTALL_ROOT")
    VERSIONS_DIR=$(readlink -f "$VERSIONS_DIR")
    for CHECK_DIR in "$BINDIR" "$INSTALL_ROOT" "$VERSIONS_DIR"; do
        while :; do
            [ "$(stat -c %u "$CHECK_DIR")" -eq 0 ] || \
                error "Root installation requires root-owned directories: $CHECK_DIR"
            MODE=$(stat -c %a "$CHECK_DIR")
            if [ "$((0$MODE & 0022))" -ne 0 ] && [ "$((0$MODE & 01000))" -eq 0 ]; then
                error "Root installation requires directories without group/other write access: $CHECK_DIR"
            fi
            [ "$CHECK_DIR" != / ] || break
            CHECK_DIR=$(dirname "$CHECK_DIR")
        done
    done
fi

TARGET_DIR="$VERSIONS_DIR/$VERSION"
TARGET_BINARY="$TARGET_DIR/exordos"
if [ -e "$TARGET_DIR" ] || [ -L "$TARGET_DIR" ]; then
    [ -d "$TARGET_DIR" ] && [ ! -L "$TARGET_DIR" ] && \
        [ -f "$TARGET_DIR/.complete" ] && [ -x "$TARGET_BINARY" ] && \
        [ ! -L "$TARGET_BINARY" ] || \
        error "Installed version is incomplete: $TARGET_DIR"
    if [ "$ROOT_INSTALL" -eq 1 ]; then
        UNTRUSTED=$(find "$TARGET_DIR" ! -type l \( ! -user root -o -perm /022 \) -print -quit)
        [ -z "$UNTRUSTED" ] || error "Root installation cannot execute an untrusted file: $UNTRUSTED"
    fi
    INSTALLED_VERSION=$("$TARGET_BINARY" --silent --no-check-updates version)
    [ "$INSTALLED_VERSION" = "$VERSION" ] || error "Installed version is corrupt"
else
    ARTIFACT="exordos-linux-$LINUX_ARCH.tar.xz"
    ARCHIVE="$TEMP_DIR/$ARTIFACT"
    status "Downloading exordos $VERSION for Linux $LINUX_ARCH..."
    curl --fail --show-error --location --progress-bar \
        "$REPO_URL/$VERSION/$ARTIFACT" --output "$ARCHIVE"
    curl --fail --show-error --location --silent \
        "$REPO_URL/$VERSION/$ARTIFACT.sha256" --output "$ARCHIVE.sha256"
    EXPECTED_HASH=$(tr 'A-F' 'a-f' < "$ARCHIVE.sha256")
    case "$EXPECTED_HASH" in
        *[!0-9a-f]*) error "Invalid SHA-256 checksum for $ARTIFACT" ;;
    esac
    [ "${#EXPECTED_HASH}" -eq 64 ] || error "Invalid SHA-256 checksum for $ARTIFACT"
    ACTUAL_HASH=$(sha256sum "$ARCHIVE")
    ACTUAL_HASH=${ACTUAL_HASH%% *}
    [ "$ACTUAL_HASH" = "$EXPECTED_HASH" ] || error "SHA-256 checksum mismatch for $ARTIFACT"

    tar -tJf "$ARCHIVE" > "$TEMP_DIR/entries"
    awk '
        $0 != "exordos" && $0 !~ /^exordos\// { exit 1 }
        /(^|\/)\.\.(\/|$)/ { exit 1 }
    ' "$TEMP_DIR/entries" || error "Invalid archive paths in $ARTIFACT"
    UNPACKED="$TEMP_DIR/unpacked"
    mkdir "$UNPACKED"
    tar -xJf "$ARCHIVE" --no-same-owner --no-same-permissions -C "$UNPACKED"
    [ -d "$UNPACKED/exordos" ] && [ ! -L "$UNPACKED/exordos" ] && \
        [ -d "$UNPACKED/exordos/_internal" ] && [ ! -L "$UNPACKED/exordos/_internal" ] && \
        [ -f "$UNPACKED/exordos/exordos" ] && [ ! -L "$UNPACKED/exordos/exordos" ] && \
        [ -x "$UNPACKED/exordos/exordos" ] || error "Invalid bundle layout in $ARTIFACT"
    find "$UNPACKED/exordos" -type l > "$TEMP_DIR/links"
    while IFS= read -r LINK; do
        LINK_TARGET=$(readlink "$LINK")
        case "$LINK_TARGET" in
            /*|..|../*|*/../*|*/..) error "Unsafe symlink in $ARTIFACT" ;;
        esac
    done < "$TEMP_DIR/links"
    find "$UNPACKED/exordos" \( -type f -o -type d \) -exec chmod go-w {} +
    ARCHIVE_VERSION=$("$UNPACKED/exordos/exordos" --silent --no-check-updates version)
    [ "$ARCHIVE_VERSION" = "$VERSION" ] || error "Archive version does not match $VERSION"
    printf '%s\n' "$ACTUAL_HASH" > "$UNPACKED/exordos/.archive-sha256"
    : > "$UNPACKED/exordos/.complete"

    [ ! -e "$TARGET_DIR" ] && [ ! -L "$TARGET_DIR" ] || error "Version directory already exists"
    INSTALL_STAGE=$(privileged mktemp -d "$VERSIONS_DIR/.exordos-install.$VERSION.XXXXXX")
    privileged cp -a --no-preserve=ownership "$UNPACKED/exordos/." "$INSTALL_STAGE/"
    privileged chmod 0755 "$INSTALL_STAGE"
    STAGED_VERSION=$("$INSTALL_STAGE/exordos" --silent --no-check-updates version)
    [ "$STAGED_VERSION" = "$VERSION" ] || error "Staged version validation failed"
    privileged mv -nT "$INSTALL_STAGE" "$TARGET_DIR"
    [ ! -e "$INSTALL_STAGE" ] || error "Version directory already exists"
    INSTALL_STAGE=''
fi

if [ -e "$BINDIR/exordos" ] && [ ! -L "$BINDIR/exordos" ]; then
    [ -f "$BINDIR/exordos" ] || error "$BINDIR/exordos is not a regular file"
    LEGACY_HASH=$(sha256sum "$BINDIR/exordos")
    LEGACY_HASH=${LEGACY_HASH%% *}
    LEGACY_BINARY="$INSTALL_ROOT/legacy/exordos-onefile-$LEGACY_HASH"
    privileged mkdir -p "$INSTALL_ROOT/legacy"
    if [ ! -f "$LEGACY_BINARY" ]; then
        privileged cp -p --no-preserve=ownership "$BINDIR/exordos" "$LEGACY_BINARY"
    fi
    BACKUP_HASH=$(sha256sum "$LEGACY_BINARY")
    [ "${BACKUP_HASH%% *}" = "$LEGACY_HASH" ] || error "Legacy backup validation failed"
fi
{
    printf '%s\n' '#!/bin/sh'
    printf "exec '"
    printf '%s' "$TARGET_BINARY" | sed "s/'/'\\\\''/g"
    printf '%s\n' "' \"\$@\""
} > "$TEMP_DIR/launcher"
INSTALL_STAGE=$(privileged mktemp "$BINDIR/.exordos-install.XXXXXX")
privileged install -m 0755 "$TEMP_DIR/launcher" "$INSTALL_STAGE"
privileged mv -fT "$INSTALL_STAGE" "$BINDIR/exordos"
INSTALL_STAGE=''
status "exordos $VERSION was successfully installed to $BINDIR/exordos."
if [ "$(command -v exordos || :)" != "$BINDIR/exordos" ]; then
    status "Add $BINDIR to the start of PATH to use this installation."
fi

}

main
