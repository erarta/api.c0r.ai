# YooKassa Payment Integration Setup Guide

This guide will help you set up YooKassa payment processing for your c0r.ai bot.

## Prerequisites

1. **YooKassa Account**: Register at [yookassa.ru](https://yookassa.ru)
2. **Shop Configuration**: Set up your shop in YooKassa dashboard
3. **API Access**: Get your Shop ID and Secret Key

## Step 1: YooKassa Dashboard Configuration

1. **Create a Shop**:
   - Go to YooKassa dashboard
   - Create a new shop or use existing one
   - Note your `Shop ID` (found in shop settings)

2. **Generate API Keys**:
   - Go to Settings → API Keys
   - Generate a new Secret Key
   - Copy both `Shop ID` and `Secret Key`

3. **Configure Webhook**:
   - Go to Settings → Webhooks
   - Add webhook URL: `https://pay.c0r.ai/webhook/yookassa`
   - Select events: `payment.succeeded`, `payment.canceled`
   - Save webhook configuration

## Step 2: Environment Variables

Add these variables to your `.env` file:

```bash
# YooKassa Configuration
YOOKASSA_SHOP_ID=your_shop_id_here
YOOKASSA_SECRET_KEY=your_secret_key_here
```

## Step 3: Payment Plans Configuration

Current plans are defined in `pay.c0r.ai/app/yookassa/config.py`:

```python
PLANS_YOOKASSA = {
    "basic": {
        "name": "Basic",
        "count": 20,
        "amount": 9900,  # 99 RUB in kopecks
        "description": "20 credits for food analysis",
        "recurring": False
    },
    "pro": {
        "name": "Pro", 
        "count": 100,
        "amount": 39900,  # 399 RUB in kopecks
        "description": "100 credits per month (subscription)",
        "recurring": True,
        "interval": "month"
    }
}
```

**Note**: Amounts are in kopecks (1 RUB = 100 kopecks)

## Step 4: Testing

### Test Payment Flow:

1. **Start the bot** and send a photo
2. **Use up free credits** (default: 3 credits)
3. **Click payment link** when out of credits
4. **Complete test payment** in YooKassa
5. **Verify credits** are added to your account

### Test Webhook:

1. **Check logs** in payment service for webhook events
2. **Verify** credits are added after successful payment
3. **Test** payment success page redirect

## Step 5: Production Deployment

1. **Update webhook URL** in YooKassa dashboard to your production domain
2. **Switch to production credentials** (if using test credentials)
3. **Test** full payment flow in production
4. **Monitor** logs for any issues

## Troubleshooting

### Common Issues:

1. **"YooKassa credentials not configured"**:
   - Check your `.env` file has correct `YOOKASSA_SHOP_ID` and `YOOKASSA_SECRET_KEY`
   - Restart the payment service after updating environment variables

2. **Webhook not receiving events**:
   - Verify webhook URL is correct in YooKassa dashboard
   - Check that your server is accessible from internet
   - Ensure webhook endpoint is not blocked by firewall

3. **Payment creation fails**:
   - Check YooKassa API credentials are valid
   - Verify shop is active and configured correctly
   - Check logs for specific error messages

4. **Credits not added after payment**:
   - Check webhook is configured correctly
   - Verify API service is accessible from payment service
   - Check `INTERNAL_API_TOKEN` is set correctly

### Log Monitoring:

Monitor these log files for debugging:
- Payment service: `pay.c0r.ai/app/main.py` logs
- API service: `api.c0r.ai/app/main.py` logs
- YooKassa client: `pay.c0r.ai/app/yookassa/client.py` logs

## Security Considerations

1. **Environment Variables**: Never commit `.env` files to version control
2. **API Keys**: Keep YooKassa credentials secure and rotate regularly
3. **Webhook Validation**: Consider implementing webhook signature validation
4. **HTTPS**: Always use HTTPS for webhook endpoints
5. **Rate Limiting**: Implement rate limiting on webhook endpoints

## Payment Flow Summary

```
User → Bot → Out of Credits → Payment Service → YooKassa → Payment Page
                                      ↓
User Pays → YooKassa → Webhook → Payment Service → API Service → Credits Added
```

## Support

For YooKassa-specific issues:
- [YooKassa Documentation](https://yookassa.ru/developers)
- [YooKassa Support](https://yookassa.ru/support)

For integration issues:
- Check application logs
- Review this setup guide
- Verify environment configuration 