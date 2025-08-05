# Hot-Reload Development Workflow

This guide explains how to use the fast development setup with automatic code reloading to avoid slow Docker rebuilds.

## 🚀 Quick Start

### Option 1: Use Development Script (Recommended)
```bash
# Run the automated development setup
./scripts/dev-mode.sh
```

### Option 2: Manual Setup
```bash
# Stop containers and start with hot-reload
docker-compose down
docker-compose up -d
```

## 📁 What Gets Hot-Reloaded

The following directories are mounted as volumes and trigger automatic reloads:

- `services/api/` - Telegram bot API service
- `services/ml/` - Machine Learning service  
- `services/pay/` - Payment service
- `shared/` - Shared utilities and contracts
- `common/` - Common database and utility modules
- `i18n/` - Translation files

## 🔄 How It Works

1. **Volume Mounting**: Source code is mounted into containers as read-only volumes
2. **Uvicorn Auto-Reload**: Services run with `--reload` flag to detect file changes
3. **Watch Directories**: Multiple `--reload-dir` flags monitor different code paths
4. **Instant Updates**: Changes trigger automatic service restart (2-3 seconds)

## 💡 Development Tips

### Making Changes
- Edit files directly in your IDE
- Save the file
- Wait 2-3 seconds for auto-reload
- Changes are immediately active

### Monitoring Reloads
```bash
# Watch for reload events
docker-compose logs ml --since="5m" | grep reload

# Check specific service logs
docker-compose logs api --follow
```

### Service Health
```bash
# Check all services
curl -s http://localhost:8000/health | jq '.status'  # API
curl -s http://localhost:8001/health | jq '.status'  # ML
curl -s http://localhost:8002/health | jq '.status'  # Pay
```

## 🔧 Configuration Details

### docker-compose.override.yml
The override file automatically extends `docker-compose.yml` with:
- Volume mounts for source code
- Uvicorn reload configuration
- Environment variables for development

### Reload Command Structure
```bash
python -m uvicorn services.ml.main:app \
  --host 0.0.0.0 \
  --port 8001 \
  --reload \
  --reload-dir /app/services/ml \
  --reload-dir /app/shared \
  --reload-dir /app/common
```

## 🚫 What Doesn't Trigger Reload

- Changes to `Dockerfile`
- Changes to `requirements.txt`
- Changes to environment variables in `.env`
- Changes to `docker-compose.yml`

For these changes, you still need:
```bash
docker-compose build
docker-compose up -d
```

## ⚠️ Important Notes

### Read-Only Volumes
Source code is mounted as read-only (`:ro`) to prevent containers from modifying your local files.

### Development Only
This setup is for development only. Production deployments should use proper Docker builds.

### Memory Usage
Hot-reload keeps Python processes watching file changes, which uses slightly more memory.

## 🐛 Troubleshooting

### Service Won't Reload
```bash
# Check if override file exists
ls -la docker-compose.override.yml

# Restart specific service
docker-compose restart ml

# Check reload logs
docker-compose logs ml | grep -i reload
```

### Performance Issues
```bash
# Reduce log verbosity
export UVICORN_LOG_LEVEL=warning

# Limit reload directories if needed
# Edit docker-compose.override.yml
```

### File Permission Issues
```bash
# Ensure files are readable
chmod -R 644 services/
chmod +x scripts/*.sh
```

## 📊 Performance Comparison

| Method | Time | Use Case |
|--------|------|----------|
| Hot-reload | ~3 seconds | Code changes, prompt updates |
| Container restart | ~10 seconds | Service configuration |
| Full rebuild | ~2-5 minutes | Dependencies, Dockerfile changes |

## 🎯 Use Cases

### Perfect for:
- ✅ Prompt engineering and tuning
- ✅ Algorithm improvements
- ✅ Bug fixes
- ✅ Translation updates
- ✅ API endpoint changes

### Still need rebuild for:
- ❌ New Python packages
- ❌ System dependencies
- ❌ Docker configuration
- ❌ Environment variables

## 🔄 Switching Back to Production Mode

```bash
# Remove override file temporarily
mv docker-compose.override.yml docker-compose.override.yml.bak

# Build and run production containers
docker-compose build
docker-compose up -d

# Restore override for next development session
mv docker-compose.override.yml.bak docker-compose.override.yml
``` 