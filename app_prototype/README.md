# c0r.ai App (Flutter)

## Run
- `flutter pub get`
- `flutter run -d <device>`

## Environments
Create the following files from templates in `assets/env/`:

- `assets/env/.env.dev`
- `assets/env/.env.prod`

Required keys:

- `API_BASE_URL` — e.g., https://api.c0r.ai
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SENTRY_DSN` (optional)

## Lint & Format
- `flutter analyze`

## Testing
- `flutter test --coverage`
- Coverage target: >= 85%
- Widget tests under `test/widgets/`
- Unit tests under `test/unit/`
- Integration tests under `test/integration/`

## Build
- `flutter build ios`
- `flutter build appbundle`

## Structure
- `lib/core`: theme, router, widgets, pickers, config
- `lib/features`: screens by feature (home, onboarding, progress, settings, etc.)
- `lib/services`: api/auth clients and models

## API Namespaces
- `/v1/analyze` (common)
- `/v1/app/*` (tracker endpoints)

## Notes
- Light/Dark theme via `ThemeData`
- Supabase Auth JWT is attached to API calls via `ApiClient` interceptor
- All internal imports use `package:c0r_app/...`
