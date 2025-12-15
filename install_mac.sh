#!/bin/bash
# XJTLU PDF Downloader - macOS Installation Script

# Change to script directory (works when run from any location)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "XJTLU PDF Downloader - macOS Setup"
echo "=========================================="
echo "Working directory: $PWD"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed."
    echo "Installing pip..."
    python3 -m ensurepip --upgrade
fi

echo "✅ pip3 found"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install --user -r requirements.txt
else
    pip3 install --user playwright requests
fi

# Install Playwright browsers
echo ""
echo "🌐 Installing Chromium browser for Playwright..."
python3 -m playwright install chromium

echo ""
echo "=========================================="
echo "✅ Installation complete!"
echo ""
echo "To run the application:"
echo "  python3 main.py"
echo ""
echo "Or make it executable:"
echo "  chmod +x run_mac.sh"
echo "  ./run_mac.sh"
echo "=========================================="
