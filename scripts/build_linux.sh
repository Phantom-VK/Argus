#!/bin/bash

# Verify Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found"
    exit 1
fi

# Install requirements
pip3 install -r requirements.txt

# Build
pyinstaller \
    --onefile \
    --name argus \
    --add-data "src/argus/assets:assets" \
    src/argus/main.py

echo "Build complete: dist/argus"