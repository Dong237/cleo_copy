# Cleo Android App

AI-powered financial assistant for Android.

## Requirements

- Android Studio Hedgehog (2023.1.1) or later
- Android SDK 24+ (Android 7.0)
- Kotlin 1.9+
- Gradle 8.0+

## Tech Stack

- **UI Framework:** Jetpack Compose
- **Architecture:** MVVM with Clean Architecture
- **Networking:** Retrofit + OkHttp
- **State Management:** Flow, LiveData
- **Dependency Injection:** Hilt
- **Local Storage:** Room + EncryptedSharedPreferences
- **Analytics:** Firebase Analytics, Mixpanel
- **Crash Reporting:** Firebase Crashlytics
- **Push Notifications:** Firebase Cloud Messaging (FCM)

## Project Structure

```
app/
├── src/
│   ├── main/
│   │   ├── java/com/cleo/
│   │   │   ├── CleoApplication.kt
│   │   │   ├── di/               # Dependency injection
│   │   │   ├── data/             # Data layer
│   │   │   │   ├── local/        # Room database
│   │   │   │   ├── remote/       # API services
│   │   │   │   └── repository/   # Repositories
│   │   │   ├── domain/           # Domain layer
│   │   │   │   ├── model/        # Domain models
│   │   │   │   └── usecase/      # Use cases
│   │   │   ├── presentation/     # Presentation layer
│   │   │   │   ├── auth/         # Authentication screens
│   │   │   │   ├── dashboard/    # Home screen
│   │   │   │   ├── chat/         # AI chat
│   │   │   │   ├── budget/       # Budget management
│   │   │   │   ├── savings/      # Savings goals
│   │   │   │   └── profile/      # User profile
│   │   │   └── util/             # Utilities
│   │   └── res/                  # Resources
│   └── test/                     # Unit tests
└── build.gradle.kts
```

## Getting Started

### 1. Open in Android Studio

```bash
cd mobile/android
# Open this directory in Android Studio
```

### 2. Configuration

Create a `local.properties` file:

```properties
sdk.dir=/path/to/Android/sdk
api.base.url=http://10.0.2.2:8000/api/v1
```

Create `app/src/main/res/values/secrets.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="api_key">your_api_key_here</string>
</resources>
```

### 3. Build and Run

```bash
# Build the app
./gradlew assembleDebug

# Run on connected device/emulator
./gradlew installDebug
```

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

Follow Material Design 3 guidelines with custom branding.

**Colors:**
- Primary: `#5B47FB` (electric purple)
- Secondary: `#FF6B9D` (pink)
- Success: `#00C48C` (green)
- Warning: `#FFB547` (orange)
- Error: `#FF6B6B` (red)

**Typography:**
- Display: Roboto Bold
- Body: Roboto Regular

## Dependencies

```kotlin
dependencies {
    // Jetpack Compose
    implementation("androidx.compose.ui:ui:1.5.4")
    implementation("androidx.compose.material3:material3:1.1.2")

    // Networking
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")

    // Dependency Injection
    implementation("com.google.dagger:hilt-android:2.48")

    // Database
    implementation("androidx.room:room-runtime:2.6.0")

    // Firebase
    implementation("com.google.firebase:firebase-analytics:21.5.0")
    implementation("com.google.firebase:firebase-crashlytics:18.6.0")
    implementation("com.google.firebase:firebase-messaging:23.4.0")
}
```

## Testing

```bash
# Run unit tests
./gradlew test

# Run instrumented tests
./gradlew connectedAndroidTest

# Run lint checks
./gradlew lint
```

## Build Variants

- **Debug:** Development build with logging
- **Staging:** Pre-production testing
- **Release:** Production build with ProGuard

```bash
# Build release APK
./gradlew assembleRelease

# Build release AAB (for Play Store)
./gradlew bundleRelease
```

## Code Quality

```bash
# Run ktlint (Kotlin linter)
./gradlew ktlintCheck

# Format code
./gradlew ktlintFormat

# Run detekt (static analysis)
./gradlew detekt
```

## Useful Resources

- [Jetpack Compose Documentation](https://developer.android.com/jetpack/compose)
- [Android Architecture Components](https://developer.android.com/topic/libraries/architecture)
- [Material Design 3](https://m3.material.io/)

---

**Status:** 🚧 Placeholder - Implementation pending
