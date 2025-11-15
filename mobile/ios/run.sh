#!/bin/bash
# Run script for Cleo iOS App

set -e  # Exit on error

echo "🚀 Starting Cleo iOS App..."
echo ""

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode is not installed or xcodebuild is not in PATH"
    echo "Please install Xcode from the App Store"
    exit 1
fi

# Navigate to iOS directory
cd "$(dirname "$0")"

# Check if backend is running
echo "🔍 Checking if backend services are running..."
if curl -s http://127.0.0.1:8001/health > /dev/null 2>&1; then
    echo "✅ Backend services detected"
else
    echo "⚠️  Backend services not detected at http://127.0.0.1:8001"
    echo "   Please start the backend first:"
    echo "   cd ../../backend && docker-compose up -d"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "📱 Building and running on iOS Simulator..."

# Get available simulators
SIMULATOR=$(xcrun simctl list devices available | grep "iPhone" | grep -v "unavailable" | head -n 1 | sed 's/.*(\(.*\)).*/\1/')

if [ -z "$SIMULATOR" ]; then
    echo "❌ No available iOS Simulator found"
    echo "Please open Xcode and download a simulator"
    exit 1
fi

echo "Using simulator: $SIMULATOR"
echo ""

# Build and run
xcodebuild -project CleoApp.xcodeproj \
    -scheme CleoApp \
    -sdk iphonesimulator \
    -configuration Debug \
    -destination "platform=iOS Simulator,id=$SIMULATOR" \
    -derivedDataPath build \
    clean build

# Get the app path
APP_PATH=$(find build/Build/Products/Debug-iphonesimulator -name "*.app" | head -n 1)

if [ -z "$APP_PATH" ]; then
    echo "❌ Failed to find built app"
    exit 1
fi

# Boot simulator if not already running
xcrun simctl boot "$SIMULATOR" 2>/dev/null || true

# Install and launch app
echo "📲 Installing app on simulator..."
xcrun simctl install "$SIMULATOR" "$APP_PATH"

echo "🎉 Launching Cleo..."
xcrun simctl launch "$SIMULATOR" com.cleoapp.ios

echo ""
echo "✅ App launched successfully!"
echo "💡 To view logs, run: xcrun simctl spawn booted log stream --predicate 'process == \"CleoApp\"'"
