-- ==========================================
-- MODERA.FASHION DATABASE MIGRATION SCRIPT
-- ==========================================
-- Version: v1.0.0
-- Date: 2025-01-26
-- Purpose: Complete database setup for MODERA.FASHION
-- 
-- IMPORTANT: This script creates a COMPLETE NEW DATABASE SCHEMA
-- for MODERA.FASHION. It does NOT modify existing c0r.ai tables.
-- 
-- Run this script on a NEW Supabase project for MODERA.FASHION.
-- ==========================================

-- ==========================================
-- PHASE 1: CREATE CORE TABLES
-- ==========================================

-- Users table (adapted for fashion service)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    credits_remaining INTEGER DEFAULT 0 CHECK (credits_remaining >= 0),
    total_paid INTEGER DEFAULT 0 CHECK (total_paid >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    subscription_type TEXT DEFAULT 'free' CHECK (subscription_type IN ('free', 'basic', 'premium', 'pro')),
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    language TEXT DEFAULT 'en' CHECK (language IN ('en', 'ru')),
    country TEXT,
    phone_number TEXT,
    
    CONSTRAINT chk_users_telegram_id_positive CHECK (telegram_id > 0)
);

-- Fashion profiles (replaces nutrition profiles)
CREATE TABLE IF NOT EXISTS fashion_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    telegram_id BIGINT NOT NULL,
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

-- Virtual fitting sessions
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

-- Style recommendations
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

-- E-commerce items catalog
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

-- User style preferences
CREATE TABLE IF NOT EXISTS user_style_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    preference_type TEXT NOT NULL,
    preference_value TEXT NOT NULL,
    weight REAL DEFAULT 1.0 CHECK (weight > 0 AND weight <= 10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User activity logs (adapted for fashion)
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action_type TEXT NOT NULL CHECK (action_type IN (
        'start', 'help', 'status', 'buy', 'virtual_fitting', 
        'style_analysis', 'style_recommendation', 'profile_update',
        'language_change', 'ecommerce_click', 'fashion_profile_update'
    )),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    details JSONB
);

-- Payments table (reused from c0r.ai)
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL CHECK (amount > 0),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'cancelled')),
    payment_method TEXT CHECK (payment_method IN ('yookassa', 'stripe')),
    external_id TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- ==========================================
-- PHASE 2: CREATE INDEXES FOR PERFORMANCE
-- ==========================================

-- Users indexes
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_telegram_id_unique ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_credits_remaining ON users(credits_remaining);
CREATE INDEX IF NOT EXISTS idx_users_total_paid ON users(total_paid);
CREATE INDEX IF NOT EXISTS idx_users_language ON users(language);
CREATE INDEX IF NOT EXISTS idx_users_subscription_type ON users(subscription_type);

-- Fashion profiles indexes
CREATE INDEX IF NOT EXISTS idx_fashion_profiles_user_id ON fashion_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_fashion_profiles_telegram_id ON fashion_profiles(telegram_id);
CREATE INDEX IF NOT EXISTS idx_fashion_profiles_body_type ON fashion_profiles(body_type);
CREATE INDEX IF NOT EXISTS idx_fashion_profiles_budget_range ON fashion_profiles(budget_range);
CREATE INDEX IF NOT EXISTS idx_fashion_profiles_updated_at ON fashion_profiles(updated_at);

-- Virtual fittings indexes
CREATE INDEX IF NOT EXISTS idx_virtual_fittings_user_id ON virtual_fittings(user_id);
CREATE INDEX IF NOT EXISTS idx_virtual_fittings_status ON virtual_fittings(status);
CREATE INDEX IF NOT EXISTS idx_virtual_fittings_created_at ON virtual_fittings(created_at);
CREATE INDEX IF NOT EXISTS idx_virtual_fittings_model_used ON virtual_fittings(model_used);

-- Style recommendations indexes
CREATE INDEX IF NOT EXISTS idx_style_recommendations_user_id ON style_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_style_recommendations_type ON style_recommendations(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_style_recommendations_created_at ON style_recommendations(created_at);
CREATE INDEX IF NOT EXISTS idx_style_recommendations_occasion ON style_recommendations(occasion);

-- E-commerce items indexes
CREATE INDEX IF NOT EXISTS idx_ecommerce_items_category ON ecommerce_items(category);
CREATE INDEX IF NOT EXISTS idx_ecommerce_items_brand ON ecommerce_items(brand);
CREATE INDEX IF NOT EXISTS idx_ecommerce_items_price ON ecommerce_items(price);
CREATE INDEX IF NOT EXISTS idx_ecommerce_items_retailer ON ecommerce_items(retailer);
CREATE INDEX IF NOT EXISTS idx_ecommerce_items_updated_at ON ecommerce_items(updated_at);

-- User style preferences indexes
CREATE INDEX IF NOT EXISTS idx_user_style_preferences_user_id ON user_style_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_style_preferences_type ON user_style_preferences(preference_type);

-- Logs indexes
CREATE INDEX IF NOT EXISTS idx_logs_user_action_timestamp ON logs(user_id, action_type, timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_action_type ON logs(action_type);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp_desc ON logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_logs_user_timestamp ON logs(user_id, timestamp);

-- Payments indexes
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);
CREATE INDEX IF NOT EXISTS idx_payments_amount ON payments(amount);

-- ==========================================
-- PHASE 3: CREATE VIEWS FOR ANALYTICS
-- ==========================================

-- Fashion activity summary view
CREATE OR REPLACE VIEW fashion_activity_summary AS
SELECT 
    u.telegram_id,
    u.credits_remaining,
    u.total_paid,
    u.language,
    u.country,
    u.created_at,
    u.subscription_type,
    COUNT(l.id) as total_actions,
    COUNT(CASE WHEN l.action_type = 'virtual_fitting' THEN 1 END) as virtual_fittings,
    COUNT(CASE WHEN l.action_type = 'style_recommendation' THEN 1 END) as style_recommendations,
    COUNT(CASE WHEN l.action_type = 'ecommerce_click' THEN 1 END) as ecommerce_clicks,
    COUNT(CASE WHEN l.action_type = 'start' THEN 1 END) as start_commands,
    COUNT(CASE WHEN l.action_type = 'help' THEN 1 END) as help_commands,
    COUNT(CASE WHEN l.action_type = 'status' THEN 1 END) as status_commands,
    COUNT(CASE WHEN l.action_type = 'buy' THEN 1 END) as buy_commands,
    COUNT(CASE WHEN l.action_type = 'language_change' THEN 1 END) as language_changes,
    MAX(l.timestamp) as last_activity
FROM users u
LEFT JOIN logs l ON u.id = l.user_id
GROUP BY u.id, u.telegram_id, u.credits_remaining, u.total_paid, u.language, u.country, u.created_at, u.subscription_type;

-- Virtual fitting statistics view
CREATE OR REPLACE VIEW virtual_fitting_stats AS
SELECT 
    DATE(created_at) as fitting_date,
    status,
    model_used,
    COUNT(*) as total_fittings,
    AVG(processing_time) as avg_processing_time,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_fittings,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_fittings
FROM virtual_fittings
GROUP BY DATE(created_at), status, model_used
ORDER BY fitting_date DESC;

-- Style recommendation statistics view
CREATE OR REPLACE VIEW style_recommendation_stats AS
SELECT 
    DATE(created_at) as recommendation_date,
    recommendation_type,
    occasion,
    COUNT(*) as total_recommendations,
    AVG(total_price) as avg_price,
    COUNT(CASE WHEN total_price > 0 THEN 1 END) as recommendations_with_price
FROM style_recommendations
GROUP BY DATE(created_at), recommendation_type, occasion
ORDER BY recommendation_date DESC;

-- ==========================================
-- PHASE 4: CREATE FUNCTIONS FOR BUSINESS LOGIC
-- ==========================================

-- Function to calculate user engagement score
CREATE OR REPLACE FUNCTION calculate_user_engagement_score(user_telegram_id BIGINT)
RETURNS REAL AS $$
DECLARE
    engagement_score REAL;
    user_actions INTEGER;
    days_since_creation INTEGER;
BEGIN
    -- Get user actions count
    SELECT COUNT(*) INTO user_actions
    FROM logs l
    JOIN users u ON l.user_id = u.id
    WHERE u.telegram_id = user_telegram_id;
    
    -- Get days since user creation
    SELECT EXTRACT(DAY FROM NOW() - u.created_at) INTO days_since_creation
    FROM users u
    WHERE u.telegram_id = user_telegram_id;
    
    -- Calculate engagement score (actions per day)
    IF days_since_creation > 0 THEN
        engagement_score := user_actions::REAL / days_since_creation;
    ELSE
        engagement_score := user_actions::REAL;
    END IF;
    
    RETURN engagement_score;
END;
$$ LANGUAGE plpgsql;

-- Function to get user fashion profile completeness
CREATE OR REPLACE FUNCTION get_profile_completeness(user_telegram_id BIGINT)
RETURNS REAL AS $$
DECLARE
    completeness REAL;
    total_fields INTEGER := 8; -- Total profile fields
    filled_fields INTEGER := 0;
BEGIN
    -- Count filled fields
    SELECT 
        CASE WHEN body_type IS NOT NULL THEN 1 ELSE 0 END +
        CASE WHEN height IS NOT NULL THEN 1 ELSE 0 END +
        CASE WHEN weight IS NOT NULL THEN 1 ELSE 0 END +
        CASE WHEN preferred_style IS NOT NULL AND array_length(preferred_style, 1) > 0 THEN 1 ELSE 0 END +
        CASE WHEN color_preferences IS NOT NULL AND array_length(color_preferences, 1) > 0 THEN 1 ELSE 0 END +
        CASE WHEN budget_range IS NOT NULL THEN 1 ELSE 0 END +
        CASE WHEN occasion_preferences IS NOT NULL AND array_length(occasion_preferences, 1) > 0 THEN 1 ELSE 0 END +
        CASE WHEN size_preferences IS NOT NULL THEN 1 ELSE 0 END
    INTO filled_fields
    FROM fashion_profiles fp
    JOIN users u ON fp.user_id = u.id
    WHERE u.telegram_id = user_telegram_id;
    
    -- Calculate completeness percentage
    completeness := (filled_fields::REAL / total_fields) * 100;
    
    RETURN completeness;
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- PHASE 5: CREATE TRIGGERS FOR DATA INTEGRITY
-- ==========================================

-- Trigger to update fashion_profiles.updated_at
CREATE OR REPLACE FUNCTION update_fashion_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_fashion_profiles_updated_at
    BEFORE UPDATE ON fashion_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_fashion_profiles_updated_at();

-- Trigger to update ecommerce_items.updated_at
CREATE OR REPLACE FUNCTION update_ecommerce_items_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_ecommerce_items_updated_at
    BEFORE UPDATE ON ecommerce_items
    FOR EACH ROW
    EXECUTE FUNCTION update_ecommerce_items_updated_at();

-- ==========================================
-- PHASE 6: INSERT SAMPLE DATA (OPTIONAL)
-- ==========================================

-- Insert sample e-commerce items for testing
INSERT INTO ecommerce_items (item_id, name, description, price, category, brand, purchase_url, retailer) VALUES
('item_001', 'Classic White T-Shirt', 'Premium cotton t-shirt', 2500.00, 'clothing', 'Zara', 'https://zara.com/item001', 'Zara'),
('item_002', 'Blue Jeans', 'Comfortable denim jeans', 4500.00, 'clothing', 'H&M', 'https://hm.com/item002', 'H&M'),
('item_003', 'Black Dress', 'Elegant evening dress', 8500.00, 'clothing', 'COS', 'https://cos.com/item003', 'COS')
ON CONFLICT (item_id) DO NOTHING;

-- ==========================================
-- PHASE 7: COMMENTS AND DOCUMENTATION
-- ==========================================

-- Table comments
COMMENT ON TABLE users IS 'Main users table for MODERA.FASHION';
COMMENT ON TABLE fashion_profiles IS 'Fashion profiles for MODERA.FASHION users';
COMMENT ON TABLE virtual_fittings IS 'Virtual fitting sessions and results';
COMMENT ON TABLE style_recommendations IS 'AI-generated style recommendations';
COMMENT ON TABLE ecommerce_items IS 'E-commerce items catalog for recommendations';
COMMENT ON TABLE user_style_preferences IS 'User style preferences for AI recommendations';
COMMENT ON TABLE logs IS 'User activity logs for MODERA.FASHION';
COMMENT ON TABLE payments IS 'Payment history and transactions';

-- Column comments
COMMENT ON COLUMN users.telegram_id IS 'Unique Telegram user ID';
COMMENT ON COLUMN users.credits_remaining IS 'Remaining credits for virtual fittings and AI stylist';
COMMENT ON COLUMN users.subscription_type IS 'User subscription level: free, basic, premium, pro';
COMMENT ON COLUMN fashion_profiles.body_type IS 'User body type for fitting recommendations';
COMMENT ON COLUMN fashion_profiles.budget_range IS 'User budget range for recommendations';
COMMENT ON COLUMN virtual_fittings.status IS 'Status of virtual fitting processing';
COMMENT ON COLUMN style_recommendations.items IS 'JSON array of recommended items with purchase links';
COMMENT ON COLUMN ecommerce_items.affiliate_code IS 'Affiliate tracking code for commission';
COMMENT ON COLUMN logs.action_type IS 'Type of user action in the system';

-- ==========================================
-- MIGRATION COMPLETE
-- ==========================================

-- Verify all tables were created
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'users', 'fashion_profiles', 'virtual_fittings', 
    'style_recommendations', 'ecommerce_items', 
    'user_style_preferences', 'logs', 'payments'
)
ORDER BY table_name;

-- Verify all indexes were created
SELECT 
    indexname,
    tablename
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN (
    'users', 'fashion_profiles', 'virtual_fittings', 
    'style_recommendations', 'ecommerce_items', 
    'user_style_preferences', 'logs', 'payments'
)
ORDER BY tablename, indexname;

-- ==========================================
-- ROLLBACK SCRIPT (if needed)
-- ==========================================
/*
-- To rollback this migration, run these commands:

-- Drop triggers
DROP TRIGGER IF EXISTS trigger_update_fashion_profiles_updated_at ON fashion_profiles;
DROP TRIGGER IF EXISTS trigger_update_ecommerce_items_updated_at ON ecommerce_items;

-- Drop functions
DROP FUNCTION IF EXISTS update_fashion_profiles_updated_at();
DROP FUNCTION IF EXISTS update_ecommerce_items_updated_at();
DROP FUNCTION IF EXISTS calculate_user_engagement_score(BIGINT);
DROP FUNCTION IF EXISTS get_profile_completeness(BIGINT);

-- Drop views
DROP VIEW IF EXISTS fashion_activity_summary;
DROP VIEW IF EXISTS virtual_fitting_stats;
DROP VIEW IF EXISTS style_recommendation_stats;

-- Drop tables (in reverse order due to foreign keys)
DROP TABLE IF EXISTS user_style_preferences;
DROP TABLE IF EXISTS ecommerce_items;
DROP TABLE IF EXISTS style_recommendations;
DROP TABLE IF EXISTS virtual_fittings;
DROP TABLE IF EXISTS fashion_profiles;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS logs;
DROP TABLE IF EXISTS users;
*/ 