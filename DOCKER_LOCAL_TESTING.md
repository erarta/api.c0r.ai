# 🐳 Local Docker Testing Guide

## Quick Start

To test your Docker setup locally, run:

```bash
./scripts/test-docker-local.sh
```

This script will automatically:
- ✅ Check all prerequisites (Docker, Docker Compose)
- 🔧 Build all containers
- 🚀 Start all services
- 🔍 Test each service endpoint
- 📊 Show resource usage and logs
- 🩺 Run health checks

## What Gets Tested

### Services Tested:
- **API Service** (port 8000) - Main Telegram bot API
- **ML Service** (port 8001) - Machine learning for food analysis  
- **Pay Service** (port 8002) - Payment processing

### Health Checks:
- Container build status
- Service startup time
- Endpoint responsiveness
- Error-free logs
- Resource usage monitoring

## Manual Testing Commands

If you prefer manual testing:

### 1. Build and Start
```bash
# Using docker-compose
docker-compose build --no-cache
docker-compose up -d

# OR using docker compose (newer syntax)
docker compose build --no-cache
docker compose up -d
```

### 2. Check Status
```bash
# See all containers
docker-compose ps

# View logs
docker-compose logs -f

# Check specific service
docker-compose logs api
```

### 3. Test Endpoints
```bash
# Test API service
curl http://localhost:8000/

# Test ML service
curl http://localhost:8001/

# Test Pay service
curl http://localhost:8002/
```

### 4. Monitor Resources
```bash
# Real-time resource monitoring
docker stats

# Single snapshot
docker stats --no-stream
```

### 5. Cleanup
```bash
# Stop all services
docker-compose down

# Remove everything including volumes
docker-compose down -v

# Clean up images and cache
docker system prune -f
```

## Troubleshooting

### Common Issues:

#### 🔴 Port Already in Use
```bash
# Find what's using the port
lsof -i :8000

# Kill the process
kill -9 <PID>
```

#### 🔴 Container Build Fails
```bash
# Check Docker daemon
docker info

# Clean build cache
docker builder prune -f

# Rebuild from scratch
docker-compose build --no-cache --pull
```

#### 🔴 Service Won't Start
```bash
# Check logs for errors
docker-compose logs <service_name>

# Check .env file exists
ls -la .env

# Restart specific service
docker-compose restart <service_name>
```

#### 🔴 Out of Memory/Disk Space
```bash
# Check Docker disk usage
docker system df

# Clean up everything
docker system prune -a -f --volumes

# Remove unused images
docker image prune -a -f
```

### Environment Setup

Make sure you have:

#### Required Files:
- `.env` file with proper configuration
- `docker-compose.yml` in project root
- All service Dockerfiles present

#### Example .env content:
```env
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token

# Payment Services
STRIPE_SECRET_KEY=your_stripe_key
YOOKASSA_SECRET_KEY=your_yookassa_key

# Environment
ENVIRONMENT=development
DEBUG=true
```

## Performance Testing

### Resource Monitoring:
```bash
# Monitor in real-time
watch docker stats

# Log resource usage
docker stats --no-stream >> docker_stats.log
```

### Load Testing:
```bash
# Simple load test for API
for i in {1..100}; do
  curl -s http://localhost:8000/ &
done
wait
```

### Memory Profiling:
```bash
# Check memory usage per container
docker stats --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}"
```

## Integration with Development

### Hot Reload Setup:
Mount your source code for development:

```yaml
# In docker-compose.override.yml
services:
  api:
    volumes:
      - ./api.c0r.ai/app:/app
    environment:
      - DEBUG=true
```

### Database Testing:
```bash
# Connect to database container
docker-compose exec postgres psql -U postgres

# Run database migrations
docker-compose exec api python manage.py migrate
```

## Automated Testing Integration

The Docker testing integrates with our CI/CD pipeline:

### Local Testing Before Commit:
```bash
# Run all tests
./scripts/test-docker-local.sh

# Run unit tests
python -m pytest tests/unit/ -v

# Run integration tests  
python -m pytest tests/integration/ -v
```

### Production Readiness:
- All services must start successfully
- All endpoints must respond within 30 seconds
- No error logs during startup
- Resource usage within acceptable limits

## Best Practices

### 🔄 Development Workflow:
1. Make code changes
2. Run local Docker tests
3. Run unit/integration tests
4. Commit and push (triggers CI/CD)

### 🚀 Deployment Preparation:
1. Test locally with production-like .env
2. Verify all services work together
3. Check resource usage is reasonable
4. Test with actual API keys (carefully)

### 🛠️ Maintenance:
- Clean up Docker resources weekly: `docker system prune -f`
- Update base images regularly
- Monitor resource usage trends
- Keep .env.example updated

## Next Steps

After successful local testing:
1. ✅ All services start and respond
2. ✅ No errors in logs
3. ✅ Resource usage is acceptable
4. 🚀 Ready for deployment to staging/production

## Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Run the automated testing script
3. Check service logs: `docker-compose logs <service>`
4. Verify .env configuration
5. Test individual containers: `docker run -it <image> /bin/bash` 