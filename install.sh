#!/bin/bash

# Installation script for airenamer

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="airenamer.py"
INSTALL_DIR="$HOME/Dev/Tools/Helpers/bin"
INSTALL_NAME="airenamer"

echo "🚀 Installing airenamer..."

# Check if script exists
if [ ! -f "$SCRIPT_DIR/$SCRIPT_NAME" ]; then
    echo "❌ Error: $SCRIPT_NAME not found in $SCRIPT_DIR"
    exit 1
fi

# Make script executable
chmod +x "$SCRIPT_DIR/$SCRIPT_NAME"
echo "✅ Made script executable"

# Create install directory if it doesn't exist
mkdir -p "$INSTALL_DIR"
echo "✅ Created/verified install directory: $INSTALL_DIR"

# Check if already installed
if [ -f "$INSTALL_DIR/$INSTALL_NAME" ]; then
    echo "⚠️  $INSTALL_NAME already exists in $INSTALL_DIR"
    read -p "Overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    rm "$INSTALL_DIR/$INSTALL_NAME"
fi

# Create symlink
ln -s "$SCRIPT_DIR/$SCRIPT_NAME" "$INSTALL_DIR/$INSTALL_NAME"
echo "✅ Created symlink: $INSTALL_DIR/$INSTALL_NAME -> $SCRIPT_DIR/$SCRIPT_NAME"

# Check if directory is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "⚠️  $INSTALL_DIR is not in your PATH."
    echo "   Add it to your ~/.zshrc with:"
    echo "   echo 'export PATH=\"\$HOME/Dev/Tools/Helpers/bin:\$PATH\"' >> ~/.zshrc"
    echo "   source ~/.zshrc"
fi

# Verify installation
if command -v "$INSTALL_NAME" &> /dev/null; then
    echo "✅ Installation successful!"
    echo ""
    echo "You can now use 'airenamer' from anywhere."
    echo "Try: airenamer --help"
else
    echo "⚠️  Installation complete, but command not found in PATH."
    echo "You may need to restart your terminal or run: source ~/.zshrc"
fi

