# Telegram Payments Setup Guide

This guide will help you set up Telegram native payments for your c0r.ai bot using BotFather and YooKassa.

## Prerequisites

1. **Telegram Bot**: Your bot must be created via BotFather
2. **YooKassa Account**: Register at [yookassa.ru](https://yookassa.ru)
3. **YooKassa Shop**: Configure your shop for Telegram payments

## Step 1: Configure YooKassa for Telegram

1. **Login to YooKassa Dashboard**:
   - Go to [yookassa.ru](https://yookassa.ru)
   - Login to your account

2. **Create/Configure Shop**:
   - Go to "Shops" section
   - Create new shop or select existing one
   - **Important**: Enable "Telegram Payments" in shop settings

3. **Get Credentials**:
   - Note your `Shop ID` (found in shop settings)
   - Generate `Secret Key` (Settings → API Keys)
   - **Get Provider Token** for Telegram (Settings → Telegram Payments)

## Step 2: Configure Bot via BotFather

1. **Open BotFather**:
   - Start chat with [@BotFather](https://t.me/BotFather)
   - Send `/mybots`
   - Select your bot

2. **Enable Payments**:
   - Select "Payments" from bot menu
   - Choose "Connect Payment Provider"
   - Select "YooKassa" from the list

3. **Enter YooKassa Credentials**:
   - **Shop ID**: Enter your YooKassa Shop ID
   - **Secret Key**: Enter your YooKassa Secret Key
   - Confirm the setup

4. **Get Provider Token**:
   - After successful setup, BotFather will give you a **Provider Token**
   - Copy this token - you'll need it for `YOOKASSA_PROVIDER_TOKEN`

## Step 3: Environment Configuration

Add these variables to your `.env` file:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token

# YooKassa for Telegram Payments
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key
YOOKASSA_PROVIDER_TOKEN=your_provider_token_from_botfather
```

## Step 4: Test Payment Flow

### Testing Steps:

1. **Start your bot** and send `/start`
2. **Use up free credits** (send 3 photos)
3. **Send another photo** - you should see payment buttons
4. **Click "Basic Plan"** - invoice should appear in Telegram
5. **Complete payment** using test card
6. **Verify credits** are added to your account

### Test Cards for YooKassa:

- **Successful payment**: `4111111111111111`
- **Declined payment**: `4000000000000002`
- **3-D Secure**: `4000000000000010`

Use any future expiry date and any CVC.

## Step 5: Payment Flow

```
User → Bot → Out of Credits → Inline Buttons → Invoice → Payment → Success
```

### What happens:

1. **User runs out of credits** → Bot shows payment buttons
2. **User clicks button** → Bot sends Telegram invoice
3. **User pays** → Telegram processes payment
4. **Payment success** → Bot adds credits automatically
5. **User continues** → Can analyze more photos

## Step 6: Production Deployment

1. **Update environment** with production tokens
2. **Deploy bot** to your server
3. **Test payment flow** in production
4. **Monitor logs** for any issues

## Troubleshooting

### Common Issues:

1. **"Payment provider not configured"**:
   - Check `YOOKASSA_PROVIDER_TOKEN` in `.env`
   - Verify token is correct from BotFather
   - Restart bot after updating environment

2. **"Payment validation failed"**:
   - Check YooKassa credentials are correct
   - Verify shop is active and configured for Telegram
   - Check payment amounts match your plans

3. **"Invoice creation failed"**:
   - Verify BotFather payment setup is complete
   - Check YooKassa shop allows Telegram payments
   - Ensure provider token is from BotFather, not YooKassa dashboard

4. **"Credits not added after payment"**:
   - Check bot logs for payment processing errors
   - Verify Supabase connection is working
   - Check `add_credits` function in logs

### Log Monitoring:

Check these logs for debugging:
- Bot startup: `api.c0r.ai/app/bot.py`
- Payment processing: `api.c0r.ai/app/handlers/payments.py`
- Credit management: `common/supabase_client.py`

## Payment Plans Configuration

Current plans in `api.c0r.ai/app/handlers/payments.py`:

```python
PAYMENT_PLANS = {
    "basic": {
        "title": "Basic Plan",
        "description": "20 credits for food analysis",
        "price": 9900,  # 99 RUB in kopecks
        "credits": 20,
        "currency": "RUB"
    },
    "pro": {
        "title": "Pro Plan", 
        "description": "100 credits for food analysis",
        "price": 39900,  # 399 RUB in kopecks
        "credits": 100,
        "currency": "RUB"
    }
}
```

**Note**: Prices are in kopecks (1 RUB = 100 kopecks)

## Security Considerations

1. **Environment Variables**: Never commit `.env` files
2. **Provider Token**: Keep secure, it's tied to your bot
3. **Validation**: Always validate payments in `pre_checkout_query`
4. **Logging**: Log all payment events for monitoring
5. **Error Handling**: Graceful error handling for payment failures

## Commands Available

- `/start` - Check credits and welcome message
- `/help` - Show help with commands
- `/status` - Show account status and credits
- `/buy` - Show payment options
- Send photo - Analyze food (or show payment if no credits)

## Benefits of Telegram Payments

✅ **In-app experience** - Users never leave Telegram
✅ **Native UI** - Familiar Telegram payment interface  
✅ **Security** - Telegram handles payment processing
✅ **Multiple providers** - Easy to switch payment providers
✅ **Mobile optimized** - Works perfectly on mobile devices
✅ **No redirects** - Seamless user experience

## Support

For Telegram Payments issues:
- [Telegram Bot API Documentation](https://core.telegram.org/bots/payments)
- [BotFather Help](https://t.me/BotFather)

For YooKassa issues:
- [YooKassa Documentation](https://yookassa.ru/developers)
- [YooKassa Support](https://yookassa.ru/support) 