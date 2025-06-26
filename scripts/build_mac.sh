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
    --windowed \
    --name Argus \
    --icon src/argus/assets/icon.icns \
    --add-data "src/argus/assets:assets" \
    src/argus/main.py

# Create app bundle
echo "Creating macOS app bundle..."
mkdir -p dist/Argus.app/Contents/{MacOS,Resources}

cp dist/Argus dist/Argus.app/Contents/MacOS/
cp src/argus/assets/icon.icns dist/Argus.app/Contents/Resources/

cat > dist/Argus.app/Contents/Info.plist <<EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Argus</string>
    <key>CFBundleIconFile</key>
    <string>icon</string>
    <key>CFBundleIdentifier</key>
    <string>com.yourcompany.Argus</string>
    <key>CFBundleName</key>
    <string>Argus</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
</dict>
</plist>
EOL

echo "Build complete: dist/Argus.app"