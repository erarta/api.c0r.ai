# 🚀 Enhanced Nutrition System - Deployment Guide

## Quick Start

### 1. Run Database Migration
```bash
# Set your database URL
export DATABASE_URL="postgresql://postgres.cadeererdjwemspkeriq:xuoO4|LSaaGX5@aws-0-eu-north-1.pooler.supabase.com:6543/postgres"

# Run migrations
python scripts/run_migrations.py --database-url $DATABASE_URL

# Verify migration success
python scripts/run_migrations.py --dry-run --database-url $DATABASE_URL
```

### 2. Configure Environment Variables
```bash
# Essential Enhanced AI Settings
export USE_ENHANCED_AI=true              # Enable AI-powered nutrition system
export DNA_CONFIDENCE_THRESHOLD=0.6      # Minimum confidence for DNA generation
export PREDICTION_HORIZON_DAYS=7         # Days ahead for behavioral predictions

# Optional ML Service
export ML_SERVICE_URL=http://ml-service:8000    # External ML service for advanced analytics
export ML_SERVICE_TIMEOUT=60                    # Timeout for ML service requests

# Feature Flags
export ENABLE_BEHAVIOR_PREDICTION=true    # Predictive analytics for eating behavior
export ENABLE_CONTEXTUAL_ANALYSIS=true    # Context-aware meal recommendations
export ENABLE_VISUALIZATION=true          # Enhanced UI with charts and insights
export COLLECT_ENHANCED_DATA=true         # Store detailed behavioral data
```

### 3. Verify Deployment
```bash
# Test basic functionality
curl $API_URL/health

# Test enhanced nutrition endpoints
curl $API_URL/health/nutrition-dna
curl $API_URL/nutrition-onboarding/questionnaire-summary

# Run full verification
./deploy/post-deploy-verification.sh
```

---

## 🎯 Testing User Stories

### Test 1: New User Onboarding Flow

**Via Telegram Bot:**
1. Send `/start` to your bot
2. Click "🍽️ Create Food Plan"
3. Should see: "⚡ Let's create your perfect nutrition plan!"
4. Choose "🚀 Quick Setup"
5. Answer 5 questions
6. Receive personalized plan with DNA insights

**Expected Results:**
- ✅ No immediate plan generation (onboarding required first)
- ✅ Questionnaire appears with progress tracking
- ✅ Plan includes personalization reasoning
- ✅ User profile marked as `onboarding_completed = true`

### Test 2: Returning User Experience

**Via Telegram Bot:**
1. User who completed onboarding clicks "🍽️ Create Food Plan"
2. Should see immediate generation: "🧠 Generating personalized plan..."
3. Receive plan with archetype-specific messaging

**Expected Results:**
- ✅ No questionnaire (skips directly to generation)
- ✅ Plan includes DNA archetype information
- ✅ Recommendations respect dietary restrictions and preferences

### Test 3: API Integration Test

**Direct API Testing:**
```bash
# Get questionnaire structure
curl -X GET "$API_URL/nutrition-onboarding/questionnaire" \
     -H "Authorization: Bearer $TOKEN"

# Submit sample responses
curl -X POST "$API_URL/nutrition-onboarding/responses" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{
       "responses": [
         {
           "question_id": "primary_goal",
           "value": "weight_loss",
           "timestamp": "2025-09-25T10:00:00Z"
         }
       ]
     }'

# Check onboarding status
curl -X POST "$API_URL/nutrition-onboarding/check-profile-internal" \
     -H "Content-Type: application/json" \
     -H "X-Internal-Auth: $INTERNAL_TOKEN" \
     -d '{"user_id": "test-user-123"}'
```

---

## 🗄️ Database Verification

### Check Migration Status
```sql
-- Verify migration tracking
SELECT filename, status, applied_at
FROM schema_migrations
WHERE filename LIKE '%enhanced_nutrition%';

-- Check new tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_name IN (
  'nutrition_dna',
  'meal_recommendations',
  'nutrition_questionnaire_responses',
  'user_food_analysis_enhanced'
);

-- Verify user_profiles enhancements
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'user_profiles'
  AND column_name IN (
    'onboarding_completed',
    'favorite_foods',
    'cooking_skill',
    'social_eating_frequency'
  );
```

### Sample Data Validation
```sql
-- Check if questionnaire responses are being stored
SELECT COUNT(*), question_id
FROM nutrition_questionnaire_responses
GROUP BY question_id;

-- Verify nutrition DNA generation
SELECT archetype, confidence_score, COUNT(*)
FROM nutrition_dna
GROUP BY archetype, confidence_score;

-- Check meal recommendations quality
SELECT AVG(user_feedback), COUNT(*)
FROM meal_recommendations
WHERE user_feedback IS NOT NULL;
```

---

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 1. Migration Fails
```bash
# Check database connectivity
python3 -c "import psycopg2; psycopg2.connect('$DATABASE_URL'); print('✅ Connected')"

# View migration logs
python scripts/run_migrations.py --database-url $DATABASE_URL --verbose

# Manual rollback if needed
python scripts/run_migrations.py --rollback "2025-09-25_enhanced_nutrition_system.sql" --database-url $DATABASE_URL
```

#### 2. API Endpoints Not Responding
```bash
# Check if enhanced AI is enabled
echo $USE_ENHANCED_AI

# Verify application restart after migration
curl $API_URL/health

# Check application logs for errors
docker logs [container-name] | grep -i nutrition
```

#### 3. Bot Integration Issues
```bash
# Test internal API authentication
curl -X POST "$API_URL/nutrition-onboarding/check-profile-internal" \
     -H "X-Internal-Auth: $INTERNAL_TOKEN" \
     -d '{"user_id": "test"}'

# Verify bot can reach public API
# Check API_PUBLIC_URL environment variable in bot service
```

#### 4. Slow Performance
```bash
# Check database query performance
EXPLAIN ANALYZE SELECT * FROM nutrition_dna WHERE user_id = 'test-uuid';

# Verify indexes were created
SELECT indexname, tablename FROM pg_indexes WHERE tablename LIKE '%nutrition%';

# Monitor resource usage
docker stats [container-name]
```

---

## 🔄 Rollback Procedure

### Emergency Rollback
If deployment causes issues:

```bash
# 1. Disable enhanced features immediately
export USE_ENHANCED_AI=false

# 2. Restart application
docker restart [container-name]

# 3. Rollback database if needed
python scripts/run_migrations.py --rollback "2025-09-25_enhanced_nutrition_system.sql" --database-url $DATABASE_URL

# 4. Verify rollback success
curl $API_URL/health
```

### Gradual Rollback
For partial issues:

```bash
# Disable specific features
export ENABLE_BEHAVIOR_PREDICTION=false
export ENABLE_CONTEXTUAL_ANALYSIS=false

# Keep basic personalization
export USE_ENHANCED_AI=true  # Basic DNA profiling still works
```

---

## 📊 Success Metrics

Monitor these metrics after deployment:

### Database Metrics
- **Migration success:** 100% (no failed migrations)
- **Table creation:** All 4 new tables exist
- **Index creation:** All performance indexes applied
- **User profile enhancement:** 20+ new columns added

### Application Metrics
- **API response time:** < 2s for nutrition endpoints
- **DNA generation success:** > 95% (confidence ≥ 0.6)
- **Onboarding completion:** > 80% of new users
- **Error rate:** < 5% for enhanced features

### User Experience Metrics
- **Bot response time:** < 3s for onboarding flow
- **Plan satisfaction:** > 4.0/5.0 stars average
- **Feature adoption:** > 70% use personalized features
- **Retention improvement:** > 25% with personalized plans

---

## 📞 Support & Documentation

- **Feature Documentation:** `docs/enhanced-nutrition-features.md`
- **User Stories:** `docs/user-stories/`
- **API Reference:** Available after deployment at `/docs`
- **Troubleshooting:** `docs/troubleshooting/enhanced-features.md`

For deployment issues, contact the development team with:
1. Error messages and logs
2. Environment configuration
3. Database migration status
4. API response examples

---

## ✅ Deployment Checklist

**Pre-deployment:**
- [ ] Database backup created
- [ ] Environment variables configured
- [ ] Migration scripts tested in staging
- [ ] Team notified of deployment window

**During deployment:**
- [ ] Run pre-deployment migrations
- [ ] Deploy application with new environment variables
- [ ] Run post-deployment verification
- [ ] Monitor application logs and metrics

**Post-deployment:**
- [ ] All verification tests pass
- [ ] Sample user flows tested
- [ ] Monitoring alerts configured
- [ ] Documentation updated
- [ ] Team notified of successful deployment

---

**🎉 Ready to deploy the Enhanced Nutrition System!**

The system will transform your basic food analysis into a comprehensive AI-powered nutrition platform with maximum personalization and user engagement.