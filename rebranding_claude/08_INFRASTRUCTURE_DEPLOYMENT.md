# MODERA.FASHION - Infrastructure & Deployment Plan

**Date:** 2025-01-27  
**Purpose:** Complete infrastructure setup and deployment strategy for MODERA.FASHION  
**Domain:** https://modera.fashion  

## Infrastructure Overview

### Service Architecture Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODERA.FASHION Infrastructure                │
└─────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
         ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
         │   AWS EC2       │ │   Supabase      │ │  Cloudflare     │
         │                 │ │                 │ │                 │
         │ • API Service   │ │ • PostgreSQL    │ │ • R2 Storage    │
         │ • ML Service    │ │ • Auth          │ │ • CDN           │
         │ • Pay Service   │ │ • Real-time     │ │ • DNS           │
         │ • Load Balancer │ │ • Edge Functions│ │ • SSL/TLS       │
         │ • Redis Cache   │ │ • Backups       │ │ • DDoS Protection│
         └─────────────────┘ └─────────────────┘ └─────────────────┘
                  │                    │                    │
                  └────────────────────┼────────────────────┘
                                       │
                          ┌─────────────────┐
                          │  External APIs  │
                          │                 │
                          │ • OpenAI        │
                          │ • Gemini        │
                          │ • YooKassa      │
                          │ • Stripe        │
                          │ • E-commerce    │
                          └─────────────────┘
```

## AWS Infrastructure Setup

### EC2 Instance Configuration

#### Production Environment
```yaml
Instance Type: t3.large
vCPUs: 2
Memory: 8 GB
Storage: 100 GB SSD (gp3)
Network: Enhanced networking enabled
Region: eu-west-1 (Ireland) for international, eu-central-1 (Frankfurt) for Russian users
```

#### Security Groups
```yaml
Inbound Rules:
  - Port 80 (HTTP): 0.0.0.0/0
  - Port 443 (HTTPS): 0.0.0.0/0
  - Port 22 (SSH): Your IP only
  - Port 8000 (API Service): Load balancer only
  - Port 8001 (ML Service): Load balancer only
  - Port 8002 (Pay Service): Load balancer only

Outbound Rules:
  - All traffic: 0.0.0.0/0
```

#### Load Balancer Configuration
```yaml
Type: Application Load Balancer (ALB)
Scheme: Internet-facing
IP address type: IPv4

Target Groups:
  - api-service-tg: Port 8000, Health check: /health
  - ml-service-tg: Port 8001, Health check: /health
  - pay-service-tg: Port 8002, Health check: /health

Listeners:
  - Port 80: Redirect to HTTPS
  - Port 443: Forward to appropriate target group based on path
```

### Auto Scaling Configuration

#### Auto Scaling Groups
```yaml
API Service ASG:
  Min Size: 1
  Max Size: 5
  Desired Capacity: 2
  Health Check Type: ELB
  Health Check Grace Period: 300 seconds

ML Service ASG:
  Min Size: 1
  Max Size: 3
  Desired Capacity: 1
  Health Check Type: ELB
  Health Check Grace Period: 600 seconds

Pay Service ASG:
  Min Size: 1
  Max Size: 2
  Desired Capacity: 1
  Health Check Type: ELB
  Health Check Grace Period: 300 seconds
```

#### Scaling Policies
```yaml
Scale Up Policy:
  Metric: CPU Utilization > 70% for 2 consecutive periods
  Action: Add 1 instance
  Cooldown: 300 seconds

Scale Down Policy:
  Metric: CPU Utilization < 30% for 5 consecutive periods
  Action: Remove 1 instance
  Cooldown: 300 seconds
```

### Redis Cache Setup

#### ElastiCache Configuration
```yaml
Engine: Redis 7.0
Node Type: cache.t3.micro (production: cache.r6g.large)
Number of Nodes: 1 (production: 3 with replication)
Subnet Group: Private subnets
Security Group: Allow access from EC2 instances only
Backup: Automatic backups enabled
```

## Supabase Configuration

### Database Setup

#### Project Configuration
```yaml
Project Name: modera-fashion-prod
Region: Europe (eu-west-1)
Plan: Pro ($25/month)
Database Version: PostgreSQL 15
```

#### Database Settings
```yaml
Connection Pooling: Enabled (PgBouncer)
Max Connections: 100
Statement Timeout: 30 seconds
Idle Timeout: 10 minutes
```

#### Row Level Security (RLS)
```sql
-- Enable RLS on all user-facing tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE fashion_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE virtual_tryons ENABLE ROW LEVEL SECURITY;
ALTER TABLE style_analyses ENABLE ROW LEVEL SECURITY;

-- Create policies for user data access
CREATE POLICY "Users can access own data" ON users
  FOR ALL USING (telegram_id = current_setting('app.current_user_id')::bigint);

CREATE POLICY "Users can access own sessions" ON fashion_sessions
  FOR ALL USING (user_id = current_setting('app.current_user_id')::bigint);
```

#### Backup Strategy
```yaml
Automatic Backups: Daily at 2:00 AM UTC
Retention Period: 30 days
Point-in-Time Recovery: Enabled
Manual Backups: Before major deployments
```

### Authentication Configuration

#### Supabase Auth Settings
```yaml
Site URL: https://modera.fashion
Redirect URLs: 
  - https://modera.fashion/auth/callback
  - https://api.modera.fashion/auth/callback

JWT Settings:
  JWT expiry: 3600 seconds (1 hour)
  Refresh token expiry: 2592000 seconds (30 days)

Email Settings:
  SMTP Provider: Custom SMTP
  From Email: noreply@modera.fashion
```

## Cloudflare Configuration

### Domain and DNS Setup

#### Domain Registration
```yaml
Domain: modera.fashion
Registrar: Cloudflare Registrar
DNS Management: Cloudflare DNS
```

#### DNS Records
```yaml
A Records:
  @ (root): Points to AWS Load Balancer
  api: Points to AWS Load Balancer
  ml: Points to AWS Load Balancer  
  pay: Points to AWS Load Balancer

CNAME Records:
  www: Points to modera.fashion

MX Records:
  @: Points to email provider (Google Workspace or similar)

TXT Records:
  @: SPF, DKIM, DMARC records for email authentication
```

### R2 Storage Configuration

#### Bucket Setup
```yaml
Bucket Name: modera-fashion-storage
Region: Auto (global distribution)
Storage Class: Standard

Directories:
  /user-uploads/clothing/
  /user-uploads/persons/
  /generated-images/tryons/
  /generated-images/styles/
  /temp-processing/
```

#### Access Policies
```yaml
Public Access: Disabled (all access via signed URLs)
CORS Policy:
  - Origin: https://modera.fashion
  - Methods: GET, PUT, POST
  - Headers: Content-Type, Authorization
  - Max Age: 3600

Lifecycle Rules:
  - Delete temp files after 24 hours
  - Move old generated images to cheaper storage after 90 days
```

### CDN and Security

#### Cloudflare Settings
```yaml
SSL/TLS: Full (strict)
Always Use HTTPS: Enabled
HTTP Strict Transport Security (HSTS): Enabled
Minimum TLS Version: 1.2

Security Level: Medium
Bot Fight Mode: Enabled
DDoS Protection: Enabled

Caching:
  Browser Cache TTL: 4 hours
  Edge Cache TTL: 2 hours
  Always Online: Enabled
```

## Environment Configuration

### Production Environment Variables

#### API Service (.env)
```bash
# Application
NODE_ENV=production
PORT=8000
DOMAIN=https://modera.fashion

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# Redis
REDIS_URL=redis://your-elasticache-endpoint:6379

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_WEBHOOK_URL=https://api.modera.fashion/webhook/telegram

# Internal Services
ML_SERVICE_URL=http://internal-ml-service:8001
PAY_SERVICE_URL=http://internal-pay-service:8002
INTERNAL_API_TOKEN=your-internal-token

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=info
```

#### ML Service (.env)
```bash
# Application
NODE_ENV=production
PORT=8001

# AI APIs
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key

# Storage
CLOUDFLARE_R2_ENDPOINT=your-r2-endpoint
CLOUDFLARE_R2_ACCESS_KEY=your-access-key
CLOUDFLARE_R2_SECRET_KEY=your-secret-key
CLOUDFLARE_R2_BUCKET=modera-fashion-storage

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# Cache
REDIS_URL=redis://your-elasticache-endpoint:6379

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

#### Payment Service (.env)
```bash
# Application
NODE_ENV=production
PORT=8002

# YooKassa
YOOKASSA_SHOP_ID=your-shop-id
YOOKASSA_SECRET_KEY=your-secret-key
YOOKASSA_WEBHOOK_SECRET=your-webhook-secret

# Stripe
STRIPE_SECRET_KEY=your-stripe-secret
STRIPE_WEBHOOK_SECRET=your-webhook-secret
STRIPE_PUBLISHABLE_KEY=your-publishable-key

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

## Docker Configuration

### Multi-Service Docker Compose

#### docker-compose.prod.yml
```yaml
version: '3.8'

services:
  api-service:
    build:
      context: ./services/api
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
    env_file:
      - ./services/api/.env.prod
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  ml-service:
    build:
      context: ./services/ml
      dockerfile: Dockerfile.prod
    ports:
      - "8001:8001"
    environment:
      - NODE_ENV=production
    env_file:
      - ./services/ml/.env.prod
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  pay-service:
    build:
      context: ./services/pay
      dockerfile: Dockerfile.prod
    ports:
      - "8002:8002"
    environment:
      - NODE_ENV=production
    env_file:
      - ./services/pay/.env.prod
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - api-service
      - ml-service
      - pay-service
    restart: unless-stopped

volumes:
  redis_data:
```

### Individual Service Dockerfiles

#### API Service Dockerfile
```dockerfile
# services/api/Dockerfile.prod
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS runtime

RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --chown=nextjs:nodejs . .

USER nextjs

EXPOSE 8000

CMD ["npm", "start"]
```

## Monitoring and Logging

### Application Monitoring

#### Sentry Configuration
```javascript
// Sentry setup for error tracking
import * as Sentry from "@sentry/node";

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
  integrations: [
    new Sentry.Integrations.Http({ tracing: true }),
    new Sentry.Integrations.Express({ app }),
  ],
});
```

#### Health Check Endpoints
```javascript
// Health check implementation
app.get('/health', async (req, res) => {
  const health = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: process.env.SERVICE_NAME,
    version: process.env.npm_package_version,
    checks: {
      database: await checkDatabase(),
      redis: await checkRedis(),
      external_apis: await checkExternalAPIs()
    }
  };
  
  const isHealthy = Object.values(health.checks).every(check => check.status === 'ok');
  res.status(isHealthy ? 200 : 503).json(health);
});
```

### Log Management

#### Structured Logging
```javascript
// Winston logger configuration
import winston from 'winston';

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});
```

### Performance Monitoring

#### Metrics Collection
```javascript
// Prometheus metrics
import client from 'prom-client';

const httpRequestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code']
});

const aiProcessingDuration = new client.Histogram({
  name: 'ai_processing_duration_seconds',
  help: 'Duration of AI processing in seconds',
  labelNames: ['model', 'task_type']
});
```

## Deployment Strategy

### CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test
      - run: npm run lint

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-west-1

      - name: Build and push Docker images
        run: |
          docker build -t modera-api ./services/api
          docker build -t modera-ml ./services/ml
          docker build -t modera-pay ./services/pay
          
          # Push to ECR or Docker Hub
          docker tag modera-api:latest $ECR_REGISTRY/modera-api:latest
          docker push $ECR_REGISTRY/modera-api:latest

      - name: Deploy to EC2
        run: |
          # Deploy using AWS CodeDeploy or direct SSH
          aws deploy create-deployment \
            --application-name modera-fashion \
            --deployment-group-name production \
            --s3-location bucket=modera-deployments,key=latest.zip,bundleType=zip
```

### Blue-Green Deployment

#### Deployment Process
1. **Preparation Phase**
   - Build new version in staging environment
   - Run comprehensive tests
   - Prepare database migrations

2. **Green Environment Setup**
   - Deploy new version to green environment
   - Run health checks
   - Perform smoke tests

3. **Traffic Switch**
   - Update load balancer to route traffic to green
   - Monitor metrics and error rates
   - Keep blue environment running for rollback

4. **Cleanup**
   - After successful deployment, terminate blue environment
   - Update monitoring and alerting

### Database Migration Strategy

#### Migration Process
```bash
# Pre-deployment database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Run migrations
npm run migrate:up

# Verify migration success
npm run migrate:verify

# If migration fails, rollback
npm run migrate:down
```

## Security Configuration

### SSL/TLS Setup

#### Certificate Management
```yaml
Certificate Provider: Let's Encrypt (via Cloudflare)
Certificate Type: Wildcard (*.modera.fashion)
Auto-renewal: Enabled
HSTS: Enabled with 1 year max-age
```

### Firewall Configuration

#### AWS Security Groups
```yaml
Web Tier Security Group:
  Inbound:
    - HTTP (80): 0.0.0.0/0
    - HTTPS (443): 0.0.0.0/0
  Outbound:
    - All traffic to App Tier

App Tier Security Group:
  Inbound:
    - Port 8000-8002: Web Tier only
    - SSH (22): Bastion host only
  Outbound:
    - HTTPS (443): 0.0.0.0/0 (for external APIs)
    - PostgreSQL (5432): Database subnet

Database Tier Security Group:
  Inbound:
    - PostgreSQL (5432): App Tier only
  Outbound:
    - None
```

### Secrets Management

#### AWS Secrets Manager
```yaml
Secrets:
  - modera/production/database-url
  - modera/production/openai-api-key
  - modera/production/telegram-bot-token
  - modera/production/yookassa-credentials
  - modera/production/stripe-credentials

Rotation:
  - Database credentials: 90 days
  - API keys: Manual rotation
  - Bot tokens: Manual rotation
```

## Backup and Disaster Recovery

### Backup Strategy

#### Database Backups
```yaml
Automated Backups:
  - Frequency: Daily at 2:00 AM UTC
  - Retention: 30 days
  - Storage: Supabase managed backups + S3 cross-region

Manual Backups:
  - Before major deployments
  - Before database schema changes
  - Monthly full backups to separate S3 bucket
```

#### File Storage Backups
```yaml
Cloudflare R2 Backup:
  - Cross-region replication: Enabled
  - Versioning: Enabled (30 days)
  - Lifecycle policies: Archive after 90 days
```

### Disaster Recovery Plan

#### Recovery Time Objectives (RTO)
- **Database Recovery:** 4 hours
- **Application Recovery:** 2 hours
- **Full Service Recovery:** 6 hours

#### Recovery Point Objectives (RPO)
- **Database:** 1 hour (point-in-time recovery)
- **File Storage:** 15 minutes (real-time replication)
- **Application State:** 5 minutes (Redis persistence)

#### Recovery Procedures
1. **Database Recovery**
   ```bash
   # Restore from point-in-time backup
   supabase db restore --project-ref $PROJECT_REF --backup-id $BACKUP_ID
   ```

2. **Application Recovery**
   ```bash
   # Deploy from last known good version
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **DNS Failover**
   ```bash
   # Update DNS to point to backup region
   curl -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
     -H "Authorization: Bearer $CF_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{"content":"backup-server-ip"}'
   ```

## Cost Optimization

### Resource Optimization

#### Auto Scaling Policies
- Scale down during low-traffic hours (2 AM - 6 AM UTC)
- Use spot instances for non-critical workloads
- Implement intelligent caching to reduce AI API calls

#### Cost Monitoring
```yaml
AWS Cost Alerts:
  - Monthly budget: $2,000
  - Alert thresholds: 50%, 80%, 100%
  - Notification: Email + Slack

Resource Tagging:
  - Environment: production/staging/development
  - Service: api/ml/pay
  - Owner: team-name
  - Project: modera-fashion
```

### Estimated Monthly Costs

#### Infrastructure Costs
```yaml
AWS EC2 (t3.large x 3): $150/month
AWS Load Balancer: $25/month
AWS ElastiCache (Redis): $50/month
AWS Data Transfer: $100/month
Supabase Pro: $25/month
Cloudflare Pro: $20/month
Domain Registration: $10/month

Total Infrastructure: ~$380/month
```

#### External API Costs
```yaml
OpenAI (DALL-E 3 + GPT-4): $8,000/month (estimated)
Google Gemini Pro Vision: $2,000/month (estimated)
Payment Processing (YooKassa + Stripe): $1,500/month (estimated)

Total External APIs: ~$11,500/month
```

#### **Total Monthly Infrastructure Cost: ~$11,880**

---

**Infrastructure Summary:** The MODERA.FASHION infrastructure is designed for scalability, reliability, and cost-effectiveness. The multi-service architecture with proper separation ensures maintainability, while the comprehensive monitoring and backup strategies provide operational excellence.