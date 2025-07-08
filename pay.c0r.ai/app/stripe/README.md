# Stripe Provider

This directory contains all Stripe-specific payment logic and configuration for pay.c0r.ai.

- `config.py`: Defines all Stripe payment plans (PLANS_STRIPE).
- `client.py`: Contains the Stripe invoice/payment logic.

## How to extend
- Add new plans to `config.py` as needed.
- Implement new payment logic or webhooks in `client.py`.
- Keep all Stripe-specific code in this directory for modularity. 