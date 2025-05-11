#!/bin/bash
# Script to download and install the Vosk model for better sample rate support
# This script downloads and extracts vosk-model-en-us-0.22

set -e  # Exit on error

echo "Starting Vosk model download and installation..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MODEL_DIR="$PROJECT_ROOT/models"
NEW_MODEL="vosk-model-en-us-0.22"
MODEL_ZIP="$NEW_MODEL.zip"
MODEL_URL="https://alphacephei.com/vosk/models/$MODEL_ZIP"

# Create models directory if it doesn't exist
mkdir -p "$MODEL_DIR"
cd "$MODEL_DIR"

# Check if model already exists
if [ -d "$NEW_MODEL" ]; then
    echo "Model directory already exists. Skipping download."
    echo "To force redownload, remove the existing directory first:"
    echo "rm -rf $MODEL_DIR/$NEW_MODEL"
    exit 0
fi

# Download the model
echo "Downloading $MODEL_ZIP (approximately 1.8GB)..."
echo "This may take a while depending on your internet connection."
curl -L -o "$MODEL_ZIP" "$MODEL_URL" --progress-bar

# Extract the model
echo "Extracting $MODEL_ZIP..."
unzip -q "$MODEL_ZIP"
echo "Model extracted successfully!"

# Clean up zip file to save space
echo "Cleaning up the zip file..."
rm -f "$MODEL_ZIP"

echo "Vosk model installation complete!"
echo "New model installed at: $MODEL_DIR/$NEW_MODEL"

echo "Done!"
