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

IS_WSL2=false

KERN=$(uname -r)
case "$KERN" in
    *icrosoft*WSL2 | *icrosoft*wsl2) IS_WSL2=true;;
    *icrosoft) error "Microsoft WSL1 is not currently supported. Please use WSL2 with 'wsl --set-version <distro> 2'" ;;
    *) ;;
esac

NEEDS=$(require curl grep xargs git)
if [ -n "$NEEDS" ]; then
    status "ERROR: The following tools are required but missing:"
    for NEED in $NEEDS; do
        echo "  - $NEED"
    done
    exit 1
fi

# Function to find a writable bin directory
find_writable_bindir() {
    # Check for user's personal bin directories first
    for dir in "$HOME/bin" "$HOME/.local/bin"; do
      if [ -d "$dir" ] && [ -w "$dir" ]; then
          echo "$dir"
          return
      fi
    done

    # If ~/.local/bin is in PATH but doesn't exist, create it
    if echo "$PATH" | tr ':' '\n' | grep -q "$HOME/.local/bin"; then
        if [ ! -d "$HOME/.local/bin" ]; then
          mkdir -p "$HOME/.local/bin"
        fi
        echo "$HOME/.local/bin"
        return
    fi

    # Check other directories in PATH that are writable
    for dir in $(echo $PATH | tr ':' ' '); do
        if [ -d "$dir" ] && [ -w "$dir" ]; then
            echo "$dir"
            return
        fi
    done

    # Create $HOME/.local/bin if it doesn't exist and add to PATH
    if [ ! -d "$HOME/.local/bin" ]; then
        mkdir -p "$HOME/.local/bin"
        # Add to shell profile for persistence
        if [ -n "${BASH_VERSION-}" ]; then
            PROFILE="$HOME/.bashrc"
        else
            PROFILE="$HOME/.profile"
        fi
        if ! grep -q '.local/bin' "$PROFILE" 2>/dev/null; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$PROFILE"
        fi
        echo "$HOME/.local/bin"
        return
    fi

    # If no writable directory found in PATH, try standard system directories with sudo
    for dir in /usr/local/bin /usr/bin /bin; do
        if [ -d "$dir" ]; then
            # Try to create directory if it doesn't exist (with sudo)
            if ! [ -w "$dir" ]; then
                status "Need sudo to write to $dir"
                sudo mkdir -p "$dir" 2>/dev/null || true
                if [ -w "$dir" ]; then
                    echo "$dir"
                    return
                fi
            else
                echo "$dir"
                return
            fi
        fi
    done

    # If no suitable directory found
    error "No suitable directory found to install exordos binary"
}

! command -v exordos >/dev/null 2>&1
OLD_BINARY_EXISTS=$?
OLD_BINARY=$(which exordos 2>/dev/null || echo "/usr/local/bin/exordos")
# Find a writable directory
BINDIR=$(find_writable_bindir)

status "Installing exordos to $BINDIR"

# Determine the correct filename based on OS version
LINUX_FILENAME="exordos-linux"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$ID" = "ubuntu" ]; then
        # Check Ubuntu version for Resolute (26.04)
        VERSION_MAJOR="${VERSION_ID%%.*}"
        if [ "$VERSION_MAJOR" = "26" ]; then
            LINUX_FILENAME="exordos-linux-ubuntu-resolute"
        fi
    fi
fi

# Download and install
download() {
    local url_base="$1"
    local dest_dir="$2"
    local filename="$3"

    if curl --fail --silent --head --location "${url_base}/${filename}" >/dev/null 2>&1; then
        status "Downloading ${filename}"
        curl --fail --show-error --location --progress-bar \
            "${url_base}/${filename}" --output "${dest_dir}/exordos"
        return 0
    fi
    error "Failed to download ${filename}"
}

download "https://repo.exordos.com/exordos/latest" "$BINDIR" "$LINUX_FILENAME"
chmod +x "$BINDIR"/exordos

if [ -f "$OLD_BINARY" ]; then
    if [ "$BINDIR/exordos" != "$OLD_BINARY" ]; then
        echo "Found old binary at $OLD_BINARY"
        echo "Current binary is at: $BINDIR/exordos"
        if [ -n "${DELETE_OLD+x}" ]; then
            response=Y
        else
            echo "Do you want to remove the old exordos binary? (y/N)"
            read -r response
        fi
        case "$response" in
            [yY])
                sudo rm -f "$OLD_BINARY"
                echo "Old binary removed"
                ;;
            *)
                echo "Keeping old binary"
                ;;
        esac
    fi
fi

install_success() {
  # if exordos cmd did not exist before the launch of this script, this is installing, not updating
  if [ "$OLD_BINARY_EXISTS" -eq 0 ]; then
      "$BINDIR"/exordos introduction
  fi

  # if command is not available, print instructions to run exordos
  if ! command -v exordos >/dev/null 2>&1; then
    status ""
    status "To run exordos, either restart your shell or run:"
    status ""
    status "    $BINDIR/exordos"
  fi

  version=$("$BINDIR"/exordos --no-check-updates version)
  status ""
  status "exordos $version was successfully installed"
}
trap install_success EXIT

}

main
