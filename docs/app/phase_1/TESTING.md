# Testing Strategy (≥85% coverage)

## Targets
- Unit tests: repositories, controllers (Riverpod notifiers), formatters, mappers
- Widget tests: core screens and shared components (goldens for stable UI)
- Integration tests: auth + onboarding flow, analyze happy-path, history fetch, progress/weight update

## Tools
- flutter_test, mocktail, golden_toolkit, integration_test
- Coverage: `flutter test --coverage` → enforce ≥85%

## Structure
- test/
  - unit/
  - widget/
  - integration/

## CI gates
- Format: `flutter format --set-exit-if-changed .`
- Analyze: `flutter analyze`
- Tests: `flutter test --coverage`; fail if <85%

## Stubs/mocks
- Mock Dio client; fake repositories
- Fake camera/picker; use test images
- Time and UUID fakes for deterministic outputs

## Accessibility checks
- Ensure semantics labels present in key widgets
- Golden tests with text scaling (1.2x, 1.5x)

## Contract tests (API)
- Validate `/v1/analyze` and `/v1/app/*` payloads against examples
