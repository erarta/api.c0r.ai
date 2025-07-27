# Требования к развертыванию и инфраструктуре AIDI.APP

*Дата создания: 27 января 2025*
*Цель: Детальный план инфраструктуры и развертывания сервиса репутации и KYC*

## 🏗️ Архитектура инфраструктуры

### Диаграмма развертывания

```mermaid
graph TB
    subgraph "External Services"
        TG[Telegram Bot API]
        GEMINI[Gemini AI API]
        OPENAI[OpenAI API]
        STRIPE[Stripe API]
        YOOKASSA[YooKassa API]
        SOCIAL[Social Media APIs<br/>VK, Instagram, etc.]
    end
    
    subgraph "CDN & Load Balancer"
        CF[Cloudflare]
        LB[Load Balancer]
    end
    
    subgraph "Application Layer - AWS EC2"
        subgraph "API Service Cluster"
            API1[API Service 1<br/>Port 8000]
            API2[API Service 2<br/>Port 8000]
            API3[API Service 3<br/>Port 8000]
        end
        
        subgraph "ML Service Cluster"
            ML1[ML Service 1<br/>Port 8001]
            ML2[ML Service 2<br/>Port 8001]
        end
        
        subgraph "Payment Service Cluster"
            PAY1[Payment Service 1<br/>Port 8002]
            PAY2[Payment Service 2<br/>Port 8002]
        end
    end
    
    subgraph "Data Layer"
        DB[(Supabase PostgreSQL<br/>Primary + Replica)]
        REDIS[(Redis Cache<br/>Session & Rate Limiting)]
        R2[Cloudflare R2<br/>File Storage]
    end
    
    subgraph "Monitoring & Logging"
        GRAFANA[Grafana Dashboard]
        PROMETHEUS[Prometheus Metrics]
        LOKI[Loki Logs]
        ALERT[AlertManager]
    end
    
    TG --> CF
    CF --> LB
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> ML1
    API2 --> ML1
    API3 --> ML2
    
    API1 --> PAY1
    API2 --> PAY2
    
    ML1 --> GEMINI
    ML1 --> OPENAI
    ML2 --> SOCIAL
    
    PAY1 --> STRIPE
    PAY2 --> YOOKASSA
    
    API1 --> DB
    API2 --> DB
    API3 --> DB
    
    API1 --> REDIS
    API2 --> REDIS
    API3 --> REDIS
    
    ML1 --> R2
    ML2 --> R2
    
    API1 --> PROMETHEUS
    ML1 --> PROMETHEUS
    PAY1 --> PROMETHEUS
    
    PROMETHEUS --> GRAFANA
    PROMETHEUS --> ALERT
```

## 🖥️ Серверная инфраструктура

### AWS EC2 Конфигурация

#### Production Environment

**API Service Cluster (3 инстанса)**
- **Instance Type:** t3.large (2 vCPU, 8 GB RAM)
- **Storage:** 100 GB GP3 SSD
- **OS:** Ubuntu 22.04 LTS
- **Auto Scaling:** Min 2, Max 5 instances
- **Load Balancer:** Application Load Balancer (ALB)

**ML Service Cluster (2 инстанса)**
- **Instance Type:** c5.xlarge (4 vCPU, 8 GB RAM)
- **Storage:** 200 GB GP3 SSD
- **OS:** Ubuntu 22.04 LTS
- **Auto Scaling:** Min 1, Max 4 instances
- **GPU Support:** Optional T4 instances for heavy AI workloads

**Payment Service Cluster (2 инстанса)**
- **Instance Type:** t3.medium (2 vCPU, 4 GB RAM)
- **Storage:** 50 GB GP3 SSD
- **OS:** Ubuntu 22.04 LTS
- **Auto Scaling:** Min 1, Max 3 instances

#### Staging Environment

**Single Multi-Service Instance**
- **Instance Type:** t3.medium (2 vCPU, 4 GB RAM)
- **Storage:** 100 GB GP3 SSD
- **OS:** Ubuntu 22.04 LTS
- **Purpose:** Testing and development

### Сетевая архитектура

#### VPC Configuration
```yaml
VPC:
  CIDR: 10.0.0.0/16
  
Subnets:
  Public:
    - 10.0.1.0/24 (us-east-1a)
    - 10.0.2.0/24 (us-east-1b)
  Private:
    - 10.0.10.0/24 (us-east-1a)
    - 10.0.20.0/24 (us-east-1b)

Security Groups:
  ALB-SG:
    - HTTP (80) from 0.0.0.0/0
    - HTTPS (443) from 0.0.0.0/0
  
  API-SG:
    - Port 8000 from ALB-SG
    - SSH (22) from Bastion-SG
  
  ML-SG:
    - Port 8001 from API-SG
    - SSH (22) from Bastion-SG
  
  Payment-SG:
    - Port 8002 from API-SG
    - SSH (22) from Bastion-SG
```

## 🗄️ База данных и хранилище

### Supabase PostgreSQL

#### Production Configuration
```yaml
Database:
  Plan: Pro ($25/month)
  Compute: 4 vCPU, 8 GB RAM
  Storage: 500 GB SSD
  Connections: 200 concurrent
  Backups: Daily automated + Point-in-time recovery
  
Read Replicas:
  Count: 2
  Regions: us-east-1, eu-west-1
  Purpose: Read scaling and disaster recovery

Extensions:
  - uuid-ossp (UUID generation)
  - pg_trgm (Full-text search)
  - btree_gin (Advanced indexing)
  - pg_stat_statements (Query performance)
```

#### Connection Pooling
```yaml
PgBouncer:
  Pool Mode: transaction
  Max Client Connections: 1000
  Default Pool Size: 25
  Reserve Pool Size: 5
  
Connection String:
  Primary: postgresql://user:pass@db.supabase.co:5432/postgres
  Replica: postgresql://user:pass@replica.supabase.co:5432/postgres
```

### Redis Cache

#### Configuration
```yaml
Redis:
  Provider: AWS ElastiCache
  Node Type: cache.t3.micro
  Engine Version: 7.0
  Cluster Mode: Enabled
  Nodes: 3 (1 primary, 2 replicas)
  
Use Cases:
  - Session storage
  - Rate limiting
  - API response caching
  - Temporary analysis data
```

### Cloudflare R2 Storage

#### Configuration
```yaml
R2 Storage:
  Buckets:
    - aidi-uploads (user uploads)
    - aidi-reports (generated reports)
    - aidi-backups (database backups)
    - aidi-logs (application logs)
  
  Lifecycle Policies:
    - Delete uploads after 30 days
    - Archive reports after 90 days
    - Keep backups for 1 year
  
  Access Control:
    - Private by default
    - Signed URLs for temporary access
    - CORS enabled for web uploads
```

## 🔧 Конфигурация сервисов

### Docker Compose для Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    image: aidi/api:latest
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  ml:
    image: aidi/ml:latest
    ports:
      - "8001:8001"
    environment:
      - NODE_ENV=production
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - R2_ACCESS_KEY=${R2_ACCESS_KEY}
      - R2_SECRET_KEY=${R2_SECRET_KEY}
    volumes:
      - ./ml-models:/app/models
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 4G
          cpus: '2.0'

  payment:
    image: aidi/payment:latest
    ports:
      - "8002:8002"
    environment:
      - NODE_ENV=production
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - YOOKASSA_SECRET_KEY=${YOOKASSA_SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
      - ml
      - payment
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
```

### Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        least_conn;
        server api:8000 max_fails=3 fail_timeout=30s;
    }
    
    upstream ml_backend {
        least_conn;
        server ml:8001 max_fails=3 fail_timeout=30s;
    }
    
    upstream payment_backend {
        least_conn;
        server payment:8002 max_fails=3 fail_timeout=30s;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=ml:10m rate=5r/s;
    
    server {
        listen 80;
        server_name api.aidi.app;
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name api.aidi.app;
        
        ssl_certificate /etc/nginx/ssl/aidi.app.crt;
        ssl_certificate_key /etc/nginx/ssl/aidi.app.key;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
        
        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_timeout 300s;
        }
        
        # ML endpoints
        location /ml/ {
            limit_req zone=ml burst=10 nodelay;
            proxy_pass http://ml_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_timeout 600s;
            client_max_body_size 500M;
        }
        
        # Payment endpoints
        location /payment/ {
            proxy_pass http://payment_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health checks
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

## 🔐 Переменные окружения

### Production Environment Variables

```bash
# .env.production

# ===== ОСНОВНЫЕ НАСТРОЙКИ =====
NODE_ENV=production
APP_NAME=AIDI.APP
APP_VERSION=1.0.0
APP_URL=https://aidi.app
API_URL=https://api.aidi.app

# ===== БАЗА ДАННЫХ =====
DATABASE_URL=postgresql://user:password@db.supabase.co:5432/postgres
DATABASE_REPLICA_URL=postgresql://user:password@replica.supabase.co:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# ===== REDIS =====
REDIS_URL=redis://your-redis-cluster.cache.amazonaws.com:6379
REDIS_PASSWORD=your-redis-password

# ===== TELEGRAM =====
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_SERVICE_BOT_TOKEN=your-service-bot-token
TELEGRAM_WEBHOOK_URL=https://api.aidi.app/webhook/telegram
TELEGRAM_WEBHOOK_SECRET=your-webhook-secret

# ===== AI СЕРВИСЫ =====
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-pro
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4-vision-preview

# ===== ПЛАТЕЖИ =====
STRIPE_PUBLISHABLE_KEY=pk_live_your-stripe-key
STRIPE_SECRET_KEY=sk_live_your-stripe-secret
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

YOOKASSA_SHOP_ID=your-shop-id
YOOKASSA_SECRET_KEY=your-yookassa-secret
YOOKASSA_WEBHOOK_SECRET=your-webhook-secret

# ===== ХРАНИЛИЩЕ =====
R2_ACCOUNT_ID=your-cloudflare-account-id
R2_ACCESS_KEY=your-r2-access-key
R2_SECRET_KEY=your-r2-secret-key
R2_BUCKET_UPLOADS=aidi-uploads
R2_BUCKET_REPORTS=aidi-reports
R2_PUBLIC_URL=https://uploads.aidi.app

# ===== БЕЗОПАСНОСТЬ =====
JWT_SECRET=your-super-secret-jwt-key
ENCRYPTION_KEY=your-32-character-encryption-key
WEBHOOK_SECRET=your-webhook-verification-secret

# ===== МОНИТОРИНГ =====
SENTRY_DSN=https://your-sentry-dsn
GRAFANA_PASSWORD=your-grafana-password
PROMETHEUS_PASSWORD=your-prometheus-password

# ===== ВНЕШНИЕ API =====
VK_API_TOKEN=your-vk-api-token
INSTAGRAM_API_TOKEN=your-instagram-token
LINKEDIN_API_TOKEN=your-linkedin-token

# ===== УВЕДОМЛЕНИЯ =====
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@aidi.app
SMTP_PASSWORD=your-email-password

# ===== RATE LIMITING =====
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_PREMIUM_MAX=500

# ===== ЛОГИРОВАНИЕ =====
LOG_LEVEL=info
LOG_FORMAT=json
LOG_FILE=/app/logs/aidi.log
```

## 📊 Мониторинг и алертинг

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'aidi-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'aidi-ml'
    static_configs:
      - targets: ['ml:8001']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'aidi-payment'
    static_configs:
      - targets: ['payment:8002']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

### Alert Rules

```yaml
# alert_rules.yml
groups:
  - name: aidi_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time"
          description: "95th percentile response time is {{ $value }} seconds"

      - alert: DatabaseConnectionsHigh
        expr: pg_stat_activity_count > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "Database has {{ $value }} active connections"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "{{ $labels.job }} service is not responding"
```

### Grafana Dashboards

#### Main Dashboard Panels
1. **System Overview**
   - Total requests per minute
   - Error rate percentage
   - Average response time
   - Active users

2. **Service Health**
   - API service status
   - ML service status
   - Payment service status
   - Database connections

3. **Business Metrics**
   - Reputation analyses per hour
   - Deepfake detections per hour
   - Revenue per day
   - User registrations

4. **Infrastructure**
   - CPU usage per service
   - Memory usage per service
   - Disk usage
   - Network I/O

## 🚀 Процесс развертывания

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy AIDI.APP

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          pytest tests/ --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to Amazon ECR
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push API image
        run: |
          docker build -t aidi/api:latest ./services/api
          docker tag aidi/api:latest $ECR_REGISTRY/aidi/api:latest
          docker push $ECR_REGISTRY/aidi/api:latest
      
      - name: Build and push ML image
        run: |
          docker build -t aidi/ml:latest ./services/ml
          docker tag aidi/ml:latest $ECR_REGISTRY/aidi/ml:latest
          docker push $ECR_REGISTRY/aidi/ml:latest
      
      - name: Build and push Payment image
        run: |
          docker build -t aidi/payment:latest ./services/pay
          docker tag aidi/payment:latest $ECR_REGISTRY/aidi/payment:latest
          docker push $ECR_REGISTRY/aidi/payment:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    
    steps:
      - name: Deploy to production
        run: |
          # SSH to production servers and update services
          ssh -o StrictHostKeyChecking=no ${{ secrets.PROD_SERVER }} '
            cd /opt/aidi &&
            docker-compose pull &&
            docker-compose up -d --remove-orphans &&
            docker system prune -f
          '
```

### Deployment Scripts

```bash
#!/bin/bash
# deploy.sh - Production deployment script

set -e

echo "🚀 Starting AIDI.APP deployment..."

# Backup current deployment
echo "📦 Creating backup..."
docker-compose -f docker-compose.prod.yml down
cp -r /opt/aidi /opt/aidi-backup-$(date +%Y%m%d-%H%M%S)

# Pull latest images
echo "📥 Pulling latest images..."
docker-compose -f docker-compose.prod.yml pull

# Run database migrations
echo "🗄️ Running database migrations..."
python scripts/run_migrations.py

# Start services
echo "🔄 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Health checks
echo "🏥 Running health checks..."
sleep 30

for service in api ml payment; do
    if curl -f http://localhost:800${service#*}0/health; then
        echo "✅ $service is healthy"
    else
        echo "❌ $service health check failed"
        exit 1
    fi
done

# Cleanup old images
echo "🧹 Cleaning up..."
docker system prune -f

echo "✅ Deployment completed successfully!"
```

## 💰 Стоимость инфраструктуры

### Ежемесячные расходы (USD)

#### AWS Services
- **EC2 Instances:** $450/month
  - API: 3 × t3.large = $150
  - ML: 2 × c5.xlarge = $240
  - Payment: 2 × t3.medium = $60
- **Load Balancer:** $25/month
- **Data Transfer:** $50/month
- **EBS Storage:** $100/month

#### External Services
- **Supabase Pro:** $25/month
- **Redis ElastiCache:** $50/month
- **Cloudflare R2:** $30/month
- **Domain & SSL:** $20/month

#### AI Services (переменные)
- **Gemini API:** $200-500/month
- **OpenAI API:** $300-800/month

#### Мониторинг
- **Grafana Cloud:** $50/month
- **Sentry:** $25/month

**Общая стоимость: $1,325-1,925/month**

### Оптимизация расходов

1. **Reserved Instances** - экономия 30-50% на EC2
2. **Spot Instances** для ML обработки - экономия до 70%
3. **Auto Scaling** - оплата только за используемые ресурсы
4. **CDN кеширование** - снижение нагрузки на серверы
5. **Compression** - снижение трафика и storage costs

## 🔒 Безопасность

### Security Checklist

- [ ] **SSL/TLS** - все соединения зашифрованы
- [ ] **WAF** - защита от веб-атак
- [ ] **DDoS Protection** - через Cloudflare
- [ ] **Rate Limiting** - защита от злоупотреблений
- [ ] **Input Validation** - валидация всех входных данных
- [ ] **SQL Injection Protection** - параметризованные запросы
- [ ] **XSS Protection** - санитизация выходных данных
- [ ] **CSRF Protection** - токены для форм
- [ ] **Secrets Management** - AWS Secrets Manager
- [ ] **Regular Updates** - обновление зависимостей
- [ ] **Backup Strategy** - регулярные бэкапы
- [ ] **Monitoring** - логирование всех действий
- [ ] **Incident Response** - план реагирования на инциденты

## 📋 Чеклист развертывания

### Pre-deployment
- [ ] Создать AWS аккаунт и настроить IAM
- [ ] Настроить Supabase проект
- [ ] Получить API ключи (Telegram, Gemini, OpenAI)
- [ ] Настроить платежные системы (Stripe, YooKassa)
- [ ] Создать Cloudflare аккаунт и R2 buckets
- [ ] Настроить домены и SSL сертификаты
- [ ] Подготовить переменные окружения

### Deployment
- [ ] Развернуть VPC и сетевую инфраструктуру
- [ ] Запустить EC2 инстансы
- [ ] Настроить Load Balancer
- [ ] Развернуть базу данных и миграции
- [ ] Развернуть Redis кластер
- [ ] Развернуть приложения через Docker
- [ ] Настроить Nginx reverse proxy
- [ ] Настроить мониторинг и алертинг
- [ ] Провести нагрузочное тестирование

### Post-deployment
- [ ] Настроить бэкапы
- [ ] Настроить логирование
- [ ] Провести security audit
- [ ] Настроить CI/CD pipeline
- [ ] Создать документацию для операций
- [ ] Обучить команду процедурам

**Инфраструктура AIDI.APP готова к масштабированию и обеспечивает высокую доступность, безопасность и производительность для сервиса репутационного анализа и детекции дипфейков.**