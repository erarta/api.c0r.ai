#!/bin/bash

# Alternative SSL Certificate Setup using Standalone Method
# This method temporarily stops nginx and uses certbot's built-in web server

set -e

echo "🔐 Getting SSL certificates using standalone method..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as non-root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Run as ubuntu user."
   exit 1
fi

# Ensure we're in the right directory
cd /home/ubuntu/api.c0r.ai

print_status "Stopping nginx temporarily..."
sudo systemctl stop nginx

print_status "Getting SSL certificates using standalone method..."
sudo certbot certonly \
    --standalone \
    --email your-email@example.com \
    --agree-tos \
    --no-eff-email \
    --preferred-challenges http \
    -d api.c0r.ai \
    -d ml.c0r.ai \
    -d pay.c0r.ai

if [ $? -eq 0 ]; then
    print_status "✅ SSL certificates obtained successfully!"
    
    # Switch to production SSL configuration
    print_status "Switching to production SSL configuration..."
    
    # Backup current config
    sudo cp /etc/nginx/sites-available/c0r.ai /etc/nginx/sites-available/c0r.ai.backup
    
    # Copy production config
    sudo cp nginx.conf.production /etc/nginx/sites-available/c0r.ai
    
    # Test configuration
    if sudo nginx -t; then
        print_status "✅ Production SSL configuration is valid"
        sudo systemctl start nginx
        print_status "✅ Nginx started with SSL configuration"
    else
        print_error "❌ Production SSL configuration test failed"
        print_error "Restoring backup configuration..."
        sudo cp /etc/nginx/sites-available/c0r.ai.backup /etc/nginx/sites-available/c0r.ai
        sudo systemctl start nginx
        exit 1
    fi
    
    # Setup auto-renewal
    print_status "Setting up auto-renewal..."
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --pre-hook 'systemctl stop nginx' --post-hook 'systemctl start nginx'") | crontab -
    
    print_status "🎉 SSL setup completed successfully!"
    echo ""
    print_status "Testing HTTPS endpoints:"
    
    DOMAINS=("api.c0r.ai" "ml.c0r.ai" "pay.c0r.ai")
    for domain in "${DOMAINS[@]}"; do
        sleep 2
        if curl -I "https://$domain/health" 2>/dev/null | grep -q "200\|404"; then
            print_status "✅ https://$domain - SSL working"
        else
            print_warning "⚠️  https://$domain - Check manually"
        fi
    done
    
else
    print_error "❌ Failed to obtain SSL certificates"
    print_error "Starting nginx back..."
    sudo systemctl start nginx
    exit 1
fi

print_status "🔐 SSL certificate setup completed!"
echo ""
print_warning "Don't forget to:"
print_warning "1. Update your email in the script: your-email@example.com"
print_warning "2. Test all endpoints manually"
print_warning "3. Update your Telegram bot to use HTTPS URLs" 