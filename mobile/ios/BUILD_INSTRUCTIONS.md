# Cleo iOS App - Build Instructions

## Prerequisites

Before you begin, ensure you have the following installed:

- **macOS** (required for iOS development)
- **Xcode 15.0 or later** - [Download from Mac App Store](https://apps.apple.com/us/app/xcode/id497799835)
- **iOS 16.0+ SDK** (included with Xcode)
- **Swift 5.9+** (included with Xcode)
- **Docker Desktop** - For running backend services

## Architecture Overview

The Cleo iOS app uses:
- **SwiftUI** - Modern declarative UI framework
- **MVVM Pattern** - Model-View-ViewModel architecture
- **Combine Framework** - Reactive programming
- **URLSession** - Native HTTP networking
- **Codable** - JSON serialization

## Step 1: Start Backend Services

The iOS app requires all 10 backend microservices to be running. From the project root:

```bash
# Start all services with Docker Compose
cd /home/user/cleo_copy
docker-compose up -d

# Verify all services are running
docker-compose ps

# You should see 11 containers running:
# - postgres (database)
# - user-service (port 8001)
# - banking-service (port 8002)
# - budget-service (port 8003)
# - chat-service (port 8004)
# - savings-service (port 8005)
# - notification-service (port 8006)
# - advance-service (port 8007)
# - credit-service (port 8008)
# - analytics-service (port 8009)
# - recommendation-service (port 8010)
```

## Step 2: Verify Backend is Running

Check that services are accessible:

```bash
# Test User Service
curl http://localhost:8001/health

# Test Chat Service
curl http://localhost:8004/health

# All services should return: {"status":"healthy"}
```

## Step 3: Create Xcode Project

Since Xcode project files are binary and complex, you'll need to create the project manually:

### Option A: Using Xcode GUI (Recommended)

1. **Open Xcode**

2. **Create New Project**
   - File → New → Project
   - Select "iOS" → "App"
   - Click "Next"

3. **Configure Project**
   - **Product Name**: CleoApp
   - **Team**: Select your Apple Developer account (or use personal team for local testing)
   - **Organization Identifier**: com.cleo (or your own)
   - **Bundle Identifier**: com.cleo.CleoApp
   - **Interface**: SwiftUI
   - **Language**: Swift
   - **Storage**: None
   - Click "Next"

4. **Choose Location**
   - Navigate to `/home/user/cleo_copy/mobile/ios/`
   - **IMPORTANT**: Uncheck "Create Git repository" (we already have one)
   - Click "Create"

5. **Add Existing Files**
   - Delete the default `ContentView.swift` and `CleoAppApp.swift` files Xcode created
   - Right-click on CleoApp folder in Project Navigator
   - Select "Add Files to CleoApp..."
   - Navigate to `/home/user/cleo_copy/mobile/ios/CleoApp/`
   - Select all folders: Config, Models, Services, ViewModels, Views, Utils
   - Make sure "Copy items if needed" is **UNCHECKED** (files already in place)
   - Make sure "Create groups" is selected
   - Click "Add"

6. **Add Info.plist**
   - In Project Navigator, select CleoApp target
   - Go to "Info" tab
   - You should see the Info.plist we created automatically loaded

7. **Configure Build Settings**
   - Select CleoApp target
   - General tab:
     - **Minimum Deployments**: iOS 16.0
     - **Device Orientation**: Portrait, Landscape Left, Landscape Right
   - Build Settings tab:
     - Search for "Swift Language Version"
     - Set to "Swift 5"

### Option B: Using Command Line (Alternative)

If you prefer command line, you can create a basic Xcode project:

```bash
cd /home/user/cleo_copy/mobile/ios

# Create Xcode project using Swift Package Manager
swift package init --type executable --name CleoApp

# Then manually configure in Xcode as described above
```

## Step 4: Configure API Endpoints

The app is pre-configured to connect to local backend services. If you need to change the configuration:

1. Open `CleoApp/Config/APIConfig.swift`
2. Modify the base URL if your backend is running elsewhere:

```swift
struct APIConfig {
    // For iOS Simulator, use 127.0.0.1 (not localhost)
    static let baseURL = "http://127.0.0.1"

    // For physical device on same network, use your Mac's IP:
    // static let baseURL = "http://192.168.1.XXX"

    // Ports remain the same
    static let userServicePort = 8001
    // ... etc
}
```

**Finding Your Mac's IP Address:**
```bash
# macOS
ifconfig | grep "inet " | grep -v 127.0.0.1

# Or use System Preferences → Network
```

## Step 5: Build and Run

### Using Xcode

1. **Select Target**
   - Choose a simulator from the device dropdown (e.g., "iPhone 15 Pro")
   - Or connect a physical device

2. **Build the Project**
   - Press `Cmd + B` to build
   - Xcode will compile all Swift files

3. **Run the App**
   - Press `Cmd + R` to build and run
   - The iOS Simulator will launch
   - The app will install and open automatically

### Using Command Line

```bash
# List available simulators
xcrun simctl list devices

# Boot a simulator (optional, Xcode does this automatically)
xcrun simctl boot "iPhone 15 Pro"

# Build the app
xcodebuild -project CleoApp.xcodeproj -scheme CleoApp -sdk iphonesimulator

# Run in simulator
xcodebuild -project CleoApp.xcodeproj -scheme CleoApp -sdk iphonesimulator -destination 'platform=iOS Simulator,name=iPhone 15 Pro' test
```

## Step 6: Test the App

Once the app launches, you should see:

1. **Authentication Screen**
   - Beautiful gradient purple background
   - Login/Register toggle
   - Cleo logo and welcome message

2. **Create a Test Account**
   - Click "Register"
   - Enter:
     - Full Name: Test User
     - Email: test@example.com
     - Password: password123
   - Click "Sign Up"

3. **Explore the App**
   - **Dashboard Tab**: View financial overview
     - Total balance, income, spending
     - Savings goals progress
     - Recent transactions
     - Budget overview
   - **Chat Tab**: Talk to Cleo AI
     - Try different personalities (supportive, funny, strict, roast)
     - Ask financial questions
   - **Budget Tab**: Manage budgets
     - Create category budgets
     - Track spending vs budget
   - **Savings Tab**: Set savings goals
     - Create goals with target amounts
     - Set deadlines
   - **Profile Tab**: View account settings
     - Subscription info
     - Financial services links
     - Logout

## Troubleshooting

### Build Errors

**"Cannot find type 'X' in scope"**
- Make sure all files are added to the Xcode target
- Check that imports are correct (Foundation, SwiftUI, Combine)

**"No such module 'Combine'"**
- Ensure deployment target is iOS 13.0 or higher
- Combine is included in iOS SDK by default

**Multiple files with same name**
- Xcode may have created default files
- Delete duplicates, keep only our custom files

### Network Errors

**"The resource could not be loaded"**
- Verify backend services are running: `docker-compose ps`
- Check Info.plist has `NSAllowsLocalNetworking` set to `true`
- Verify API URLs use `127.0.0.1` not `localhost` for simulator

**"Connection refused"**
- Backend services may not be started
- Run `docker-compose up -d` from project root
- Check firewall settings aren't blocking local connections

**Testing on Physical Device**
- Update `APIConfig.baseURL` to your Mac's IP address
- Ensure device and Mac are on the same WiFi network
- Backend services must accept connections from network (not just localhost)

### Runtime Errors

**"Keychain error"**
- This is expected - we're using UserDefaults mock for demo
- Real production app would use proper Keychain

**"No data received from API"**
- Backend may not have test data
- Create some data through the app UI first
- Or use the backend API directly to seed data

## Project Structure

```
CleoApp/
├── CleoAppApp.swift          # App entry point
├── ContentView.swift          # Root view switcher (Auth/MainTab)
├── Info.plist                 # App configuration
├── Config/
│   └── APIConfig.swift        # API endpoints configuration
├── Models/
│   └── Models.swift           # Data models (User, Transaction, etc.)
├── Services/
│   ├── APIClient.swift        # Generic HTTP client
│   └── Services.swift         # Service layer (Auth, Banking, etc.)
├── ViewModels/
│   ├── AuthViewModel.swift    # Authentication state
│   └── DashboardViewModel.swift
├── Views/
│   ├── Auth/
│   │   └── AuthView.swift     # Login/Register screens
│   ├── MainTabView.swift      # Tab navigation
│   ├── Dashboard/
│   │   └── DashboardView.swift
│   ├── Chat/
│   │   └── ChatView.swift
│   ├── Budget/
│   │   └── BudgetView.swift
│   ├── Savings/
│   │   └── SavingsView.swift
│   └── Profile/
│       └── ProfileView.swift
└── Utils/
    ├── ColorExtension.swift   # Hex color support
    └── KeychainHelper.swift   # Token storage
```

## API Integration

The app connects to these backend services:

| Service | Port | Purpose |
|---------|------|---------|
| User Service | 8001 | Authentication, user management |
| Banking Service | 8002 | Bank connections, transactions |
| Budget Service | 8003 | Budget creation and tracking |
| Chat Service | 8004 | AI chat with Cleo |
| Savings Service | 8005 | Savings goals |
| Notification Service | 8006 | Push notifications |
| Advance Service | 8007 | Cash advances |
| Credit Service | 8008 | Credit building |
| Analytics Service | 8009 | Financial analytics |
| Recommendation Service | 8010 | AI recommendations |

## Development Tips

1. **Live Preview**
   - Use Xcode's live preview for faster UI development
   - Press `Option + Cmd + P` to resume preview
   - Works for individual views

2. **Debugging**
   - Set breakpoints by clicking line numbers
   - Use `print()` statements for logging
   - View console output in Xcode's debug area

3. **Testing API Calls**
   - Use Xcode's Network Inspector
   - Debug → Debug Workflow → Network Link Conditioner
   - Test different network conditions

4. **Modifying UI**
   - All views use SwiftUI
   - Changes are reflected immediately with live preview
   - Modify colors in `ColorExtension.swift`

## Next Steps

1. **Add Missing Screens**
   - Advance Service UI (cash advances)
   - Credit Service UI (credit builder)
   - Analytics dashboard
   - Recommendations feed

2. **Enhance Features**
   - Add pull-to-refresh on lists
   - Implement proper error handling UI
   - Add loading skeletons
   - Implement push notifications

3. **Production Ready**
   - Replace UserDefaults with proper Keychain
   - Add comprehensive error handling
   - Implement proper token refresh
   - Add unit tests
   - Add UI tests

4. **Deploy to TestFlight**
   - Sign up for Apple Developer Program ($99/year)
   - Configure code signing
   - Create App Store Connect app
   - Upload build to TestFlight
   - Invite beta testers

## Resources

- [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui)
- [Combine Framework](https://developer.apple.com/documentation/combine)
- [iOS Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/ios)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review backend service logs: `docker-compose logs [service-name]`
3. Check Xcode console for error messages
4. Verify API responses with curl/Postman

## License

This is a demo application for educational purposes.
