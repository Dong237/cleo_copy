# Cleo iOS App

AI-powered financial assistant for iOS.

## Requirements

- Xcode 15.0+
- iOS 16.0+
- Swift 5.9+
- CocoaPods or Swift Package Manager

## Tech Stack

- **UI Framework:** SwiftUI
- **Architecture:** MVVM (Model-View-ViewModel)
- **Networking:** Alamofire or URLSession
- **State Management:** Combine
- **Local Storage:** CoreData + Keychain
- **Analytics:** Firebase Analytics, Mixpanel
- **Crash Reporting:** Firebase Crashlytics
- **Push Notifications:** Firebase Cloud Messaging (FCM)

## Project Structure

```
Cleo/
├── App/                    # App configuration
│   ├── CleoApp.swift      # Main app entry point
│   └── AppDelegate.swift  # App lifecycle
├── Features/              # Feature modules
│   ├── Authentication/    # Login, registration
│   ├── Dashboard/         # Home screen
│   ├── Chat/              # AI chat interface
│   ├── Budget/            # Budget management
│   ├── Savings/           # Savings goals
│   └── Profile/           # User profile & settings
├── Core/                  # Core utilities
│   ├── Networking/        # API client
│   ├── Storage/           # Local data storage
│   ├── Extensions/        # Swift extensions
│   └── Models/            # Data models
├── Resources/             # Assets, fonts, etc.
└── Tests/                 # Unit and UI tests
```

## Getting Started

### 1. Install Dependencies

```bash
cd mobile/ios

# Using CocoaPods
pod install

# Or using Swift Package Manager (via Xcode)
# File > Add Packages...
```

### 2. Configuration

Create a `Config.xcconfig` file:

```
API_BASE_URL = http://localhost:8000/api/v1
ENVIRONMENT = development
```

### 3. Run the App

Open `Cleo.xcworkspace` in Xcode and run on simulator or device.

## Key Features to Implement

### Phase 1 (MVP)
- [ ] User authentication (login/register)
- [ ] Plaid bank linking
- [ ] Transaction list and details
- [ ] Basic AI chat interface
- [ ] Budget creation and tracking
- [ ] Savings goals
- [ ] Push notifications

### Phase 2
- [ ] Personality customization
- [ ] Cash advance request
- [ ] Bill tracking
- [ ] Spending habits review (swipe feature)
- [ ] Weekly quizzes

### Phase 3
- [ ] Credit builder card
- [ ] Credit score monitoring
- [ ] Early paycheck access

## Design System

Follow the design system defined in Figma (link TBD).

**Colors:**
- Primary: `#5B47FB` (electric purple)
- Secondary: `#FF6B9D` (pink)
- Success: `#00C48C` (green)
- Warning: `#FFB547` (orange)
- Error: `#FF6B6B` (red)

**Typography:**
- Heading: SF Pro Display Bold
- Body: SF Pro Text Regular

## Testing

```bash
# Run unit tests
xcodebuild test -workspace Cleo.xcworkspace -scheme Cleo -destination 'platform=iOS Simulator,name=iPhone 15'

# Run UI tests
xcodebuild test -workspace Cleo.xcworkspace -scheme CleoUITests -destination 'platform=iOS Simulator,name=iPhone 15'
```

## Build & Deploy

```bash
# Build for testing
xcodebuild archive -workspace Cleo.xcworkspace -scheme Cleo -archivePath ./build/Cleo.xcarchive

# Export IPA
xcodebuild -exportArchive -archivePath ./build/Cleo.xcarchive -exportPath ./build -exportOptionsPlist ExportOptions.plist
```

## Useful Resources

- [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui/)
- [Combine Framework](https://developer.apple.com/documentation/combine)
- [iOS Design Guidelines](https://developer.apple.com/design/human-interface-guidelines/ios)

---

**Status:** 🚧 Placeholder - Implementation pending
