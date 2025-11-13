# Cleo iOS App - Quick Start Guide

Get the Cleo iOS demo app running in 5 minutes!

## TL;DR

```bash
# 1. Start backend services
cd /home/user/cleo_copy
docker-compose up -d

# 2. Open Xcode and create new iOS App project
# - Name: CleoApp
# - Location: /home/user/cleo_copy/mobile/ios/
# - Add all existing files from CleoApp/ folder

# 3. Build and Run (Cmd + R)
# 4. Register test account in app
# 5. Explore features!
```

## Detailed Steps

### 1. Start Backend (2 minutes)

```bash
# From project root
docker-compose up -d

# Verify all 10 services are running
docker-compose ps
```

You should see 11 containers (postgres + 10 services on ports 8001-8010).

### 2. Create Xcode Project (2 minutes)

1. **Open Xcode**
2. **File → New → Project**
3. **Select "App" template**
4. **Configure:**
   - Product Name: `CleoApp`
   - Interface: `SwiftUI`
   - Language: `Swift`
5. **Save to:** `/home/user/cleo_copy/mobile/ios/`
6. **Delete default files** Xcode created
7. **Add existing files:**
   - Right-click CleoApp folder
   - "Add Files to CleoApp..."
   - Select all folders (Config, Models, Services, ViewModels, Views, Utils)
   - Uncheck "Copy items if needed"
   - Add

### 3. Run App (30 seconds)

1. **Select iPhone 15 Pro simulator**
2. **Press Cmd + R**
3. **Wait for build and simulator launch**

### 4. Test Features (1 minute)

1. **Register account:**
   - Name: Test User
   - Email: test@example.com
   - Password: password123

2. **Explore tabs:**
   - Dashboard - See financial overview
   - Chat - Talk to Cleo with different personalities
   - Budget - Create and track budgets
   - Savings - Set savings goals
   - Profile - View account info

## Common Issues

### Backend not starting?
```bash
docker-compose down
docker-compose up -d --build
```

### Can't connect to backend?
- Check `APIConfig.swift` uses `127.0.0.1` (not `localhost`)
- Verify Info.plist allows local networking
- Restart simulator

### Build errors?
- Make sure all files are added to Xcode target
- Check deployment target is iOS 16.0+
- Clean build folder (Cmd + Shift + K)

## What's Included

✅ **Complete UI**
- Beautiful gradient authentication
- 5-tab navigation
- Dashboard with financial cards
- AI chat with personality modes
- Budget management with progress tracking
- Savings goals with deadlines
- Profile and settings

✅ **Full Backend Integration**
- 10 microservices connected
- JWT authentication
- Real-time data sync
- Error handling

✅ **Modern Architecture**
- SwiftUI declarative UI
- MVVM pattern
- Combine reactive programming
- Type-safe networking

## Next Steps

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for:
- Detailed setup options
- Troubleshooting guide
- Development tips
- Production deployment

Enjoy exploring Cleo! 🎉
