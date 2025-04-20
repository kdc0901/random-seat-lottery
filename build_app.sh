#!/bin/bash

# Check if Command Line Tools are installed (for iconutil)
if ! command -v iconutil &> /dev/null; then
    echo "Command Line Tools are not installed. Please install them using:"
    echo "xcode-select --install"
    exit 1
fi

# Install required packages
python3 -m pip install --upgrade pip
python3 -m pip install pyinstaller
python3 -m pip install -r requirements.txt

# Create icon
python3 create_icon.py

# Build the app
python3 -m PyInstaller --windowed --icon=app.icns --name="Random Lottery" random_lottery_gui.py

echo "App build complete. You can find the app in the dist folder." 