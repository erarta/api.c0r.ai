# Environment Configuration Guide

## Quick Setup

### Development Environment (Local Docker)
```bash
# Copy development template
cp .env.example .env

# OR use the switching script
./scripts/switch-env.sh dev
```

**Development URLs:**
- `ML_SERVICE_URL=http://ml:8001`
- `PAY_SERVICE_URL=http://pay:8002`

### Production Environment (AWS)
```bash
# Copy production template
cp .env.production.example .env

# OR use the switching script
./scripts/switch-env.sh prod
```

**Production URLs:**
- `ML_SERVICE_URL=https://ml.c0r.ai`
- `PAY_SERVICE_URL=https://pay.c0r.ai`

## Environment Variables

### Required for Both Environments
```bash
TELEGRAM_BOT_TOKEN=your_telegram_token
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
OPENAI_API_KEY=your_openai_key
INTERNAL_API_TOKEN=your_strong_random_token
```

### Production-Only Variables
```bash
YOOKASSA_SHOP_ID=your_yookassa_shop_id
YOOKASSA_SECRET_KEY=your_yookassa_secret_key
YOOKASSA_PROVIDER_TOKEN=your_yookassa_provider_token
ENVIRONMENT=production
DEBUG=false
```

## Switching Between Environments

### Using the Script (Recommended)
```bash
# Switch to development
./scripts/switch-env.sh dev

# Switch to production
./scripts/switch-env.sh prod
```

### Manual Configuration
Edit `.env` file and change service URLs:

**For development:**
```bash
ML_SERVICE_URL=http://ml:8001
PAY_SERVICE_URL=http://pay:8002
```

**For production:**
```bash
ML_SERVICE_URL=https://ml.c0r.ai
PAY_SERVICE_URL=https://pay.c0r.ai
```

## Deployment Checklist

### Before Production Deployment
- [ ] DNS records configured for api/ml/pay.c0r.ai
- [ ] SSL certificates obtained
- [ ] Production environment variables set
- [ ] Service URLs switched to production domains
- [ ] GitHub secrets configured for CI/CD

### After Deployment
- [ ] Test all service endpoints
- [ ] Verify Telegram bot functionality
- [ ] Check ML service responses
- [ ] Test payment integration

## Troubleshooting

### Common Issues
1. **Service URLs not updated**: Use `./scripts/switch-env.sh prod`
2. **SSL certificate errors**: Ensure certbot is configured properly
3. **DNS resolution**: Check A records point to correct AWS EC2 IP
4. **Service communication**: Verify nginx proxy configuration

### Health Checks
```bash
# Check service status
curl https://api.c0r.ai/
curl https://ml.c0r.ai/
curl https://pay.c0r.ai/

# Check current environment
grep -E "^(ML_SERVICE_URL|PAY_SERVICE_URL)" .env
``` 