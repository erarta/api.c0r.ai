# Health Check System Documentation

## Overview

The c0r.AI project implements a comprehensive health check system that provides monitoring and observability for all services. The system checks service health, dependency status, and provides detailed diagnostic information for operations and debugging.

## Architecture

### Core Components

1. **Enhanced Health Module** (`shared/health.py`)
   - Centralized health check functionality
   - Dependency checking capabilities
   - Standardized response formats

2. **Service Health Endpoints**
   - API Service: `GET /` and `GET /health`
   - ML Service: `GET /` and `GET /health`
   - Payment Service: `GET /` and `GET /health`

3. **Dependency Checks**
   - Database connectivity (Supabase)
   - External service availability
   - OpenAI API connectivity
   - Configuration validation

## Health Status Levels

The system uses three health status levels:

- **`healthy`** - Service and all dependencies are functioning normally
- **`degraded`** - Service is functional but some non-critical dependencies have issues
- **`unhealthy`** - Service or critical dependencies are not functioning

## Health Response Format

All health endpoints return a standardized JSON response:

```json
{
  "service": "api.c0r.ai",
  "status": "healthy",
  "timestamp": "2025-07-21T20:30:00.000Z",
  "version": "0.3.61",
  "dependencies": {
    "database": {
      "status": "healthy",
      "response_time_ms": 45.2
    },
    "ml_service": {
      "status": "healthy",
      "response_time_ms": 120.5
    }
  },
  "ml_service_configured": true,
  "pay_service_configured": true,
  "r2_enabled": true
}
```

## Service-Specific Health Checks

### API Service (`api.c0r.ai`)

**Endpoint:** `GET /` or `GET /health`

**Dependencies Checked:**
- Database connectivity (Supabase)
- ML service availability (if configured)
- Payment service availability (if configured)

**Additional Information:**
- ML service configuration status
- Payment service configuration status
- R2 storage enablement status

**Example Response:**
```json
{
  "service": "api.c0r.ai",
  "status": "healthy",
  "timestamp": "2025-07-21T20:30:00.000Z",
  "version": "0.3.61",
  "dependencies": {
    "database": {
      "status": "healthy",
      "response_time_ms": 45.2
    },
    "ml_service": {
      "status": "healthy",
      "response_time_ms": 120.5
    },
    "pay_service": {
      "status": "healthy",
      "response_time_ms": 89.3
    }
  },
  "ml_service_configured": true,
  "pay_service_configured": true,
  "r2_enabled": true
}
```

### ML Service (`ml.c0r.ai`)

**Endpoint:** `GET /` or `GET /health`

**Dependencies Checked:**
- Database connectivity (Supabase)
- OpenAI API connectivity (if configured)

**Additional Information:**
- OpenAI API configuration status
- Gemini API configuration status
- Default ML provider

**Example Response:**
```json
{
  "service": "ml.c0r.ai",
  "status": "healthy",
  "timestamp": "2025-07-21T20:30:00.000Z",
  "version": "0.3.61",
  "dependencies": {
    "database": {
      "status": "healthy",
      "response_time_ms": 45.2
    },
    "openai": {
      "status": "healthy",
      "response_time_ms": 234.7
    }
  },
  "openai_configured": true,
  "gemini_configured": false,
  "default_provider": "openai"
}
```

### Payment Service (`pay.c0r.ai`)

**Endpoint:** `GET /` or `GET /health`

**Dependencies Checked:**
- Database connectivity (Supabase)
- API service availability (if configured)

**Additional Information:**
- API service configuration status
- YooKassa configuration status
- Stripe configuration status
- Available payment plans

**Example Response:**
```json
{
  "service": "pay.c0r.ai",
  "status": "healthy",
  "timestamp": "2025-07-21T20:30:00.000Z",
  "version": "0.3.61",
  "dependencies": {
    "database": {
      "status": "healthy",
      "response_time_ms": 45.2
    },
    "api_service": {
      "status": "healthy",
      "response_time_ms": 67.8
    }
  },
  "api_service_configured": true,
  "yookassa_configured": true,
  "stripe_configured": true,
  "available_plans": ["basic", "premium", "pro"]
}
```

## Dependency Check Types

### Database Health Check

Validates Supabase database connectivity by performing a simple query.

```python
async def check_database_health() -> DependencyCheck:
    # Performs: SELECT id FROM users LIMIT 1
    # Returns: DependencyCheck with status and response time
```

### External Service Health Check

Validates external service availability via HTTP requests.

```python
async def check_external_service_health(service_name: str, url: str) -> DependencyCheck:
    # Performs: GET request to service URL
    # Returns: DependencyCheck with status and response time
```

### OpenAI API Health Check

Validates OpenAI API connectivity and authentication.

```python
async def check_openai_health() -> DependencyCheck:
    # Performs: GET https://api.openai.com/v1/models
    # Returns: DependencyCheck with status and response time
```

## Usage Examples

### Basic Health Check

```python
from shared.health import create_health_response

# Simple health response
response = create_health_response("api")
```

### Comprehensive Health Check

```python
from shared.health import create_comprehensive_health_response

# Full health check with dependencies
response = await create_comprehensive_health_response(
    service_name="api",
    check_database=True,
    check_external_services={"ml_service": "https://ml.c0r.ai/"},
    additional_info={"custom_field": "value"}
)
```

### Custom Dependency Check

```python
from shared.health import DependencyCheck, HealthStatus

# Create custom dependency check
custom_check = DependencyCheck(
    name="custom_service",
    status=HealthStatus.HEALTHY,
    response_time=0.123,
    error=None
)
```

## Monitoring Integration

### Prometheus Metrics

Health check endpoints can be scraped by Prometheus for monitoring:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'c0r-ai-services'
    static_configs:
      - targets: ['api.c0r.ai', 'ml.c0r.ai', 'pay.c0r.ai']
    metrics_path: '/health'
    scrape_interval: 30s
```

### Uptime Monitoring

Use external monitoring services to check health endpoints:

```bash
# Check all services
curl -f https://api.c0r.ai/health
curl -f https://ml.c0r.ai/health
curl -f https://pay.c0r.ai/health
```

### Load Balancer Health Checks

Configure load balancers to use health endpoints:

```nginx
# nginx.conf
upstream api_backend {
    server api1.c0r.ai:8000;
    server api2.c0r.ai:8000;
}

location /health {
    access_log off;
    return 200 "healthy\n";
    add_header Content-Type text/plain;
}
```

## Error Scenarios

### Database Connection Failure

```json
{
  "service": "api.c0r.ai",
  "status": "unhealthy",
  "dependencies": {
    "database": {
      "status": "unhealthy",
      "error": "Connection timeout"
    }
  }
}
```

### External Service Unavailable

```json
{
  "service": "api.c0r.ai",
  "status": "unhealthy",
  "dependencies": {
    "ml_service": {
      "status": "unhealthy",
      "error": "HTTP 503",
      "response_time_ms": 5000.0
    }
  }
}
```

### Partial Service Degradation

```json
{
  "service": "ml.c0r.ai",
  "status": "degraded",
  "dependencies": {
    "database": {
      "status": "healthy",
      "response_time_ms": 45.2
    },
    "openai": {
      "status": "degraded",
      "response_time_ms": 8000.0
    }
  }
}
```

## Testing

### Unit Tests

Run health check unit tests:

```bash
python -m pytest tests/unit/test_health_checks.py -v
```

### Integration Tests

Run health endpoint integration tests:

```bash
python -m pytest tests/integration/test_health_endpoints.py -v
```

### Manual Testing

Test health endpoints manually:

```bash
# Test API service
curl -s https://api.c0r.ai/health | jq .

# Test ML service
curl -s https://ml.c0r.ai/health | jq .

# Test Payment service
curl -s https://pay.c0r.ai/health | jq .
```

## Configuration

### Environment Variables

Health checks respect these environment variables:

- `SERVICE_VERSION` - Service version included in health response
- `ML_SERVICE_URL` - ML service URL for API service health checks
- `PAY_SERVICE_URL` - Payment service URL for API service health checks
- `API_SERVICE_URL` - API service URL for payment service health checks
- `OPENAI_API_KEY` - OpenAI API key for ML service health checks
- `YOOKASSA_SHOP_ID` - YooKassa configuration for payment service
- `STRIPE_SECRET_KEY` - Stripe configuration for payment service

### Timeouts

Default timeouts for dependency checks:

- Database check: 5 seconds
- External service check: 5 seconds
- OpenAI API check: 10 seconds

## Best Practices

### 1. Regular Monitoring

- Set up automated monitoring of all health endpoints
- Configure alerts for unhealthy status
- Monitor response times for performance degradation

### 2. Graceful Degradation

- Services should continue operating when non-critical dependencies fail
- Use `degraded` status for partial functionality
- Provide clear error messages in dependency checks

### 3. Security Considerations

- Health endpoints don't require authentication (public monitoring)
- Don't expose sensitive information in health responses
- Log health check failures for security monitoring

### 4. Performance

- Health checks should be lightweight and fast
- Cache dependency check results when appropriate
- Use appropriate timeouts to prevent hanging

## Troubleshooting

### Common Issues

1. **Database Connection Failures**
   - Check Supabase credentials and network connectivity
   - Verify database service status
   - Check connection pool limits

2. **External Service Timeouts**
   - Verify service URLs and network connectivity
   - Check service authentication and authorization
   - Monitor service response times

3. **OpenAI API Issues**
   - Verify API key configuration
   - Check API quota and rate limits
   - Monitor OpenAI service status

### Debug Commands

```bash
# Check service logs
docker logs api-service
docker logs ml-service
docker logs pay-service

# Test database connectivity
psql -h your-supabase-host -U postgres -d your-database -c "SELECT 1;"

# Test external service connectivity
curl -v https://ml.c0r.ai/health
curl -v https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
```

## Migration from Legacy Health Checks

The new health check system replaces simple status responses with comprehensive dependency monitoring. Legacy endpoints continue to work but provide enhanced information.

### Before (Legacy)
```json
{"status": "ok", "service": "api.c0r.ai"}
```

### After (Enhanced)
```json
{
  "service": "api.c0r.ai",
  "status": "healthy",
  "timestamp": "2025-07-21T20:30:00.000Z",
  "version": "0.3.61",
  "dependencies": {...},
  "additional_info": {...}
}
```

All existing monitoring and alerting systems will continue to work, with additional diagnostic information now available.