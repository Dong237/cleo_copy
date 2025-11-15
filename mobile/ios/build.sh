#!/bin/bash
# Build script for Cleo iOS App

set -e  # Exit on error

echo "🏗️  Building Cleo iOS App..."
echo ""

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode is not installed or xcodebuild is not in PATH"
    echo "Please install Xcode from the App Store"
    exit 1
fi

# Navigate to iOS directory
cd "$(dirname "$0")"

echo "📱 Building for iOS Simulator..."
xcodebuild -project CleoApp.xcodeproj \
    -scheme CleoApp \
    -sdk iphonesimulator \
    -configuration Debug \
    -derivedDataPath build \
    clean build

echo ""
echo "✅ Build completed successfully!"
echo ""
echo "To run the app, use ./run.sh or open CleoApp.xcodeproj in Xcode"
