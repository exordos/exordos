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

TEMP_DIR=$(mktemp -d)
cleanup() { rm -rf $TEMP_DIR; }
trap cleanup EXIT

available() { command -v $1 >/dev/null; }
require() {
    local MISSING=''
    for TOOL in $*; do
        if ! available $TOOL; then
            MISSING="$MISSING $TOOL"
        fi
    done

    echo $MISSING
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
    NEEDS=$(require curl)
    if [ -n "$NEEDS" ]; then
        status "ERROR: The following tools are required but missing:"
        for NEED in $NEEDS; do
            echo "  - $NEED"
        done
        exit 1
    fi

    BINDIR="/usr/local/bin"
    DOWNLOAD_URL="https://repo.exordos.com/exordos/latest/exordos-macos-arm"

    status "Installing exordos to $BINDIR..."
    mkdir -p "$BINDIR" 2>/dev/null || sudo mkdir -p "$BINDIR"
    curl --fail --show-error --location --progress-bar \
        "$DOWNLOAD_URL" --output "$TEMP_DIR/exordos"
    chmod +x "$TEMP_DIR/exordos"
    mv "$TEMP_DIR/exordos" "$BINDIR/exordos" 2>/dev/null || \
        sudo mv "$TEMP_DIR/exordos" "$BINDIR/exordos"

    status "Install complete. You can now run 'exordos'."
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
        export PATH="$HOME/.local/bin:$PATH"
        # Add to shell profile for persistence
        if [ -n "${BASH_VERSION-}" ]; then
            PROFILE="$HOME/.bashrc"
        else
            PROFILE="$HOME/.profile"
        fi
        if ! grep -q 'export PATH="\$HOME/.local/bin:\$PATH"' "$PROFILE" 2>/dev/null; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$PROFILE"
        fi
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

OLD_BINARY=$(which exordos 2>/dev/null || echo "/usr/local/bin/exordos")
# Find a writable directory
BINDIR=$(find_writable_bindir)

status "Installing exordos to $BINDIR"

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

download "https://repo.exordos.com/exordos/latest" "$BINDIR" "exordos-linux"
chmod +x "$BINDIR"/exordos

if [ -f "$OLD_BINARY" ]; then
    if [ "$BINDIR" != "/usr/local/bin" ]; then
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
    exordos introduction
}
trap install_success EXIT

}

main
