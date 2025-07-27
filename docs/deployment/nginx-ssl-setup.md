# Quick Fix for Nginx SSL Configuration Issue

## Problem
```
nginx: [emerg] open() "/etc/letsencrypt/options-ssl-nginx.conf" failed (2: No such file or directory)
```

This happens because the production nginx config references SSL files that don't exist yet.

## Solution

### Step 1: Use Temporary HTTP Configuration
```bash
# From your project directory
cd ~/api.c0r.ai

# Copy temporary HTTP-only config
sudo cp nginx.conf.temp /etc/nginx/sites-available/c0r.ai

# Create web root for certbot
sudo mkdir -p /var/www/html

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### Step 2: Start Your Services
```bash
# Build and start all services
docker-compose build
docker-compose up -d

# Check status
docker-compose ps
```

### Step 3: Obtain SSL Certificates
```bash
# Get certificates for all subdomains
sudo certbot --nginx -d api.c0r.ai -d ml.c0r.ai -d pay.c0r.ai
```

### Step 4: Switch to Production SSL Configuration
```bash
# Copy production SSL config
sudo cp nginx.conf.production /etc/nginx/sites-available/c0r.ai

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### Step 5: Verify Everything Works
```bash
# Test HTTP endpoints (should redirect to HTTPS)
curl -I http://api.c0r.ai/health
curl -I http://ml.c0r.ai/health
curl -I http://pay.c0r.ai/health

# Test HTTPS endpoints
curl -I https://api.c0r.ai/health
curl -I https://ml.c0r.ai/health
curl -I https://pay.c0r.ai/health
```

## Files Overview

- **`nginx.conf.temp`** - HTTP-only configuration for initial setup
- **`nginx.conf.production`** - Full HTTPS configuration with SSL
- **`scripts/setup-production.sh`** - Automated setup script (updated)

## Why This Approach?

1. **Chicken-and-egg problem**: SSL config needs certificates, but certificates need HTTP access
2. **Certbot needs HTTP**: Certbot validates domain ownership via HTTP before issuing certificates
3. **Two-stage setup**: Start with HTTP, get certificates, then switch to HTTPS

This is the standard approach for Let's Encrypt SSL setup! 