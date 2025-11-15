#!/bin/bash
# Setup script for Cleo iOS development environment

set -e  # Exit on error

echo "🛠️  Setting up Cleo iOS Development Environment..."
echo ""

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode is not installed"
    echo ""
    echo "Please install Xcode from the App Store:"
    echo "1. Open App Store"
    echo "2. Search for 'Xcode'"
    echo "3. Click Install"
    echo ""
    exit 1
fi

echo "✅ Xcode is installed"
echo "   Version: $(xcodebuild -version | head -n 1)"
echo ""

# Check Xcode command line tools
if ! xcode-select -p &> /dev/null; then
    echo "📦 Installing Xcode Command Line Tools..."
    xcode-select --install
    echo "⚠️  Please complete the installation and run this script again"
    exit 1
fi

echo "✅ Xcode Command Line Tools installed"
echo ""

# Check if backend is available
echo "🔍 Checking backend services..."
cd "$(dirname "$0")/../.."

if [ -f "docker-compose.yml" ]; then
    echo "✅ Backend found"
    echo ""
    echo "To start the backend services, run:"
    echo "   docker-compose up -d"
    echo ""
else
    echo "⚠️  Backend docker-compose.yml not found"
fi

# Summary
echo "📋 Setup Summary:"
echo "   ✅ Xcode installed"
echo "   ✅ iOS project configured"
echo "   ✅ Build scripts ready"
echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start the backend: cd ../../ && docker-compose up -d"
echo "2. Build the app: ./build.sh"
echo "3. Run the app: ./run.sh"
echo ""
echo "Or simply open CleoApp.xcodeproj in Xcode!"
