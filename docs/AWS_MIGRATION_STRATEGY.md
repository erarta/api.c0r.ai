# 🚀 AWS Deployment Migration Strategy

## 📋 Overview

This document outlines how database migrations are handled during AWS deployments and provides guidance for manual migration execution when needed.

## 🔄 Migration Types

### 1. **Automatic Migrations (Deployment Pipeline)**
- **When**: During standard CI/CD deployments to AWS
- **Status**: ❌ **NOT CURRENTLY CONFIGURED**
- **Location**: Would be in deployment pipeline (GitHub Actions, CodePipeline, etc.)

### 2. **Manual Migrations (Current Method)**
- **When**: Developer-initiated, testing, emergency fixes
- **Status**: ✅ **FULLY IMPLEMENTED**
- **Tools**: `run_migration_simple.py`, `run_migration_production.py`

## 🛠️ Manual Migration Process

### Quick Migration Commands

```bash
# Development Database
python3 run_migration_simple.py development [migration_file.sql]

# Production Database (automatic confirmation)
python3 run_migration_production.py [migration_file.sql]

# Custom migration file
python3 run_migration_simple.py development 2025-09-25_rename_meal_to_food.sql
```

### Step-by-Step Manual Process

#### 1. **Pre-Migration Checklist**
```bash
# Verify connection
python3 -c "
import psycopg2
import os
os.environ['DATABASE_URL'] = 'your_database_url_here'
psycopg2.connect(os.environ['DATABASE_URL'])
print('✅ Database connection successful')
"

# Backup critical data (production only)
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### 2. **Execute Migration**
```bash
# Development first
python3 run_migration_simple.py development migration_file.sql

# Test and verify
# Then production
python3 run_migration_production.py migration_file.sql
```

#### 3. **Post-Migration Verification**
```bash
# Built-in verification runs automatically
# Additional manual checks:
psql $DATABASE_URL -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
```

## 🏗️ Setting Up Automatic Migrations on AWS

### Option 1: GitHub Actions (Recommended)

```yaml
# .github/workflows/deploy.yml
name: Deploy with Migrations

on:
  push:
    branches: [ main, production ]

jobs:
  migrate-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install PostgreSQL client
        run: |
          sudo apt-get update
          sudo apt-get install -y postgresql-client

      - name: Run Database Migrations
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          # Run all pending migrations
          python3 run_migration_simple.py production

      - name: Deploy to AWS
        # Your deployment steps here
        run: |
          # AWS deployment commands
          echo "Deploying to AWS..."
```

### Option 2: AWS CodeBuild/CodePipeline

```yaml
# buildspec.yml
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.9
    commands:
      - apt-get update
      - apt-get install -y postgresql-client

  pre_build:
    commands:
      - echo "Running database migrations..."
      - python3 run_migration_simple.py production

  build:
    commands:
      - echo "Building and deploying application..."
      # Your build commands here

  post_build:
    commands:
      - echo "Verifying deployment..."
      # Post-deployment verification
```

### Option 3: ECS/Lambda Pre-Hook

```python
# deploy_hooks.py - Run before application starts
import subprocess
import os

def run_migrations():
    """Run migrations before application startup"""
    try:
        result = subprocess.run([
            'python3', 'run_migration_production.py'
        ], capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            print("✅ Migrations completed successfully")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Migration execution failed: {e}")
        return False

if __name__ == "__main__":
    if not run_migrations():
        exit(1)
```

## 📂 Migration File Organization

```
migrations/
├── database/
│   ├── 2025-09-25_enhanced_nutrition_system.sql     # Main enhancement
│   ├── 2025-09-25_rename_meal_to_food.sql          # Renaming migration
│   └── [YYYY-MM-DD]_description.sql                # Future migrations
├── rollbacks/
│   ├── 2025-09-25_enhanced_nutrition_system_rollback.sql
│   ├── 2025-09-25_rename_meal_to_food_rollback.sql
│   └── [YYYY-MM-DD]_description_rollback.sql
└── scripts/
    ├── run_migration_simple.py                      # Development/manual
    ├── run_migration_production.py                  # Production auto-confirm
    └── migration_helpers/
```

## ⚠️ Emergency Procedures

### Migration Failed During Deployment

```bash
# 1. Immediate rollback
export USE_ENHANCED_AI=false
docker restart [application-containers]

# 2. Database rollback (if needed)
python3 run_migration_simple.py production rollback_file.sql

# 3. Verify system stability
curl $API_URL/health
```

### Partial Migration Success

```bash
# Check what was applied
psql $DATABASE_URL -c "
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name LIKE '%food%' OR table_name LIKE '%nutrition%'
ORDER BY table_name;
"

# Apply remaining parts manually
psql $DATABASE_URL -f remaining_migration_parts.sql
```

## 🔍 Monitoring and Alerting

### Migration Monitoring

```python
# monitoring/migration_tracker.py
import json
import boto3
from datetime import datetime

def log_migration_event(migration_name, status, details=None):
    """Log migration events to CloudWatch"""
    client = boto3.client('logs')

    log_event = {
        'timestamp': datetime.utcnow().isoformat(),
        'migration': migration_name,
        'status': status,  # 'started', 'completed', 'failed', 'rolled_back'
        'details': details or {}
    }

    client.put_log_events(
        logGroupName='/aws/lambda/migrations',
        logStreamName=f"migration-{datetime.now().strftime('%Y/%m/%d')}",
        logEvents=[{
            'timestamp': int(datetime.now().timestamp() * 1000),
            'message': json.dumps(log_event)
        }]
    )
```

### Slack Notifications

```python
# notifications/slack_alerts.py
import requests
import json

def send_migration_alert(webhook_url, migration_name, status, error=None):
    """Send migration alerts to Slack"""

    color = {
        'started': '#36a64f',    # Green
        'completed': '#36a64f',  # Green
        'failed': '#ff0000',     # Red
        'rolled_back': '#ff9900' # Orange
    }.get(status, '#808080')    # Gray default

    payload = {
        'attachments': [{
            'color': color,
            'title': f'Database Migration: {migration_name}',
            'text': f'Status: {status.upper()}',
            'fields': [
                {'title': 'Environment', 'value': 'Production', 'short': True},
                {'title': 'Time', 'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'), 'short': True}
            ]
        }]
    }

    if error:
        payload['attachments'][0]['fields'].append({
            'title': 'Error', 'value': str(error), 'short': False
        })

    requests.post(webhook_url, data=json.dumps(payload))
```

## 📊 Best Practices

### ✅ Do's
- **Always test migrations on development first**
- **Create rollback scripts for every migration**
- **Use transactions (BEGIN/COMMIT) in migration files**
- **Verify migrations with automatic checks**
- **Monitor migration execution time and resource usage**
- **Keep migration files in version control**
- **Use descriptive migration file names with dates**

### ❌ Don'ts
- **Never run migrations directly on production without testing**
- **Don't mix data and schema changes in the same migration**
- **Avoid migrations during peak traffic hours**
- **Don't delete migration files after they've been applied**
- **Never skip migration verification steps**
- **Avoid complex logic in migration scripts**

## 🎯 Current Status Summary

| Component | Status | Details |
|-----------|--------|---------|
| **Manual Migrations** | ✅ **Ready** | Fully tested on dev/prod |
| **Migration Scripts** | ✅ **Complete** | Both simple and production versions |
| **Database Schema** | ✅ **Updated** | Enhanced nutrition system deployed |
| **Rollback Scripts** | ✅ **Available** | Ready for emergency use |
| **Auto-Migrations** | ❌ **Missing** | Need to configure in deployment pipeline |
| **Monitoring** | ⚠️ **Basic** | Manual verification only |

## 🚀 Next Steps for Full Automation

1. **Configure CI/CD Pipeline**
   - Add migration step to GitHub Actions
   - Test with staging environment first

2. **Implement Monitoring**
   - CloudWatch logging for migrations
   - Slack/email alerts for migration events

3. **Create Migration Tracking**
   - Database table to track applied migrations
   - Version control integration

4. **Production Readiness**
   - Blue-green deployment with migration support
   - Automated rollback triggers

## 📞 Emergency Contacts

- **Database Issues**: Check AWS RDS logs and Supabase dashboard
- **Migration Failures**: Use rollback scripts in `/migrations/rollbacks/`
- **Application Issues**: Toggle `USE_ENHANCED_AI=false` for immediate fallback

**Ready to go live with enhanced nutrition system! 🎉**