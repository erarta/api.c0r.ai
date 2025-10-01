# Fix Production Food Plan Generation Issue

## Problem Analysis
Food plan generation is failing on production with error:
```
Food plan API error: 404 {"detail":"Not Found"}
```

The bot is trying to call `/food-plan/generate-internal` endpoint but getting 404.

## Root Cause
After investigation:
1. ✅ The endpoint `/food-plan/generate-internal` exists in code (`services/api/public/routers/food_plan.py:123`)
2. ✅ The endpoint works locally (tested with curl)
3. ✅ Authentication is configured correctly (`INTERNAL_API_TOKEN`)
4. ❌ The `api_public` service is not running on production

## Solution
The `api_public` service needs to be started on production server.

### Steps to Fix (run on production server):

1. **Check current containers:**
```bash
docker ps
```

2. **If api_public is missing, start it:**
```bash
cd /path/to/project
docker-compose -f docker-compose.production.yml up -d api_public
```

3. **Or restart all services:**
```bash
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d
```

4. **Verify api_public is running:**
```bash
docker ps | grep api_public
```

5. **Check api_public logs:**
```bash
docker logs apic0rai-api_public-1
```

6. **Test the endpoint:**
```bash
curl -X POST "http://localhost:8020/food-plan/generate-internal" \
  -H "Content-Type: application/json" \
  -H "X-Internal-Token: test-token-12345-for-testing-purposes-only" \
  -d '{"user_id": "test", "days": 3, "force": true}'
```

## Verification
After fixing, test food plan generation in the bot:
1. Send `/start` to the bot
2. Click on food plan generation
3. Should generate plan successfully instead of showing error

## Technical Details
- Bot service calls: `http://api_public:8020/food-plan/generate-internal`
- This requires `api_public` container to be running and accessible on port 8020
- The containers communicate via Docker network `c0r-network`