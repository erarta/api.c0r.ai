#!/bin/bash

# Production Setup Script for c0r.ai on AWS EC2
# Run this script on your Ubuntu 22.04 EC2 instance

set -e

echo "🚀 Starting c0r.ai production setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as non-root user
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Run as ubuntu user."
   exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
    rm get-docker.sh
    print_status "Docker installed. Please log out and log back in to apply group changes."
else
    print_status "Docker already installed."
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    print_status "Docker Compose already installed."
fi

# Install Nginx
if ! command -v nginx &> /dev/null; then
    print_status "Installing Nginx..."
    sudo apt install nginx -y
else
    print_status "Nginx already installed."
fi

# Install Certbot
if ! command -v certbot &> /dev/null; then
    print_status "Installing Certbot..."
    sudo apt install certbot python3-certbot-nginx -y
else
    print_status "Certbot already installed."
fi

# Install Git
if ! command -v git &> /dev/null; then
    print_status "Installing Git..."
    sudo apt install git -y
else
    print_status "Git already installed."
fi

# Clone repository if not exists
if [ ! -d "/home/ubuntu/api.c0r.ai" ]; then
    print_status "Cloning repository..."
    cd /home/ubuntu
    print_warning "Please update the repository URL below with your actual GitHub repository:"
    echo "git clone https://github.com/erarta/api.c0r.ai.git"
    read -p "Press Enter after you've cloned the repository manually..."
else
    print_status "Repository already exists."
fi

# Navigate to project directory
cd /home/ubuntu/api.c0r.ai

# Check if .env exists
if [ ! -f ".env" ]; then
    print_status "Setting up environment configuration..."
    if [ -f ".env.production.example" ]; then
        cp .env.production.example .env
        print_warning "Please edit .env file with your production values:"
        print_warning "nano .env"
        print_warning "Required variables:"
        print_warning "- TELEGRAM_BOT_TOKEN"
        print_warning "- SUPABASE_URL"
        print_warning "- SUPABASE_SERVICE_KEY"
        print_warning "- OPENAI_API_KEY"
        print_warning "- INTERNAL_API_TOKEN (generate with: openssl rand -hex 32)"
        print_warning "- YOOKASSA_SHOP_ID"
        print_warning "- YOOKASSA_SECRET_KEY"
        print_warning "- YOOKASSA_PROVIDER_TOKEN"
        read -p "Press Enter after editing .env file..."
    else
        print_error ".env.production.example not found!"
        exit 1
    fi
else
    print_status "Environment file already exists."
fi

# Switch to production URLs
print_status "Switching to production service URLs..."
if [ -f "scripts/switch-env.sh" ]; then
    chmod +x scripts/switch-env.sh
    ./scripts/switch-env.sh prod
else
    print_warning "Environment switch script not found. Please ensure service URLs are set to production domains."
fi

# Configure Nginx
print_status "Configuring Nginx..."
if [ -f "nginx.conf.production" ]; then
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo cp nginx.conf.production /etc/nginx/sites-available/c0r.ai
    sudo ln -sf /etc/nginx/sites-available/c0r.ai /etc/nginx/sites-enabled/
    
    # Test nginx configuration
    if sudo nginx -t; then
        print_status "Nginx configuration is valid."
        sudo systemctl reload nginx
    else
        print_error "Nginx configuration test failed!"
        exit 1
    fi
else
    print_error "nginx.conf.production not found!"
    exit 1
fi

# Configure firewall
print_status "Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

print_status "✅ Basic setup completed!"
echo ""
print_warning "Next steps:"
print_warning "1. Configure DNS records for api.c0r.ai, ml.c0r.ai, pay.c0r.ai to point to this server's IP"
print_warning "2. Run: sudo certbot --nginx -d api.c0r.ai -d ml.c0r.ai -d pay.c0r.ai"
print_warning "3. Build and start services: docker-compose build && docker-compose up -d"
print_warning "4. Test all endpoints and functionality"
echo ""
print_status "Setup script completed!"

# Save useful commands for reference
cat > ~/c0r-ai-commands.txt << 'EOF'
# Useful commands for c0r.ai management

# Check service status
docker-compose ps
docker-compose logs -f

# Restart services
docker-compose restart

# Update and rebuild
git pull
docker-compose build
docker-compose up -d

# Check nginx status
sudo nginx -t
sudo systemctl status nginx
sudo systemctl reload nginx

# Check SSL certificates
sudo certbot certificates
sudo certbot renew --dry-run

# Monitor logs
tail -f /var/log/nginx/c0r.ai_access.log
tail -f /var/log/nginx/c0r.ai_error.log

# Check firewall
sudo ufw status

# System monitoring
htop
df -h
docker system df

# Health checks
curl https://api.c0r.ai/health
curl https://ml.c0r.ai/health  
curl https://pay.c0r.ai/health
EOF

print_status "Useful commands saved to ~/c0r-ai-commands.txt" 