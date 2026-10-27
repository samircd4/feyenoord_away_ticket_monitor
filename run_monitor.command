#!/bin/bash
# Navigate to the directory containing this script
cd "$(dirname "$0")"

echo "======================================================="
echo "           FEYENOORD AWAY TICKET MONITOR               "
echo "======================================================="
echo ""
echo "Starting ticket monitor on macOS..."
echo "(Press Ctrl + C in this window anytime to stop)"
echo ""

# Prefer uv if available, otherwise fallback to python3
if command -v uv &> /dev/null; then
    uv run main.py
elif command -v python3 &> /dev/null; then
    python3 main.py
elif command -v python &> /dev/null; then
    python main.py
else
    echo "❌ Error: Neither 'uv' nor 'python3' was found on your Mac."
    echo "Please install Python from https://www.python.org/downloads/ or via Homebrew: brew install python"
fi

echo ""
echo "Monitor has stopped."
read -p "Press [Enter] to exit..."
