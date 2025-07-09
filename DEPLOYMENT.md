# 🚀 Deployment Guide for c0r.ai

## Prerequisites

### 1. AWS EC2 Setup
- **Instance Type**: t3.medium or higher (minimum 4GB RAM)
- **OS**: Ubuntu 22.04 LTS
- **Storage**: 20GB+ SSD
- **Security Group**: Ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

### 2. Domain Configuration
Configure DNS A records for your domain:
```
api.c0r.ai  → Your_EC2_Public_IP
ml.c0r.ai   → Your_EC2_Public_IP  
pay.c0r.ai  → Your_EC2_Public_IP
```

## 🔧 Server Setup

### 1. Connect to EC2 Instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt install nginx -y

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y

# Install Git
sudo apt install git -y
```

### 3. Clone Repository
```bash
cd /home/ubuntu
git clone https://github.com/yourusername/api.c0r.ai.git
cd api.c0r.ai
```

### 4. Configure Environment
```bash
# Copy production environment template
cp .env.production.example .env

# Edit environment variables
nano .env
```

**Required variables to update:**
- `TELEGRAM_BOT_TOKEN` - Your production bot token
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_KEY` - Your Supabase service key
- `OPENAI_API_KEY` - Your OpenAI API key
- `INTERNAL_API_TOKEN` - Generate secure token: `openssl rand -hex 32`
- `YOOKASSA_SHOP_ID` - Your YooKassa shop ID
- `YOOKASSA_SECRET_KEY` - Your YooKassa secret key
- `YOOKASSA_PROVIDER_TOKEN` - Your YooKassa provider token

**Service URLs are automatically configured:**
- `ML_SERVICE_URL=https://ml.c0r.ai` (production)
- `PAY_SERVICE_URL=https://pay.c0r.ai` (production)

**Alternative: Use environment switching script**
```bash
# Switch to production URLs
./scripts/switch-env.sh prod

# Switch back to development URLs (if needed)
./scripts/switch-env.sh dev
```

### 5. Configure Nginx (Temporary HTTP Configuration)
```bash
# Remove default config
sudo rm /etc/nginx/sites-enabled/default

# Copy temporary HTTP config from api.c0r.ai directory
cd /home/ubuntu/api.c0r.ai
sudo cp nginx.conf.temp /etc/nginx/sites-available/c0r.ai
sudo ln -s /etc/nginx/sites-available/c0r.ai /etc/nginx/sites-enabled/

# Create web root for certbot
sudo mkdir -p /var/www/html

# Test configuration
sudo nginx -t

# If configuration is OK, reload nginx
sudo systemctl reload nginx
```

### 6. Start Services
```bash
# Build and start all services
docker-compose build
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs
```

### 7. Obtain SSL Certificates
```bash
# Get certificates for all subdomains
sudo certbot --nginx -d api.c0r.ai -d ml.c0r.ai -d pay.c0r.ai

# Setup auto-renewal
sudo crontab -e
# Add line: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 8. Switch to Production SSL Configuration
```bash
# Copy production SSL config
sudo cp nginx.conf.production /etc/nginx/sites-available/c0r.ai

# Test configuration
sudo nginx -t

# If configuration is OK, reload nginx
sudo systemctl reload nginx
```

### 9. Configure Firewall
```bash
# Setup UFW
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

## 🤖 GitHub Actions Setup

### 1. Repository Secrets
Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

- `EC2_SSH_KEY` - Your EC2 private key content
- `EC2_USER` - `ubuntu`
- `EC2_HOST` - Your EC2 public IP or domain

### 2. Generate SSH Key for Deployment
```bash
# On your local machine
ssh-keygen -t rsa -b 4096 -f ~/.ssh/c0r_ai_deploy

# Copy public key to EC2
ssh-copy-id -i ~/.ssh/c0r_ai_deploy.pub ubuntu@your-ec2-ip

# Add private key content to GitHub secrets
cat ~/.ssh/c0r_ai_deploy
```

### 3. Test Deployment
Push to main branch or trigger manual deployment:
```bash
git add .
git commit -m "feat: setup production deployment"
git push origin main
```

## 🔍 Monitoring & Maintenance

### Health Checks
```bash
# Check service status
curl https://api.c0r.ai/
curl https://ml.c0r.ai/
curl https://pay.c0r.ai/

# Check logs
docker-compose logs -f api
docker-compose logs -f ml
docker-compose logs -f pay
```

### System Monitoring
```bash
# Check system resources
htop
df -h
docker system df

# Clean up old images
docker system prune -f
```

### Backup Strategy
```bash
# Backup environment file
cp .env .env.backup.$(date +%Y%m%d)

# Database backup (if using local DB)
# Configure Supabase backups in dashboard
```

## 🔒 Security Considerations

### 1. Environment Variables
- Never commit `.env` to repository
- Use strong `INTERNAL_API_TOKEN`
- Rotate API keys regularly

### 2. Nginx Security
- Rate limiting configured per service
- Security headers enabled
- SSL certificates auto-renewal

### 3. Docker Security
- Services run in isolated containers
- No root privileges in containers
- Internal network communication only

## 🚨 Troubleshooting

### Common Issues

**Services not starting:**
```bash
docker-compose logs [service-name]
docker-compose down && docker-compose up -d
```

**SSL certificate issues:**
```bash
sudo certbot renew --dry-run
sudo nginx -t && sudo systemctl reload nginx
```

**High memory usage:**
```bash
docker system prune -f
sudo systemctl restart docker
```

### Log Locations
- Nginx: `/var/log/nginx/`
- Docker: `docker-compose logs`
- System: `journalctl -u docker`

## 📊 Performance Optimization

### 1. Docker Optimization
```bash
# Add to docker-compose.yml for production
version: '3.8'
services:
  api:
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### 2. Nginx Optimization
```nginx
# Add to nginx.conf
gzip on;
gzip_types text/plain application/json;
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;
```

## 🎯 Next Steps

1. **Setup Monitoring**: Configure Grafana/Prometheus
2. **Load Balancing**: Add multiple instances if needed
3. **CDN**: Configure Cloudflare for static assets
4. **Database Scaling**: Optimize Supabase configuration
5. **Payment Integration**: Complete YooKassa setup

## 📞 Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Verify environment variables
3. Test network connectivity
4. Check SSL certificates

---

**Ready for production deployment!** 🚀 