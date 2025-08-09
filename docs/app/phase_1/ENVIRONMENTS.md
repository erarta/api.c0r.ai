# Environments & Config

## App flavors
- dev, prod: separate bundle IDs, icons, names
- API base URLs per flavor

## Env variables (app)
- SUPABASE_URL
- SUPABASE_ANON_KEY
- API_BASE_URL (e.g., https://api.c0r.ai)
- SENTRY_DSN (optional)

## Backend
- Supabase JWKS available for JWT verify in API service
- CORS allow app schemes in dev (http://localhost, custom scheme for deep links)

## Keys & auth providers
- Apple Sign-In: bundle ID, Services ID, associated domain if needed
- Google OAuth: iOS client ID, Android SHA certs

## Secrets handling
- No secrets in repo; use .env and CI secret stores
- Rotate keys periodically
