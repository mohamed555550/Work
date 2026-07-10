# صنعتى Mobile Builds

This project uses Capacitor.

## API URL

Before building store apps, edit `.env.mobile`:

```env
VITE_API_BASE_URL=https://your-production-domain.com/api/v1
VITE_WS_BASE_URL=wss://your-production-domain.com/ws
```

Do not use `localhost` for store builds.

## Sync web assets

```bash
npm run cap:android
npm run cap:ios
```

## Android

Debug APK:

```bash
npm run android:debug
```

Release bundle for Google Play:

```bash
npm run android:release
```

For Play Store upload, configure signing in Android Studio first.

## iPhone

The iOS project is in `ios/`, but the final archive must be built on macOS with Xcode:

```bash
npm run cap:ios
npx cap open ios
```

Then use Xcode Archive and upload to App Store Connect.
