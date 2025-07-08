# YooKassa Provider

This directory contains all YooKassa-specific payment logic and configuration for pay.c0r.ai.

- `config.py`: Defines all YooKassa payment plans (PLANS_YOOKASSA).
- `client.py`: Contains the YooKassa invoice/payment logic.

## How to extend
- Add new plans to `config.py` as needed.
- Implement new payment logic or webhooks in `client.py`.
- Keep all YooKassa-specific code in this directory for modularity. 