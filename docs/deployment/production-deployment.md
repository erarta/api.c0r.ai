# Production Deployment Guide

## 🚀 Deployment Process with Migrations

### Pre-Deployment Checklist

1. **Code Review & Testing**
   ```bash
   # Run all tests
   python -m pytest tests/ -v
   
   # Check code quality
   flake8 .
   black --check .
   ```

2. **Database Backup**
   ```bash
   # Create backup before deployment
   pg_dump -h your-supabase-host -U postgres -d your-database > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

3. **Migration Preparation**
   ```bash
   # Check for new migrations
   ls -la migrations/database/
   
   # Verify rollback scripts exist
   ls -la migrations/rollbacks/
   ```

### Deployment Steps

#### Step 1: Stop Services (if needed)
```bash
# For zero-downtime deployment, skip this step
# For maintenance window deployment:
docker-compose down
```

#### Step 2: Run Database Migrations
```bash
# Connect to production database
psql -h your-supabase-host -d your-database -U postgres

# Check current migration status
SELECT * FROM migration_history ORDER BY applied_at DESC LIMIT 5;

# Run new migrations in order
\i migrations/database/2025-07-21_new_migration.sql

# Verify migration success
\dt  -- List tables
\d table_name  -- Describe specific table
```

#### Step 3: Deploy Application Code
```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Restart services
docker-compose up -d
```

#### Step 4: Verify Deployment
```bash
# Check service health
curl -f https://api.c0r.ai/health
curl -f https://ml.c0r.ai/health
curl -f https://pay.c0r.ai/health

# Check logs
docker-compose logs -f api
docker-compose logs -f ml
docker-compose logs -f pay
```

### Migration Management

#### Creating New Migrations

1. **Create Migration File**
   ```bash
   # Create new migration
   touch migrations/database/$(date +%Y-%m-%d)_description.sql
   
   # Create corresponding rollback
   touch migrations/rollbacks/$(date +%Y-%m-%d)_description_rollback.sql
   ```

2. **Migration Template**
   ```sql
   -- migrations/database/2025-07-22_add_feature.sql
   -- Description: Add new feature to database
   -- Date: 2025-07-22
   -- Author: Developer Name
   
   BEGIN;
   
   -- Your migration code here
   CREATE TABLE new_feature (
       id SERIAL PRIMARY KEY,
       name VARCHAR(255) NOT NULL,
       created_at TIMESTAMP DEFAULT NOW()
   );
   
   -- Update migration history
   INSERT INTO migration_history (migration_name, applied_at, description)
   VALUES ('2025-07-22_add_feature', NOW(), 'Add new feature to database');
   
   COMMIT;
   ```

3. **Rollback Template**
   ```sql
   -- migrations/rollbacks/2025-07-22_add_feature_rollback.sql
   -- Rollback for: Add new feature to database
   -- Date: 2025-07-22
   
   BEGIN;
   
   -- Rollback changes
   DROP TABLE IF EXISTS new_feature;
   
   -- Remove from migration history
   DELETE FROM migration_history WHERE migration_name = '2025-07-22_add_feature';
   
   COMMIT;
   ```

#### Migration History Tracking

Create migration tracking table:
```sql
-- Run once to set up migration tracking
CREATE TABLE IF NOT EXISTS migration_history (
    id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT NOW(),
    description TEXT,
    rollback_available BOOLEAN DEFAULT TRUE
);
```

### Rollback Procedure

If deployment fails:

1. **Immediate Rollback**
   ```bash
   # Rollback database changes
   psql -h your-supabase-host -d your-database -U postgres \
        -f migrations/rollbacks/2025-07-22_add_feature_rollback.sql
   
   # Rollback application code
   git checkout previous-stable-tag
   docker-compose up -d
   ```

2. **Verify Rollback**
   ```bash
   # Check services
   curl -f https://api.c0r.ai/health
   
   # Check database state
   psql -h your-supabase-host -d your-database -U postgres \
        -c "SELECT * FROM migration_history ORDER BY applied_at DESC LIMIT 5;"
   ```

### Zero-Downtime Deployment

For production systems requiring zero downtime:

1. **Blue-Green Deployment**
   ```bash
   # Deploy to green environment
   docker-compose -f docker-compose.green.yml up -d
   
   # Run migrations (compatible with both versions)
   psql -f migrations/database/compatible_migration.sql
   
   # Switch traffic to green
   # Update load balancer configuration
   
   # Stop blue environment
   docker-compose -f docker-compose.blue.yml down
   ```

2. **Rolling Updates**
   ```bash
   # Update services one by one
   docker-compose up -d --no-deps api
   sleep 30
   docker-compose up -d --no-deps ml
   sleep 30
   docker-compose up -d --no-deps pay
   ```

### Environment-Specific Considerations

#### Development
```bash
# Quick migration for development
python scripts/run_migrations.py --env=dev
```

#### Staging
```bash
# Full deployment simulation
python scripts/run_migrations.py --env=staging --dry-run
python scripts/run_migrations.py --env=staging
```

#### Production
```bash
# Production deployment with all checks
python scripts/run_migrations.py --env=production --backup --verify
```

### Monitoring & Alerts

Set up monitoring for:
- Migration execution time
- Database connection health
- Service startup success
- Error rates post-deployment

### Emergency Procedures

#### Database Corruption
```bash
# Restore from backup
psql -h your-supabase-host -d your-database -U postgres < backup_20250722_120000.sql

# Verify data integrity
python scripts/verify_database_integrity.py
```

#### Service Failure
```bash
# Check logs
docker-compose logs --tail=100 service-name

# Restart specific service
docker-compose restart service-name

# Full system restart
docker-compose down && docker-compose up -d
```

### Best Practices

1. **Always test migrations in staging first**
2. **Create database backups before production deployment**
3. **Use feature flags for new functionality**
4. **Monitor system health during and after deployment**
5. **Have rollback plan ready before starting deployment**
6. **Document all changes in CHANGELOG.md**
7. **Notify team of deployment schedule**

### Automation Scripts

Create deployment automation:
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

ENV=${1:-staging}
echo "Deploying to $ENV environment..."

# Pre-deployment checks
./scripts/pre_deploy_checks.sh $ENV

# Backup database
./scripts/backup_database.sh $ENV

# Run migrations
./scripts/run_migrations.sh $ENV

# Deploy application
./scripts/deploy_application.sh $ENV

# Post-deployment verification
./scripts/post_deploy_checks.sh $ENV

echo "Deployment to $ENV completed successfully!"