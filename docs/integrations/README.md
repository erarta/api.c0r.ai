# Integrations Documentation

This directory contains documentation for all external service integrations used in the c0r.AI project.

## Payment Integrations

### YooKassa
- [`YOOKASSA_SETUP.md`](YOOKASSA_SETUP.md) - Complete YooKassa payment system setup guide
- [`YOOKASSA_WEBHOOK_SETUP.md`](YOOKASSA_WEBHOOK_SETUP.md) - Webhook configuration for YooKassa
- [`get_yookassa_keys.md`](get_yookassa_keys.md) - Guide to obtain YooKassa API keys

## Telegram Integration

### Bot Setup & Configuration
- [`TELEGRAM_PAYMENTS_SETUP.md`](TELEGRAM_PAYMENTS_SETUP.md) - Telegram Bot payment integration setup
- [`TELEGRAM_TEST_SCENARIOS.md`](TELEGRAM_TEST_SCENARIOS.md) - Testing scenarios for Telegram Bot functionality

## Service Directories

### GitHub Integration
- [`github/`](github/) - GitHub Actions, webhooks, and CI/CD integration documentation

### Payment Services
- [`payments/`](payments/) - Detailed payment service integration guides (Stripe, YooKassa)

### Telegram Services
- [`telegram/`](telegram/) - Advanced Telegram Bot integration documentation

## Quick Reference

| Service | Setup Guide | Testing Guide | API Keys |
|---------|-------------|---------------|----------|
| YooKassa | [Setup](YOOKASSA_SETUP.md) | [Testing](../testing/payment-testing.md) | [Keys](get_yookassa_keys.md) |
| Telegram | [Setup](TELEGRAM_PAYMENTS_SETUP.md) | [Scenarios](TELEGRAM_TEST_SCENARIOS.md) | [Bot Token](../getting-started/GET_TELEGRAM_ID.md) |

## Integration Architecture

All integrations follow the modular service architecture:
- **API Service** (`services/api/`) - Handles external API calls
- **Payment Service** (`services/pay/`) - Manages payment processing
- **ML Service** (`services/ml/`) - Processes AI/ML integrations

For development setup, see [`../development/README.md`](../development/README.md).
For deployment guides, see [`../deployment/README.md`](../deployment/README.md).