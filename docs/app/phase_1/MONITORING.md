# Monitoring & Observability

## Crashes & Errors
- Sentry SDK (Flutter)
  - DSN via env
  - Release + environment tags
  - Breadcrumbs (navigation, HTTP)
  - PII disabled by default

## Performance
- Sentry Performance (traces) for critical flows: analyze upload, home load
- App start time metric; frame build jank sampling

## Analytics (minimal)
- Events (no PII):
  - onboarding_complete
  - analyze_success / analyze_failed (error_code)
  - payment_success / payment_failed (gateway)
- Provider: lean (PostHog/Amplitude) or server-logged via `/v1/app/metrics` (optional)

## Logging hygiene
- Redact tokens and sensitive headers
- Correlate with `X-Request-ID` across app and API

## Alerts
- Error rate threshold → Slack/Telegram
- Payment webhook failures → alert
