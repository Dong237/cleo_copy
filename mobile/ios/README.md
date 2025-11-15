# Cleo iOS App

<div align="center">

![Cleo Logo](https://via.placeholder.com/150x150/667EEA/FFFFFF?text=CLEO)

**AI-Powered Financial Assistant for iOS**

[![iOS](https://img.shields.io/badge/iOS-16.0%2B-blue.svg)](https://developer.apple.com/ios/)
[![Swift](https://img.shields.io/badge/Swift-5.9-orange.svg)](https://swift.org/)
[![SwiftUI](https://img.shields.io/badge/SwiftUI-4.0-green.svg)](https://developer.apple.com/xcode/swiftui/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](../../LICENSE)

</div>

## 📱 Overview

The Cleo iOS app is a fully-featured financial assistant that helps users manage their money through AI-powered conversations, smart budgeting, automated savings, cash advances, and credit building.

### ✨ Key Features

- 🤖 **AI Chat** - Conversational assistant with 4 personality modes
- 💰 **Smart Budgeting** - Category-based budget tracking with alerts
- 🎯 **Savings Goals** - Automated savings with goal tracking
- 💵 **Cash Advances** - Quick cash when you need it ($20-$250)
- 📊 **Credit Building** - Secured credit card and score monitoring
- 📈 **Analytics** - Spending insights and financial health tracking
- 🔔 **Real-time Alerts** - Budget warnings and bill reminders

## 🏗️ Architecture

### Tech Stack

- **Language**: Swift 5.9+
- **UI Framework**: SwiftUI
- **Architecture**: MVVM (Model-View-ViewModel)
- **Networking**: Combine + URLSession
- **State Management**: Combine (@Published, ObservableObject)
- **Security**: Keychain (for token storage)
- **Min iOS**: 16.0+

### Project Structure

```
CleoApp/
├── App/                    # App entry point
│   ├── CleoAppApp.swift   # Main app
│   └── ContentView.swift  # Root view
├── Config/
│   └── APIConfig.swift    # API endpoints configuration
├── Models/
│   └── Models.swift       # All data models (User, Transaction, etc.)
├── Services/
│   ├── APIClient.swift    # Generic API client + Keychain
│   └── Services.swift     # All service classes
├── ViewModels/
│   ├── AuthViewModel.swift      # Authentication logic
│   └── DashboardViewModel.swift # Dashboard data management
├── Views/
│   ├── Auth/              # Login & Register
│   ├── Dashboard/         # Main dashboard
│   ├── Chat/              # AI chat interface
│   ├── Budget/            # Budget management
│   ├── Savings/           # Savings goals
│   ├── Advance/           # Cash advances
│   ├── Credit/            # Credit builder & score
│   └── Profile/           # User profile
└── Resources/
    └── Assets.xcassets    # Images, colors, icons
```

## 🚀 Getting Started

### Prerequisites

- **macOS** 13.0 or later
- **Xcode** 15.0 or later
- **iOS Simulator** or physical device running iOS 16.0+
- **Backend Services** running (see [backend README](../../backend/README.md))

### Option 1: Quick Setup (Recommended)

```bash
cd mobile/ios

# 1. Run setup script
./setup.sh

# 2. Start backend services (in separate terminal)
cd ../../
docker-compose up -d

# 3. Build and run the app
cd mobile/ios
./run.sh
```

### Option 2: Manual Setup

```bash
cd mobile/ios

# 1. Open project in Xcode
open CleoApp.xcodeproj

# 2. Select target device/simulator
# Click "CleoApp" at top left → Select simulator or device

# 3. Build and run
# Press Cmd+R or click the Play button
```

### Option 3: Command Line Build

```bash
cd mobile/ios

# Build for simulator
./build.sh

# Or use xcodebuild directly
xcodebuild -project CleoApp.xcodeproj \
    -scheme CleoApp \
    -sdk iphonesimulator \
    -configuration Debug \
    build
```

## 🔧 Configuration

### API Endpoints

Update `CleoApp/Config/APIConfig.swift` to point to your backend:

```swift
struct APIConfig {
    // For iOS Simulator
    static let baseURL = "http://127.0.0.1"
    
    // For physical device, use your Mac's IP
    // static let baseURL = "http://192.168.1.100"
    
    // Ports match backend services
    static let userServicePort = 8001
    static let bankingServicePort = 8002
    // ... etc
}
```

### Backend Services

Ensure all 10 backend services are running:

```bash
# Check if services are running
curl http://127.0.0.1:8001/health  # User Service
curl http://127.0.0.1:8002/health  # Banking Service
curl http://127.0.0.1:8003/health  # Budget Service
# ... etc
```

## 📦 Features Detail

### 1. Authentication
- Email/password registration
- Secure login with JWT tokens
- Keychain-based token storage (production-ready)
- Auto-login on app launch

### 2. Dashboard
- Total balance overview
- Monthly income vs spending
- Recent transactions (last 5)
- Savings goals progress
- Budget status with warnings
- Quick action buttons

### 3. AI Chat
- 4 personality modes:
  - **Supportive** - Encouraging and empathetic
  - **Funny** - Witty with pop culture references
  - **Strict** - Direct and no-nonsense
  - **Roast** - Sarcastic, calls out bad spending
- Real-time messaging
- Context-aware responses
- Chat history

### 4. Budget Management
- Create budgets by category
- Set monthly/weekly/yearly limits
- Visual progress indicators
- Budget vs actual spending
- Alerts at 90%+ usage

### 5. Savings Goals
- Multiple concurrent goals
- Target amount and deadline
- Automated contributions
- Progress tracking
- Goal achievement celebrations

### 6. Cash Advance
- Eligibility checking ($20-$250)
- Instant or standard delivery
- Transparent fee disclosure
- Repayment tracking
- Advance history

### 7. Credit Builder
- Credit score monitoring
- Score trend tracking
- Credit factors breakdown
- Enrollment in builder program
- Monthly contribution calculator
- Credit activity feed

### 8. Profile
- User information
- Subscription tier display
- Account settings
- Support access
- Logout

## 🔐 Security

### Token Storage
- **Production**: iOS Keychain (`kSecAttrAccessibleWhenUnlockedThisDeviceOnly`)
- **Encryption**: AES-256 at rest
- **Transport**: TLS 1.3 for API calls

### Best Practices
- No credentials stored in UserDefaults
- JWT tokens in Keychain only
- Automatic token refresh (future)
- Secure error handling

## 🧪 Testing

### Manual Testing

1. **Registration Flow**
   ```
   Email: test@example.com
   Password: Password123!
   Full Name: Test User
   ```

2. **Test Endpoints** (with backend running)
   - Login → Should receive JWT token
   - Dashboard → Should load user data
   - Chat → Should respond to messages
   - Budget → Create and view budgets
   - Savings → Create goals
   - Advance → Check eligibility
   - Credit → View credit score

### Unit Tests (Future)
```bash
# Run tests
xcodebuild test -project CleoApp.xcodeproj \
    -scheme CleoApp \
    -destination 'platform=iOS Simulator,name=iPhone 15'
```

## 📱 Supported Devices

- **iPhone**: All models running iOS 16.0+
- **iPad**: All models running iPadOS 16.0+
- **Simulators**: All iOS 16.0+ simulators

### Optimized For
- iPhone 15/15 Pro (primary)
- iPhone 14/14 Pro
- iPhone 13/13 Pro
- iPhone 12/12 Pro

## 🐛 Troubleshooting

### Common Issues

**1. "Failed to connect to backend"**
```bash
# Check if backend is running
docker ps | grep cleo

# Start backend if not running
cd ../../
docker-compose up -d
```

**2. "Xcode build error"**
```bash
# Clean build folder
rm -rf ~/Library/Developer/Xcode/DerivedData/CleoApp-*

# Rebuild
xcodebuild clean build -project CleoApp.xcodeproj
```

**3. "App crashes on launch"**
- Check Xcode console for errors
- Verify Info.plist is present
- Ensure iOS Deployment Target is set to 16.0

**4. "Cannot connect from physical device"**
```swift
// Update APIConfig.swift to use your Mac's IP
static let baseURL = "http://192.168.1.XXX"  // Your Mac's IP

// Find your Mac's IP:
// System Settings → Network → Wi-Fi → Details → IP Address
```

## 🛠️ Development

### Adding New Features

1. **Model** - Add to `Models/Models.swift`
2. **Service** - Add to `Services/Services.swift`
3. **ViewModel** - Create in `ViewModels/`
4. **View** - Create in `Views/[Feature]/`

Example:
```swift
// 1. Add Model
struct NewFeature: Codable {
    let id: UUID
    let name: String
}

// 2. Add Service
class NewFeatureService {
    static let shared = NewFeatureService()
    private let client = APIClient.shared
    
    func getFeatures() -> AnyPublisher<[NewFeature], Error> {
        // Implementation
    }
}

// 3. Add View
struct NewFeatureView: View {
    var body: some View {
        // Implementation
    }
}
```

### Code Style

- Use SwiftUI for all UI components
- Follow MVVM architecture strictly
- Use Combine for reactive programming
- Keep views small and composable
- Extract reusable components

## 📊 Performance

### Target Metrics
- App launch: < 2 seconds
- API response: < 500ms
- UI interactions: 60 FPS
- Memory usage: < 150MB

### Optimization Tips
- Use `@Published` sparingly
- Implement pagination for long lists
- Cache network responses
- Use SwiftUI Lazy stacks

## 🔄 CI/CD (Future)

```yaml
# .github/workflows/ios.yml
name: iOS CI
on: [push, pull_request]
jobs:
  build:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build
        run: xcodebuild build -project CleoApp.xcodeproj
      - name: Test
        run: xcodebuild test -project CleoApp.xcodeproj
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

- **Documentation**: [/docs](../../docs/)
- **Backend README**: [/backend/README.md](../../backend/README.md)
- **API Docs**: http://localhost:8001/docs (when backend running)
- **Issues**: [GitHub Issues](https://github.com/yourusername/cleo/issues)

## 🗺️ Roadmap

### ✅ Completed (v1.0)
- [x] Authentication (Login/Register)
- [x] Dashboard with financial overview
- [x] AI Chat with 4 personalities
- [x] Budget management
- [x] Savings goals
- [x] Cash advance
- [x] Credit builder & monitoring
- [x] Profile management
- [x] Keychain security

### 🚧 In Progress (v1.1)
- [ ] Unit tests (50+ tests)
- [ ] UI tests
- [ ] Dark mode support
- [ ] iPad optimization
- [ ] Localization (Spanish, French)

### 📋 Planned (v2.0)
- [ ] Plaid bank linking (real)
- [ ] Push notifications
- [ ] Biometric auth (Face ID/Touch ID)
- [ ] Widget support
- [ ] Apple Watch companion
- [ ] Siri shortcuts

---

<div align="center">

**Built with ❤️ using SwiftUI**

[Report Bug](https://github.com/yourusername/cleo/issues) · [Request Feature](https://github.com/yourusername/cleo/issues)

</div>
