# Database Migration Plan - c0r.ai to MODERA.FASHION

## Date: 2025-01-26
## Purpose: Plan database migration from nutrition to fashion service

## Migration Strategy

### Phase 1: Schema Preparation
1. Create new tables for fashion functionality
2. Keep existing tables for backward compatibility
3. Add new columns to existing tables where needed

### Phase 2: Data Migration
1. Migrate user data (keep core user information)
2. Transform nutrition profiles to fashion profiles
3. Archive nutrition-specific data

### Phase 3: Cleanup
1. Remove nutrition-specific tables
2. Optimize indexes for fashion queries
3. Update constraints and relationships

## Migration Script

```sql
-- ==========================================
-- MODERA.FASHION DATABASE MIGRATION
-- ==========================================
-- Version: v1.0.0
-- Date: 2025-01-26
-- Purpose: Transform c0r.ai nutrition service to MODERA.FASHION

-- ==========================================
-- PHASE 1: CREATE NEW TABLES
-- ==========================================

-- Create fashion profiles table
CREATE TABLE IF NOT EXISTS fashion_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body_type TEXT CHECK (body_type IN ('hourglass', 'rectangle', 'triangle', 'inverted_triangle', 'oval')),
    height REAL CHECK (height > 0 AND height < 300),
    weight REAL CHECK (weight > 0 AND weight < 1000),
    preferred_style TEXT[],
    color_preferences TEXT[],
    budget_range TEXT DEFAULT 'mid_range' CHECK (budget_range IN ('budget', 'mid_range', 'premium', 'luxury')),
    occasion_preferences TEXT[],
    size_preferences JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create virtual fittings table
CREATE TABLE IF NOT EXISTS virtual_fittings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    clothing_image_url TEXT NOT NULL,
    person_image_url TEXT NOT NULL,
    result_image_url TEXT,
    status TEXT DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed', 'cancelled')),
    model_used TEXT,
    processing_time REAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create style recommendations table
CREATE TABLE IF NOT EXISTS style_recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recommendation_type TEXT NOT NULL CHECK (recommendation_type IN ('outfit', 'item', 'accessory')),
    items JSONB NOT NULL, -- Array of recommended items with links
    style_description TEXT,
    occasion TEXT,
    total_price REAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create e-commerce items table
CREATE TABLE IF NOT EXISTS ecommerce_items (
    id SERIAL PRIMARY KEY,
    item_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL CHECK (price > 0),
    currency TEXT DEFAULT 'RUB',
    category TEXT NOT NULL,
    subcategory TEXT,
    brand TEXT,
    sizes JSONB,
    colors JSONB,
    images JSONB,
    purchase_url TEXT NOT NULL,
    affiliate_code TEXT,
    retailer TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user style preferences table
CREATE TABLE IF NOT EXISTS user_style_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    preference_type TEXT NOT NULL,
    preference_value TEXT NOT NULL,
    weight REAL DEFAULT 1.0 CHECK (weight > 0 AND weight <= 10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- PHASE 2: UPDATE EXISTING TABLES
-- ==========================================

-- Add fashion-specific columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS fashion_credits_remaining INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS style_preferences JSONB;

-- Update logs table to include fashion actions
ALTER TABLE logs DROP CONSTRAINT IF EXISTS chk_logs_action_type;
ALTER TABLE logs ADD CONSTRAINT chk_logs_action_type CHECK (
    action_type IN (
        'start', 'help', 'status', 'buy', 'photo_analysis', 
        'recipe_generation', 'profile_update', 'calorie_calculation',
        'language_change',
        -- New fashion actions
        'virtual_fitting', 'style_analysis', 'style_recommendation',
        'fashion_profile_update', 'ecommerce_click'
    )
);

-- ==========================================
-- PHASE 3: CREATE INDEXES
-- ==========================================

-- Fashion profiles indexes
CREATE INDEX IF NOT EXISTS idx_fashion_profiles_user_id ON fashion_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_fashion_profiles_body_type ON fashion_profiles(body_type);
CREATE INDEX IF NOT EXISTS idx_fashion_profiles_budget_range ON fashion_profiles(budget_range);

-- Virtual fittings indexes
CREATE INDEX IF NOT EXISTS idx_virtual_fittings_user_id ON virtual_fittings(user_id);
CREATE INDEX IF NOT EXISTS idx_virtual_fittings_status ON virtual_fittings(status);
CREATE INDEX IF NOT EXISTS idx_virtual_fittings_created_at ON virtual_fittings(created_at);

-- Style recommendations indexes
CREATE INDEX IF NOT EXISTS idx_style_recommendations_user_id ON style_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_style_recommendations_type ON style_recommendations(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_style_recommendations_created_at ON style_recommendations(created_at);

-- E-commerce items indexes
CREATE INDEX IF NOT EXISTS idx_ecommerce_items_category ON ecommerce_items(category);
CREATE INDEX IF NOT EXISTS idx_ecommerce_items_brand ON ecommerce_items(brand);
CREATE INDEX IF NOT EXISTS idx_ecommerce_items_price ON ecommerce_items(price);
CREATE INDEX IF NOT EXISTS idx_ecommerce_items_retailer ON ecommerce_items(retailer);

-- User style preferences indexes
CREATE INDEX IF NOT EXISTS idx_user_style_preferences_user_id ON user_style_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_style_preferences_type ON user_style_preferences(preference_type);

-- ==========================================
-- PHASE 4: CREATE VIEWS
-- ==========================================

-- Fashion activity summary view
CREATE OR REPLACE VIEW fashion_activity_summary AS
SELECT 
    u.telegram_id,
    u.fashion_credits_remaining,
    u.total_paid,
    u.language,
    u.country,
    u.created_at,
    COUNT(l.id) as total_actions,
    COUNT(CASE WHEN l.action_type = 'virtual_fitting' THEN 1 END) as virtual_fittings,
    COUNT(CASE WHEN l.action_type = 'style_recommendation' THEN 1 END) as style_recommendations,
    COUNT(CASE WHEN l.action_type = 'ecommerce_click' THEN 1 END) as ecommerce_clicks,
    MAX(l.timestamp) as last_activity
FROM users u
LEFT JOIN logs l ON u.id = l.user_id
GROUP BY u.id, u.telegram_id, u.fashion_credits_remaining, u.total_paid, u.language, u.country, u.created_at;

-- ==========================================
-- PHASE 5: DATA MIGRATION
-- ==========================================

-- Migrate existing users to have fashion credits
UPDATE users 
SET fashion_credits_remaining = credits_remaining 
WHERE fashion_credits_remaining = 0;

-- Create fashion profiles for existing users (with default values)
INSERT INTO fashion_profiles (user_id, body_type, budget_range)
SELECT 
    id as user_id,
    'rectangle' as body_type,
    'mid_range' as budget_range
FROM users 
WHERE id NOT IN (SELECT user_id FROM fashion_profiles);

-- ==========================================
-- PHASE 6: CLEANUP (OPTIONAL - AFTER TESTING)
-- ==========================================

-- Archive nutrition-specific data (optional)
-- CREATE TABLE archived_nutrition_profiles AS SELECT * FROM user_profiles;
-- DROP TABLE user_profiles;

-- Remove nutrition-specific constraints (optional)
-- ALTER TABLE logs DROP CONSTRAINT IF EXISTS chk_logs_action_type_old;

-- ==========================================
-- COMMENTS AND DOCUMENTATION
-- ==========================================

COMMENT ON TABLE fashion_profiles IS 'Fashion profiles for MODERA.FASHION users';
COMMENT ON TABLE virtual_fittings IS 'Virtual fitting sessions and results';
COMMENT ON TABLE style_recommendations IS 'AI-generated style recommendations';
COMMENT ON TABLE ecommerce_items IS 'E-commerce items for recommendations';
COMMENT ON TABLE user_style_preferences IS 'User style preferences for AI recommendations';

COMMENT ON COLUMN fashion_profiles.body_type IS 'User body type for fitting recommendations';
COMMENT ON COLUMN fashion_profiles.budget_range IS 'User budget range for recommendations';
COMMENT ON COLUMN virtual_fittings.status IS 'Status of virtual fitting processing';
COMMENT ON COLUMN style_recommendations.items IS 'JSON array of recommended items with purchase links';
COMMENT ON COLUMN ecommerce_items.affiliate_code IS 'Affiliate tracking code for commission';
```

## Rollback Plan

```sql
-- Rollback script (if needed)
-- DROP TABLE IF EXISTS user_style_preferences;
-- DROP TABLE IF EXISTS ecommerce_items;
-- DROP TABLE IF EXISTS style_recommendations;
-- DROP TABLE IF EXISTS virtual_fittings;
-- DROP TABLE IF EXISTS fashion_profiles;
-- ALTER TABLE users DROP COLUMN IF EXISTS fashion_credits_remaining;
-- ALTER TABLE users DROP COLUMN IF EXISTS style_preferences;
```

## Testing Strategy

1. **Backup Database:** Create full backup before migration
2. **Test Environment:** Run migration on test database first
3. **Data Validation:** Verify all user data is preserved
4. **Performance Testing:** Check query performance with new indexes
5. **Rollback Testing:** Test rollback procedure

## Migration Checklist

- [ ] Create database backup
- [ ] Run migration on test environment
- [ ] Validate data integrity
- [ ] Test application functionality
- [ ] Update application code
- [ ] Deploy to production
- [ ] Monitor for issues
- [ ] Clean up old tables (after validation) 