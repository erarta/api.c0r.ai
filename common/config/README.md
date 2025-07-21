# Centralized Payment Plans Configuration

This directory contains the centralized configuration for all payment plans across the c0r.AI project.

## Overview

Previously, payment plans were duplicated across multiple files:
- `api.c0r.ai/app/config.py` (production prices)
- `pay.c0r.ai/app/stripe/config.py` (test prices)
- `pay.c0r.ai/app/yookassa_handlers/config.py` (test prices)

This led to inconsistencies and maintenance issues. Now all payment plans are centralized in [`payment_plans.py`](payment_plans.py).

## Usage

### Basic Import

```python
from common.config.payment_plans import PAYMENT_PLANS, get_payment_plans

# Get all payment plans
plans = get_payment_plans()
print(plans['basic']['price'])  # Price in kopecks
```

### Environment-Based Configuration

The configuration automatically adjusts based on environment variables:

```bash
# Development mode (default) - uses minimum Telegram amounts
ENVIRONMENT=development python3 your_script.py

# Production mode - uses real prices
ENVIRONMENT=production python3 your_script.py

# Test mode override - forces test prices even in production
TEST_MODE=true ENVIRONMENT=production python3 your_script.py
```

### Helper Functions

```python
from common.config.payment_plans import (
    get_plan_by_id,
    get_plan_price,
    get_plan_credits,
    validate_payment_plans
)

# Get specific plan
basic_plan = get_plan_by_id('basic')

# Get price for plan (in kopecks)
price = get_plan_price('basic')

# Get credits for plan
credits = get_plan_credits('pro')

# Validate configuration
is_valid = validate_payment_plans()
```

## Environment Variables

| Variable | Values | Description |
|----------|--------|-------------|
| `ENVIRONMENT` | `development`, `staging`, `production` | Sets the environment mode |
| `TEST_MODE` | `true`, `false` | Forces test prices regardless of environment |

## Price Configuration

### Development/Test Prices
- Basic: 1000 kopecks (10 RUB) - minimum Telegram amount
- Pro: 5000 kopecks (50 RUB) - minimum Telegram amount

### Production Prices
- Basic: 9900 kopecks (99 RUB)
- Pro: 34900 kopecks (349 RUB)

## Migration Guide

### For API Service (`api.c0r.ai`)

**Before:**
```python
from app.config import PAYMENT_PLANS
```

**After:**
```python
from common.config.payment_plans import PAYMENT_PLANS
```

### For Payment Service (`pay.c0r.ai`)

**Before:**
```python
from app.stripe.config import PAYMENT_PLANS
from app.yookassa_handlers.config import PAYMENT_PLANS
```

**After:**
```python
from common.config.payment_plans import PAYMENT_PLANS
```

## Testing

Run the configuration test to verify everything works:

```bash
# Test the configuration directly
python3 common/config/payment_plans.py

# Run unit tests (if pytest is available)
python3 -m pytest tests/unit/test_payment_plans_config.py -v
```

## Benefits

1. **Single Source of Truth** - All payment plans defined in one place
2. **Environment Awareness** - Automatic price adjustment based on environment
3. **Test Mode Support** - Easy testing with minimum Telegram amounts
4. **Validation** - Built-in configuration validation
5. **Backward Compatibility** - Existing imports continue to work
6. **Type Safety** - Helper functions with proper return types

## File Structure

```
common/config/
├── payment_plans.py    # Main configuration file
├── README.md          # This documentation
└── __init__.py        # Package initialization (if needed)
```

## Troubleshooting

### Import Errors

If you get import errors, make sure to add the common directory to your Python path:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'common'))
```

### Price Inconsistencies

If you notice price inconsistencies:

1. Check the `ENVIRONMENT` variable
2. Check if `TEST_MODE` is enabled
3. Run validation: `python3 common/config/payment_plans.py`

### Adding New Plans

To add a new payment plan:

1. Add it to `BASE_PAYMENT_PLANS` in [`payment_plans.py`](payment_plans.py)
2. Add prices for all environments in `PRICE_CONFIG`
3. Run validation to ensure everything works
4. Update this documentation

## Future Improvements

- [ ] Add support for multiple currencies
- [ ] Add plan feature flags
- [ ] Add plan availability by region
- [ ] Add promotional pricing support