#!/bin/bash
# Install pingme to ~/.local/bin

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/.local/bin"

mkdir -p "$INSTALL_DIR"
ln -sf "$SCRIPT_DIR/scripts/pingme.py" "$INSTALL_DIR/pingme"
chmod +x "$SCRIPT_DIR/scripts/pingme.py"

echo "✅ Installed pingme to $INSTALL_DIR/pingme"

# Check if in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "⚠️  Add to your shell config:"
    echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
fi
