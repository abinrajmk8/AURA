#!/bin/bash
# Setup script to allow IDS to run without sudo
# This grants network capabilities to Python

echo "🔧 Setting up IDS permissions..."
echo ""
echo "This will grant CAP_NET_RAW and CAP_NET_ADMIN capabilities to Python"
echo "This allows packet sniffing without sudo"
echo ""

# Get the actual Python binary (follow symlinks)
VENV_PYTHON="$(pwd)/venv/bin/python3"
ACTUAL_PYTHON=$(readlink -f "$VENV_PYTHON")

if [ ! -f "$ACTUAL_PYTHON" ]; then
    echo "❌ Error: Python binary not found"
    exit 1
fi

echo "Virtual env Python: $VENV_PYTHON"
echo "Actual Python binary: $ACTUAL_PYTHON"
echo ""
echo "Setting capabilities on: $ACTUAL_PYTHON"
echo ""

# Grant capabilities to actual Python binary
sudo setcap cap_net_raw,cap_net_admin=eip "$ACTUAL_PYTHON"

# Verify
echo "✓ Capabilities set!"
echo ""
echo "Verifying:"
getcap "$ACTUAL_PYTHON"

echo ""
echo "✅ Done! You can now run IDS without sudo"
echo ""
echo "To test, run:"
echo "  source venv/bin/activate"
echo "  python3 IDS/main.py"

