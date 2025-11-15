# 🚀 Quick Start Guide

Get the Cleo iOS app running in 3 simple steps!

## Prerequisites

- macOS 13.0+
- Xcode 15.0+
- Docker Desktop (for backend)

## Step 1: Start Backend Services (2 minutes)

```bash
# From project root
cd /path/to/cleo_copy
docker-compose up -d

# Verify services are running
curl http://127.0.0.1:8001/health
# Should return: {"status":"healthy"}
```

## Step 2: Run Setup Script (1 minute)

```bash
cd mobile/ios
./setup.sh
```

## Step 3: Launch the App (1 minute)

**Option A: Using run script (easiest)**
```bash
./run.sh
```

**Option B: Using Xcode**
```bash
open CleoApp.xcodeproj
# Then press Cmd+R to build and run
```

## 🎉 That's it!

The app should now be running on the iOS Simulator.

### First Time Setup

1. **Register** a new account:
   - Email: `test@example.com`
   - Password: `Password123!`
   - Name: `Test User`

2. **Explore** the features:
   - 💰 Dashboard - See your financial overview
   - 🤖 Chat - Talk to Cleo AI
   - 📊 Budget - Create your first budget
   - 🎯 Savings - Set a savings goal
   - 💵 Advance - Check cash advance eligibility
   - 📈 Credit - View credit score

## 📱 Supported Devices

- iPhone 12+
- iOS 16.0+

## ⚠️ Troubleshooting

**Backend not connecting?**
```bash
# Check services
docker ps

# Restart if needed
docker-compose restart
```

**Xcode build errors?**
```bash
# Clean build
rm -rf ~/Library/Developer/Xcode/DerivedData/CleoApp-*

# Rebuild
./build.sh
```

**Physical device testing?**
Update `APIConfig.swift`:
```swift
static let baseURL = "http://YOUR_MAC_IP_ADDRESS"
```

## 📚 More Information

- Full README: [README.md](README.md)
- Backend README: [../../backend/README.md](../../backend/README.md)
- API Documentation: http://localhost:8001/docs

---

**Need help?** Open an issue on GitHub!
