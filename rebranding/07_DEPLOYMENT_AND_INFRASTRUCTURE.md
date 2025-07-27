# Deployment & Infrastructure Plan - MODERA.FASHION

## Date: 2025-01-26
## Purpose: Plan deployment and infrastructure for MODERA.FASHION

## Infrastructure Overview

### Current Infrastructure (c0r.ai)
- **Hosting:** AWS EC2
- **Database:** Supabase (PostgreSQL)
- **Storage:** Cloudflare R2
- **CDN:** Cloudflare
- **Domain:** c0r.ai
- **SSL:** Let's Encrypt

### Target Infrastructure (MODERA.FASHION)
- **Hosting:** AWS EC2 (upgraded)
- **Database:** Supabase (new project)
- **Storage:** Cloudflare R2 (new bucket)
- **CDN:** Cloudflare
- **Domain:** https://modera.fashion
- **API Domain:** https://api.modera.fashion
- **CDN Domain:** https://cdn.modera.fashion
- **SSL:** Let's Encrypt

## Deployment Architecture

### Service Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │    │   ML Service    │    │  Payment Service│
│   (FastAPI)     │◄──►│   (AI Models)   │◄──►│   (Yookassa)    │
│   Port: 8000    │    │   Port: 8001    │    │   Port: 8001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Supabase DB   │
                    │   (PostgreSQL)  │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Cloudflare R2  │
                    │   (Storage)     │
                    └─────────────────┘
```

### Docker Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: services/api/bot/Dockerfile
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      - ml
      - pay
    networks:
      - modera-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  ml:
    build:
      context: .
      dockerfile: services/ml/Dockerfile
    env_file: .env
    ports:
      - "8001:8001"
    networks:
      - modera-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  pay:
    build:
      context: .
      dockerfile: services/pay/Dockerfile
    env_file: .env
    ports:
      - "8002:8002"
    networks:
      - modera-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  modera-network:
    driver: bridge
```

## Environment Configuration

### New Environment Variables
```bash
# MODERA.FASHION Configuration
BASE_URL=https://modera.fashion
API_URL=https://api.modera.fashion
CDN_URL=https://cdn.modera.fashion
SERVICE_NAME=modera-fashion

# New Supabase Configuration
SUPABASE_URL=https://[new-project].supabase.co
SUPABASE_SERVICE_KEY=[new-service-key]

# New R2 Configuration
R2_BUCKET_NAME=modera-fashion-storage
R2_ACCOUNT_ID=[account-id]
R2_ACCESS_KEY_ID=[access-key]
R2_SECRET_ACCESS_KEY=[secret-key]

# New Telegram Bot
TELEGRAM_BOT_TOKEN=[new-bot-token]
TELEGRAM_SERVICE_BOT_TOKEN=[new-service-bot-token]

# New Payment Configuration
YOOKASSA_SHOP_ID=[new-shop-id]
YOOKASSA_SECRET_KEY=[new-secret-key]

# AI Model Configuration
OPENAI_API_KEY=[openai-key]
GEMINI_API_KEY=[gemini-key]

# E-commerce Integration
ECOMMERCE_API_KEYS=[api-keys]
AFFILIATE_CODES=[affiliate-codes]
```

## Deployment Steps

### Phase 1: Infrastructure Setup

#### 1. Domain and DNS
```bash
# Register domain
modera.fashion

# Configure DNS
A     modera.fashion     [EC2-IP]
CNAME www.modera.fashion modera.fashion
CNAME api.modera.fashion modera.fashion
CNAME cdn.modera.fashion modera.fashion
```

#### 2. AWS EC2 Setup
```bash
# Launch new EC2 instance
Instance Type: t3.medium (upgrade from current)
OS: Ubuntu 22.04 LTS
Storage: 50GB SSD
Security Groups: 
  - SSH (22)
  - HTTP (80)
  - HTTPS (443)
  - Custom (8000-8002)
```

#### 3. Supabase Project
```bash
# Create new Supabase project
Project Name: modera-fashion
Database: PostgreSQL 15
Region: [closest to target market]

# Run migration script
psql -h [host] -U [user] -d [database] -f migrations/migration_script.sql
```

#### 4. Cloudflare R2
```bash
# Create new R2 bucket
Bucket Name: modera-fashion-storage
Public Access: Enabled
CORS: Configured for web access

# Configure CDN
Custom Domain: cdn.modera.fashion
```

### Phase 2: Application Deployment

#### 1. Code Migration
```bash
# Clone and setup new repository
git clone [modera-fashion-repo]
cd modera-fashion

# Update configuration files
cp .env.example .env
# Edit .env with new values

# Update docker-compose.yml
# Update nginx configuration
```

#### 2. Database Migration
```bash
# Run migration script
python scripts/run_migrations.py

# Verify data integrity
python scripts/verify_migration.py
```

#### 3. Service Deployment
```bash
# Build and start services
docker-compose build
docker-compose up -d

# Verify services
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
```

### Phase 3: SSL and Security

#### 1. SSL Certificate
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate SSL certificate
sudo certbot --nginx -d modera.fashion -d www.modera.fashion

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 2. Security Configuration
```bash
# Configure firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Update system
sudo apt update && sudo apt upgrade -y
```

## Monitoring and Logging

### Health Checks
```python
# Health check endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "services": {
            "database": check_database_connection(),
            "storage": check_r2_connection(),
            "ai_models": check_ai_models()
        }
    }
```

### Logging Configuration
```python
# Structured logging
import logging
from loguru import logger

logger.add(
    "logs/modera-fashion.log",
    rotation="100 MB",
    retention="30 days",
    level="INFO",
    format="{time} | {level} | {message}"
)
```

### Monitoring Dashboard
```bash
# Setup monitoring
# Option 1: Simple monitoring script
python scripts/monitor_services.py

# Option 2: Prometheus + Grafana
docker-compose -f monitoring/docker-compose.yml up -d
```

## Backup and Recovery

### Database Backup
```bash
# Automated backup script
#!/bin/bash
# backup_database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/database"

# Create backup
pg_dump $DATABASE_URL > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

### File Storage Backup
```bash
# R2 backup script
#!/bin/bash
# backup_storage.sh

# Sync R2 bucket to local backup
rclone sync modera-fashion-storage: /backups/storage/

# Keep only last 30 days
find /backups/storage -mtime +30 -delete
```

## Performance Optimization

### Caching Strategy
```python
# Redis caching for AI results
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@cache(redis_client, ttl=3600)
async def get_cached_analysis(image_hash: str):
    """Cache AI analysis results"""
    pass
```

### Load Balancing
```nginx
# Nginx configuration for load balancing
upstream modera_api {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name modera.fashion;
    
    location / {
        proxy_pass http://modera_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Disaster Recovery

### Recovery Procedures
1. **Database Recovery:**
   ```bash
   # Restore from backup
   psql $DATABASE_URL < backup_20250126_120000.sql
   ```

2. **Application Recovery:**
   ```bash
   # Redeploy services
   docker-compose down
   docker-compose up -d
   ```

3. **Domain Recovery:**
   ```bash
   # Update DNS if needed
   # Point to backup server
   ```

### Backup Testing
```bash
# Monthly backup testing
python scripts/test_backup_restore.py
```

## Cost Optimization

### Resource Monitoring
```bash
# Monitor resource usage
htop
df -h
docker stats
```

### Cost Optimization Strategies
1. **Use spot instances** for non-critical workloads
2. **Implement auto-scaling** based on demand
3. **Optimize AI model usage** to reduce API costs
4. **Use CDN caching** to reduce bandwidth costs

## Security Checklist

- [ ] SSL certificates installed and auto-renewing
- [ ] Firewall configured and enabled
- [ ] Database access restricted
- [ ] API keys secured and rotated
- [ ] Regular security updates
- [ ] Backup encryption enabled
- [ ] Monitoring and alerting configured
- [ ] Access logs enabled and monitored
