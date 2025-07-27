# MODERA.FASHION - User Setup Instructions

**Date:** 2025-01-27  
**Purpose:** Complete instructions for what the user needs to create and setup  
**Estimated Setup Time:** 4-6 hours  

## Overview

This document provides step-by-step instructions for setting up all external services and accounts required for MODERA.FASHION deployment. Follow these instructions before beginning the technical implementation.

## Required Accounts and Services

### 1. Domain and DNS Management

#### Cloudflare Account Setup
**Purpose:** Domain registration, DNS management, CDN, and R2 storage

**Steps:**
1. **Create Cloudflare Account**
   - Go to https://cloudflare.com
   - Sign up with business email
   - Verify email address

2. **Register Domain**
   - Navigate to "Domain Registration"
   - Search for "modera.fashion"
   - Complete purchase ($10-15/year)
   - Enable domain privacy protection

3. **Configure DNS Management**
   - Add domain to Cloudflare
   - Update nameservers at registrar
   - Wait for DNS propagation (24-48 hours)

4. **Set up R2 Storage**
   - Navigate to R2 Object Storage
   - Create bucket: `modera-fashion-storage`
   - Configure CORS settings
   - Generate R2 API tokens

**Required Information to Save:**
```
Domain: modera.fashion
Cloudflare Account ID: [from dashboard]
R2 Access Key ID: [from API tokens]
R2 Secret Access Key: [from API tokens]
R2 Endpoint: [from R2 dashboard]
```

### 2. Cloud Infrastructure

#### AWS Account Setup
**Purpose:** EC2 instances, load balancing, auto-scaling, Redis cache

**Steps:**
1. **Create AWS Account**
   - Go to https://aws.amazon.com
   - Sign up with business email
   - Add payment method
   - Complete identity verification

2. **Set up Billing Alerts**
   - Go to AWS Billing Dashboard
   - Create budget: $2,000/month
   - Set up alerts at 50%, 80%, 100%

3. **Create IAM User for Deployment**
   - Go to IAM Console
   - Create user: `modera-deployment`
   - Attach policies: EC2FullAccess, ElastiCacheFullAccess, ApplicationLoadBalancerFullAccess
   - Generate access keys

4. **Set up Key Pair**
   - Go to EC2 Console
   - Create key pair: `modera-fashion-key`
   - Download .pem file securely

**Required Information to Save:**
```
AWS Account ID: [12-digit number]
AWS Access Key ID: [from IAM user]
AWS Secret Access Key: [from IAM user]
AWS Region: eu-west-1 (or preferred region)
Key Pair Name: modera-fashion-key
```

### 3. Database and Backend Services

#### Supabase Account Setup
**Purpose:** PostgreSQL database, authentication, real-time features

**Steps:**
1. **Create Supabase Account**
   - Go to https://supabase.com
   - Sign up with GitHub or email
   - Verify email address

2. **Create New Project**
   - Click "New Project"
   - Project name: `modera-fashion-prod`
   - Database password: Generate strong password
   - Region: Europe (eu-west-1)
   - Plan: Pro ($25/month)

3. **Configure Project Settings**
   - Go to Settings > API
   - Copy project URL and API keys
   - Go to Settings > Database
   - Note connection string

4. **Set up Authentication**
   - Go to Authentication > Settings
   - Site URL: `https://modera.fashion`
   - Add redirect URLs for auth callbacks

**Required Information to Save:**
```
Supabase Project URL: https://[project-id].supabase.co
Supabase Anon Key: [public API key]
Supabase Service Role Key: [private API key]
Database Password: [strong password]
```

### 4. Telegram Bot Setup

#### BotFather Configuration
**Purpose:** Create and configure Telegram bot

**Steps:**
1. **Create Bot with BotFather**
   - Open Telegram and search for @BotFather
   - Send `/newbot` command
   - Bot name: `MODERA.FASHION`
   - Bot username: `ModeraFashionBot` (or available alternative)
   - Save the bot token securely

2. **Configure Bot Settings**
   - Send `/setdescription` to BotFather
   - Description: "AI-powered virtual try-on and personal styling assistant"
   - Send `/setabouttext`
   - About: "Virtual fashion fitting and AI styling in Telegram"

3. **Set Bot Commands**
   - Send `/setcommands` to BotFather
   - Commands list:
   ```
   start - Start using MODERA.FASHION
   help - Get help and instructions
   profile - View your profile
   credits - Check credit balance
   settings - Change language and preferences
   ```

4. **Configure Bot Image**
   - Send `/setuserpic` to BotFather
   - Upload bot profile picture (fashion-related)

**Required Information to Save:**
```
Bot Token: [from BotFather]
Bot Username: @ModeraFashionBot
Bot ID: [numeric ID from token]
```

### 5. AI Service APIs

#### OpenAI Account Setup
**Purpose:** DALL-E 3 for virtual try-on, GPT-4 Vision for style analysis

**Steps:**
1. **Create OpenAI Account**
   - Go to https://platform.openai.com
   - Sign up with business email
   - Verify phone number

2. **Set up Billing**
   - Go to Billing section
   - Add payment method
   - Set usage limits: $1,000/month initially
   - Enable usage notifications

3. **Generate API Key**
   - Go to API Keys section
   - Create new secret key
   - Name: `modera-fashion-prod`
   - Save key securely (cannot be viewed again)

4. **Request Model Access**
   - Ensure access to DALL-E 3
   - Ensure access to GPT-4 Vision Preview
   - Contact support if access needed

**Required Information to Save:**
```
OpenAI API Key: sk-[your-key]
Organization ID: [if applicable]
Usage Limit: $1,000/month
```

#### Google AI (Gemini) Setup
**Purpose:** Gemini Pro Vision for image analysis and validation

**Steps:**
1. **Create Google Cloud Account**
   - Go to https://cloud.google.com
   - Sign up with business email
   - Complete billing setup

2. **Enable Gemini API**
   - Go to Google AI Studio: https://makersuite.google.com
   - Create new project
   - Enable Gemini Pro Vision API

3. **Generate API Key**
   - Go to API Keys section
   - Create new API key
   - Restrict key to Gemini APIs only
   - Save key securely

4. **Set up Billing and Quotas**
   - Set monthly budget: $500
   - Configure usage alerts
   - Review rate limits

**Required Information to Save:**
```
Gemini API Key: [your-api-key]
Project ID: [google-cloud-project-id]
Usage Limit: $500/month
```

### 6. Payment Processing

#### YooKassa Setup (Russian Market)
**Purpose:** Process payments in rubles for Russian users

**Steps:**
1. **Create YooKassa Account**
   - Go to https://yookassa.ru
   - Register business account
   - Complete business verification (may take 3-5 days)
   - Provide required business documents

2. **Configure Shop Settings**
   - Shop name: `MODERA.FASHION`
   - Description: `AI-powered fashion styling service`
   - Website: `https://modera.fashion`
   - Category: `Digital services`

3. **Set up API Access**
   - Go to Settings > API
   - Generate API keys
   - Configure webhook URL: `https://pay.modera.fashion/webhook/yookassa`
   - Set up webhook secret

4. **Configure Payment Methods**
   - Enable bank cards
   - Enable SberPay
   - Enable YooMoney
   - Set up commission rates

**Required Information to Save:**
```
YooKassa Shop ID: [numeric ID]
YooKassa Secret Key: [API secret]
YooKassa Webhook Secret: [webhook secret]
Commission Rate: [percentage]
```

#### Stripe Setup (International Market)
**Purpose:** Process payments in USD/EUR for international users

**Steps:**
1. **Create Stripe Account**
   - Go to https://stripe.com
   - Sign up with business email
   - Complete business verification
   - Provide tax information

2. **Configure Account Settings**
   - Business name: `MODERA.FASHION`
   - Website: `https://modera.fashion`
   - Business type: `Software/SaaS`
   - Enable international payments

3. **Set up API Keys**
   - Go to Developers > API Keys
   - Copy publishable and secret keys
   - Generate restricted keys for production

4. **Configure Webhooks**
   - Go to Developers > Webhooks
   - Add endpoint: `https://pay.modera.fashion/webhook/stripe`
   - Select events: payment_intent.succeeded, payment_intent.payment_failed
   - Generate webhook secret

**Required Information to Save:**
```
Stripe Publishable Key: pk_live_[your-key]
Stripe Secret Key: sk_live_[your-key]
Stripe Webhook Secret: whsec_[your-secret]
Account ID: acct_[your-account]
```

### 7. Monitoring and Analytics

#### Sentry Setup
**Purpose:** Error tracking and performance monitoring

**Steps:**
1. **Create Sentry Account**
   - Go to https://sentry.io
   - Sign up with business email
   - Choose appropriate plan

2. **Create Projects**
   - Create project: `modera-fashion-api`
   - Create project: `modera-fashion-ml`
   - Create project: `modera-fashion-pay`
   - Platform: Node.js for each

3. **Configure Alerts**
   - Set up error rate alerts
   - Configure performance alerts
   - Set up Slack/email notifications

**Required Information to Save:**
```
Sentry DSN (API): [your-api-dsn]
Sentry DSN (ML): [your-ml-dsn]
Sentry DSN (Pay): [your-pay-dsn]
Organization Slug: [your-org]
```

## Environment Variables Setup

### Create Environment Files

#### API Service Environment (.env.prod)
```bash
# Application
NODE_ENV=production
PORT=8000
DOMAIN=https://modera.fashion

# Database
SUPABASE_URL=https://[project-id].supabase.co
SUPABASE_ANON_KEY=[your-anon-key]
SUPABASE_SERVICE_ROLE_KEY=[your-service-key]

# Redis
REDIS_URL=redis://[elasticache-endpoint]:6379

# Telegram
TELEGRAM_BOT_TOKEN=[your-bot-token]
TELEGRAM_WEBHOOK_URL=https://api.modera.fashion/webhook/telegram

# Internal Services
ML_SERVICE_URL=http://internal-ml-service:8001
PAY_SERVICE_URL=http://internal-pay-service:8002
INTERNAL_API_TOKEN=[generate-random-token]

# Monitoring
SENTRY_DSN=[your-api-sentry-dsn]
LOG_LEVEL=info
```

#### ML Service Environment (.env.prod)
```bash
# Application
NODE_ENV=production
PORT=8001

# AI APIs
OPENAI_API_KEY=[your-openai-key]
GEMINI_API_KEY=[your-gemini-key]

# Storage
CLOUDFLARE_R2_ENDPOINT=[your-r2-endpoint]
CLOUDFLARE_R2_ACCESS_KEY=[your-r2-access-key]
CLOUDFLARE_R2_SECRET_KEY=[your-r2-secret-key]
CLOUDFLARE_R2_BUCKET=modera-fashion-storage

# Database
SUPABASE_URL=https://[project-id].supabase.co
SUPABASE_SERVICE_ROLE_KEY=[your-service-key]

# Cache
REDIS_URL=redis://[elasticache-endpoint]:6379

# Monitoring
SENTRY_DSN=[your-ml-sentry-dsn]
```

#### Payment Service Environment (.env.prod)
```bash
# Application
NODE_ENV=production
PORT=8002

# YooKassa
YOOKASSA_SHOP_ID=[your-shop-id]
YOOKASSA_SECRET_KEY=[your-yookassa-secret]
YOOKASSA_WEBHOOK_SECRET=[your-webhook-secret]

# Stripe
STRIPE_SECRET_KEY=[your-stripe-secret]
STRIPE_WEBHOOK_SECRET=[your-stripe-webhook-secret]
STRIPE_PUBLISHABLE_KEY=[your-stripe-publishable]

# Database
SUPABASE_URL=https://[project-id].supabase.co
SUPABASE_SERVICE_ROLE_KEY=[your-service-key]

# Monitoring
SENTRY_DSN=[your-pay-sentry-dsn]
```

## Security Setup

### SSL Certificate Configuration

#### Let's Encrypt via Cloudflare
**Steps:**
1. **Enable Cloudflare SSL**
   - Go to SSL/TLS section in Cloudflare
   - Set encryption mode to "Full (strict)"
   - Enable "Always Use HTTPS"

2. **Generate Origin Certificate**
   - Go to SSL/TLS > Origin Server
   - Create certificate for *.modera.fashion
   - Download certificate and private key
   - Install on your servers

3. **Configure HSTS**
   - Enable HTTP Strict Transport Security
   - Set max-age to 1 year
   - Include subdomains

### Secrets Management

#### AWS Secrets Manager Setup
**Steps:**
1. **Create Secrets**
   - Go to AWS Secrets Manager
   - Create secret: `modera/production/database-credentials`
   - Create secret: `modera/production/api-keys`
   - Create secret: `modera/production/payment-credentials`

2. **Configure Access Policies**
   - Create IAM role for EC2 instances
   - Grant access to specific secrets only
   - Enable rotation where applicable

## Pre-Deployment Checklist

### Account Verification Status
- [ ] Cloudflare account active and domain registered
- [ ] AWS account set up with billing alerts
- [ ] Supabase project created and configured
- [ ] Telegram bot created and configured
- [ ] OpenAI account with API access and billing
- [ ] Google AI account with Gemini API access
- [ ] YooKassa business account verified (3-5 days)
- [ ] Stripe account verified and configured
- [ ] Sentry projects created and configured

### API Keys and Credentials Collected
- [ ] All environment variables documented
- [ ] API keys tested and working
- [ ] Webhook URLs configured
- [ ] SSL certificates generated
- [ ] Secrets stored securely

### Service Limits and Quotas
- [ ] OpenAI usage limits set ($1,000/month)
- [ ] Gemini API quotas configured ($500/month)
- [ ] AWS billing alerts active ($2,000/month)
- [ ] Payment processor limits understood
- [ ] Cloudflare R2 storage limits noted

## Testing Account Setup

### Create Test Accounts
**Purpose:** Test all integrations before production

**Steps:**
1. **Telegram Test Bot**
   - Create separate test bot with BotFather
   - Use for development and testing
   - Configure with test webhook URLs

2. **Payment Test Accounts**
   - YooKassa: Use test shop credentials
   - Stripe: Use test API keys
   - Test with sandbox environments

3. **AI Service Test Limits**
   - Set lower limits for testing
   - Use test API keys where available
   - Monitor usage during development

## Support and Documentation

### Important Contacts and Resources

#### Technical Support
- **Cloudflare Support:** https://support.cloudflare.com
- **AWS Support:** https://aws.amazon.com/support/
- **Supabase Support:** https://supabase.com/support
- **OpenAI Support:** https://help.openai.com
- **Stripe Support:** https://support.stripe.com

#### Documentation Links
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **OpenAI API Docs:** https://platform.openai.com/docs
- **Gemini API Docs:** https://ai.google.dev/docs
- **YooKassa API:** https://yookassa.ru/developers
- **Stripe API:** https://stripe.com/docs/api

### Emergency Contacts
**Save these for production issues:**
- AWS Support Phone: [your region support number]
- Cloudflare Emergency: [enterprise support if applicable]
- Payment Processor Emergency: [24/7 support numbers]

## Cost Estimation Summary

### Monthly Service Costs
```
Domain Registration: $1/month (annual)
Cloudflare Pro: $20/month
AWS Infrastructure: $380/month (estimated)
Supabase Pro: $25/month
OpenAI API: $8,000/month (estimated usage)
Google Gemini API: $2,000/month (estimated usage)
Stripe Processing: 2.9% + $0.30 per transaction
YooKassa Processing: 2.8% + ₽15 per transaction
Sentry: $26/month (team plan)

Total Fixed Costs: ~$450/month
Total Variable Costs: ~$10,000/month (AI + payments)
Total Estimated: ~$10,450/month
```

### Setup Time Estimation
```
Account Creation: 2-3 hours
Service Configuration: 2-3 hours
API Key Generation: 1 hour
Testing and Validation: 1-2 hours
Documentation: 1 hour

Total Setup Time: 7-10 hours
```

## Final Validation

### Pre-Implementation Checklist
- [ ] All accounts created and verified
- [ ] All API keys generated and tested
- [ ] All environment variables documented
- [ ] All webhook URLs configured
- [ ] All billing and limits set up
- [ ] All security measures implemented
- [ ] All test accounts created
- [ ] All documentation saved securely

### Ready for Implementation
Once all items above are completed, you're ready to begin the technical implementation following the other planning documents in this rebranding package.

---

**Setup Summary:** This comprehensive setup ensures all external dependencies are properly configured before beginning development. The estimated 7-10 hours of setup time is crucial for smooth implementation and deployment of MODERA.FASHION.