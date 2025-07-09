# YooKassa Webhook Configuration Guide

## Quick Setup Steps

### Step 1: Login to YooKassa Dashboard
1. Go to [yookassa.ru](https://yookassa.ru)
2. Login with your credentials
3. Select your shop

### Step 2: Navigate to Webhooks
1. In the left sidebar, click **"Настройки"** (Settings)
2. Click **"Уведомления"** (Notifications) or **"Webhooks"**
3. Click **"Добавить webhook"** (Add webhook)

### Step 3: Configure Webhook
1. **URL**: Enter your webhook URL:
   ```
   https://pay.c0r.ai/webhook/yookassa
   ```
   
2. **Events to listen for**:
   - ✅ `payment.succeeded` (Payment successful)
   - ✅ `payment.canceled` (Payment canceled)
   - ✅ `payment.waiting_for_capture` (Payment waiting for capture)
   
3. **HTTP Method**: Select `POST`

4. **Content Type**: Select `application/json`

### Step 4: Test Webhook
1. Click **"Тест"** (Test) button
2. Select `payment.succeeded` event
3. Click **"Отправить"** (Send)
4. Check your server logs to verify webhook received

### Step 5: Activate Webhook
1. Click **"Сохранить"** (Save)
2. Webhook should appear in your webhooks list
3. Status should be **"Активен"** (Active)

## Important Notes

- **URL must be HTTPS** - HTTP webhooks are not supported
- **Server must be accessible** from internet
- **Response time** should be under 10 seconds
- **Return HTTP 200** for successful webhook processing

## Webhook Payload Example

```json
{
  "type": "notification",
  "event": "payment.succeeded",
  "object": {
    "id": "24b94598-000f-5000-9000-1b68e7b15f3f",
    "status": "succeeded",
    "paid": true,
    "amount": {
      "value": "99.00",
      "currency": "RUB"
    },
    "created_at": "2024-07-09T14:05:02.846Z",
    "description": "Basic Plan",
    "metadata": {
      "user_id": "123456789",
      "plan_id": "basic",
      "credits_count": "20"
    }
  }
}
```

## Testing Webhook

### Using curl:
```bash
curl -X POST https://pay.c0r.ai/webhook/yookassa \
  -H "Content-Type: application/json" \
  -d '{
    "type": "notification",
    "event": "payment.succeeded",
    "object": {
      "id": "test-payment-id",
      "status": "succeeded",
      "amount": {"value": "99.00", "currency": "RUB"},
      "metadata": {
        "user_id": "123456789",
        "plan_id": "basic", 
        "credits_count": "20"
      }
    }
  }'
```

### Expected Response:
```json
{"status": "ok"}
```

## Troubleshooting

### Common Issues:

1. **Webhook not receiving events**:
   - Check URL is correct and accessible
   - Verify HTTPS certificate is valid
   - Check firewall settings

2. **Webhook returns error**:
   - Check server logs for detailed error
   - Verify webhook endpoint is working
   - Test with curl command above

3. **Events not processed**:
   - Check webhook payload format
   - Verify event type is `payment.succeeded`
   - Check metadata contains required fields

### Webhook Logs:
Monitor these files for debugging:
- Payment service logs: `pay.c0r.ai/app/main.py`
- Webhook processing: Look for "YooKassa webhook received"
- Credit addition: Check "Added credits to user" messages

## Security

- Webhook URL should be kept private
- Consider implementing webhook signature validation
- Always validate payment data before processing
- Log all webhook events for audit trail 