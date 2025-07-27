# MODERA.FASHION Database Migration Script

**Date:** 2025-01-27  
**Purpose:** Complete database schema for MODERA.FASHION service  
**Migration Type:** Full schema creation for new Supabase project  

## Migration Overview

This migration creates a complete database schema for MODERA.FASHION, designed for fashion AI services including virtual try-on and AI styling features.

## SQL Migration Script

### 1. Enable Required Extensions

```sql
-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable PostgreSQL crypto functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enable full-text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

### 2. Core User Management

#### Users Table (Enhanced for Fashion)
```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10) DEFAULT 'en',
    credits INTEGER DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0,
    
    -- Fashion-specific fields
    style_profile JSONB DEFAULT '{}',
    body_measurements JSONB DEFAULT '{}',
    preferences JSONB DEFAULT '{}',
    size_preferences JSONB DEFAULT '{}',
    
    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    is_premium BOOLEAN DEFAULT FALSE,
    last_activity TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_language_code ON users(language_code);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_last_activity ON users(last_activity);

-- Comments for clarity
COMMENT ON TABLE users IS 'User accounts and profiles for MODERA.FASHION';
COMMENT ON COLUMN users.style_profile IS 'AI-generated style analysis and preferences';
COMMENT ON COLUMN users.body_measurements IS 'Body type and measurement data';
COMMENT ON COLUMN users.preferences IS 'User fashion preferences and settings';
COMMENT ON COLUMN users.size_preferences IS 'Preferred sizes across different brands';
```

### 3. Fashion Session Management

#### Fashion Sessions Table
```sql
CREATE TABLE fashion_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    session_type VARCHAR(20) NOT NULL CHECK (session_type IN ('tryon', 'styling')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'processing', 'completed', 'failed', 'expired')),
    
    -- Session data
    input_data JSONB DEFAULT '{}',
    result_data JSONB DEFAULT '{}',
    processing_metadata JSONB DEFAULT '{}',
    
    -- Resource tracking
    credits_used INTEGER DEFAULT 0,
    processing_time INTEGER, -- seconds
    ai_model_used VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    started_processing_at TIMESTAMP,
    completed_at TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '30 minutes')
);

-- Indexes
CREATE INDEX idx_fashion_sessions_user_id ON fashion_sessions(user_id);
CREATE INDEX idx_fashion_sessions_type ON fashion_sessions(session_type);
CREATE INDEX idx_fashion_sessions_status ON fashion_sessions(status);
CREATE INDEX idx_fashion_sessions_created_at ON fashion_sessions(created_at);
CREATE INDEX idx_fashion_sessions_expires_at ON fashion_sessions(expires_at);

-- Comments
COMMENT ON TABLE fashion_sessions IS 'User sessions for virtual try-on and AI styling';
COMMENT ON COLUMN fashion_sessions.input_data IS 'User input data (images, preferences, etc.)';
COMMENT ON COLUMN fashion_sessions.result_data IS 'AI processing results and recommendations';
COMMENT ON COLUMN fashion_sessions.processing_metadata IS 'Technical metadata about AI processing';
```

### 4. Virtual Try-On System

#### Virtual Try-Ons Table
```sql
CREATE TABLE virtual_tryons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES fashion_sessions(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    
    -- Input images
    clothing_image_url TEXT NOT NULL,
    person_image_url TEXT NOT NULL,
    clothing_image_metadata JSONB DEFAULT '{}',
    person_image_metadata JSONB DEFAULT '{}',
    
    -- Output results
    result_image_url TEXT,
    result_image_metadata JSONB DEFAULT '{}',
    
    -- AI analysis
    fit_analysis JSONB DEFAULT '{}',
    quality_score DECIMAL(3,2) CHECK (quality_score >= 0 AND quality_score <= 1),
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- User feedback
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_feedback TEXT,
    user_saved BOOLEAN DEFAULT FALSE,
    user_shared BOOLEAN DEFAULT FALSE,
    
    -- Resource tracking
    credits_used INTEGER DEFAULT 3,
    processing_time INTEGER,
    ai_model_version VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_virtual_tryons_session_id ON virtual_tryons(session_id);
CREATE INDEX idx_virtual_tryons_user_id ON virtual_tryons(user_id);
CREATE INDEX idx_virtual_tryons_created_at ON virtual_tryons(created_at);
CREATE INDEX idx_virtual_tryons_quality_score ON virtual_tryons(quality_score);
CREATE INDEX idx_virtual_tryons_user_rating ON virtual_tryons(user_rating);

-- Comments
COMMENT ON TABLE virtual_tryons IS 'Virtual try-on sessions and results';
COMMENT ON COLUMN virtual_tryons.fit_analysis IS 'AI analysis of how clothing fits the person';
COMMENT ON COLUMN virtual_tryons.quality_score IS 'AI-assessed quality of the generated image (0-1)';
COMMENT ON COLUMN virtual_tryons.confidence_score IS 'AI confidence in the result (0-1)';
```

### 5. AI Styling System

#### Style Analyses Table
```sql
CREATE TABLE style_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES fashion_sessions(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    
    -- Input data
    input_image_url TEXT NOT NULL,
    input_image_metadata JSONB DEFAULT '{}',
    user_preferences JSONB DEFAULT '{}',
    
    -- AI analysis results
    style_profile JSONB NOT NULL DEFAULT '{}',
    body_analysis JSONB DEFAULT '{}',
    color_analysis JSONB DEFAULT '{}',
    style_recommendations JSONB DEFAULT '{}',
    
    -- Analysis metadata
    confidence_scores JSONB DEFAULT '{}',
    analysis_version VARCHAR(50),
    
    -- User interaction
    user_feedback JSONB DEFAULT '{}',
    user_accepted_recommendations INTEGER DEFAULT 0,
    
    -- Resource tracking
    credits_used INTEGER DEFAULT 5,
    processing_time INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_style_analyses_session_id ON style_analyses(session_id);
CREATE INDEX idx_style_analyses_user_id ON style_analyses(user_id);
CREATE INDEX idx_style_analyses_created_at ON style_analyses(created_at);

-- Comments
COMMENT ON TABLE style_analyses IS 'AI style analysis sessions and results';
COMMENT ON COLUMN style_analyses.style_profile IS 'Comprehensive AI-generated style profile';
COMMENT ON COLUMN style_analyses.body_analysis IS 'Body type and measurement analysis';
COMMENT ON COLUMN style_analyses.color_analysis IS 'Personal color palette analysis';
COMMENT ON COLUMN style_analyses.style_recommendations IS 'AI-generated style recommendations';
```

#### Product Recommendations Table
```sql
CREATE TABLE product_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    style_analysis_id UUID REFERENCES style_analyses(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    
    -- Product information
    product_id VARCHAR(255) NOT NULL,
    partner_name VARCHAR(100) NOT NULL,
    product_url TEXT NOT NULL,
    product_data JSONB NOT NULL DEFAULT '{}',
    
    -- Recommendation metadata
    recommendation_score DECIMAL(3,2) CHECK (recommendation_score >= 0 AND recommendation_score <= 1),
    recommendation_reason TEXT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    
    -- User interaction tracking
    user_viewed BOOLEAN DEFAULT FALSE,
    user_clicked BOOLEAN DEFAULT FALSE,
    user_saved BOOLEAN DEFAULT FALSE,
    user_purchased BOOLEAN DEFAULT FALSE,
    
    -- Affiliate tracking
    affiliate_commission DECIMAL(10,2),
    commission_rate DECIMAL(5,4),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    first_viewed_at TIMESTAMP,
    clicked_at TIMESTAMP,
    purchased_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_product_recommendations_style_analysis_id ON product_recommendations(style_analysis_id);
CREATE INDEX idx_product_recommendations_user_id ON product_recommendations(user_id);
CREATE INDEX idx_product_recommendations_partner_name ON product_recommendations(partner_name);
CREATE INDEX idx_product_recommendations_category ON product_recommendations(category);
CREATE INDEX idx_product_recommendations_user_clicked ON product_recommendations(user_clicked);
CREATE INDEX idx_product_recommendations_user_purchased ON product_recommendations(user_purchased);

-- Comments
COMMENT ON TABLE product_recommendations IS 'AI-generated product recommendations';
COMMENT ON COLUMN product_recommendations.product_data IS 'Complete product information from partner API';
COMMENT ON COLUMN product_recommendations.recommendation_score IS 'AI confidence in recommendation (0-1)';
COMMENT ON COLUMN product_recommendations.recommendation_reason IS 'Human-readable explanation for recommendation';
```

### 6. Payment and Credit System

#### Credit Transactions Table
```sql
CREATE TABLE credit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    
    -- Transaction details
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('purchase', 'usage', 'refund', 'bonus', 'expired')),
    credits_amount INTEGER NOT NULL,
    credits_balance_after INTEGER NOT NULL,
    
    -- Payment information (for purchases)
    cost_amount DECIMAL(10,2),
    currency VARCHAR(3),
    payment_provider VARCHAR(20),
    payment_id VARCHAR(255),
    payment_status VARCHAR(20),
    
    -- Usage information (for usage transactions)
    feature_used VARCHAR(50),
    session_id UUID REFERENCES fashion_sessions(id),
    
    -- Metadata
    description TEXT,
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX idx_credit_transactions_type ON credit_transactions(transaction_type);
CREATE INDEX idx_credit_transactions_payment_provider ON credit_transactions(payment_provider);
CREATE INDEX idx_credit_transactions_created_at ON credit_transactions(created_at);
CREATE INDEX idx_credit_transactions_session_id ON credit_transactions(session_id);

-- Comments
COMMENT ON TABLE credit_transactions IS 'All credit-related transactions (purchases, usage, refunds)';
COMMENT ON COLUMN credit_transactions.credits_balance_after IS 'User credit balance after this transaction';
COMMENT ON COLUMN credit_transactions.feature_used IS 'Which feature consumed credits (tryon, styling, etc.)';
```

#### Payment Invoices Table
```sql
CREATE TABLE payment_invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    
    -- Invoice details
    invoice_id VARCHAR(255) UNIQUE NOT NULL,
    payment_provider VARCHAR(20) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    
    -- Credit package information
    credits_amount INTEGER NOT NULL,
    package_type VARCHAR(50) NOT NULL,
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'cancelled', 'expired', 'refunded')),
    
    -- Payment URLs and metadata
    payment_url TEXT,
    webhook_data JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    paid_at TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '1 hour')
);

-- Indexes
CREATE INDEX idx_payment_invoices_user_id ON payment_invoices(user_id);
CREATE INDEX idx_payment_invoices_invoice_id ON payment_invoices(invoice_id);
CREATE INDEX idx_payment_invoices_status ON payment_invoices(status);
CREATE INDEX idx_payment_invoices_payment_provider ON payment_invoices(payment_provider);
CREATE INDEX idx_payment_invoices_created_at ON payment_invoices(created_at);

-- Comments
COMMENT ON TABLE payment_invoices IS 'Payment invoices for credit purchases';
COMMENT ON COLUMN payment_invoices.package_type IS 'Credit package type (basic, premium)';
COMMENT ON COLUMN payment_invoices.webhook_data IS 'Payment provider webhook data';
```

### 7. Analytics and Reporting

#### User Analytics Table
```sql
CREATE TABLE user_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    
    -- Date tracking
    date DATE NOT NULL,
    
    -- Usage metrics
    sessions_count INTEGER DEFAULT 0,
    tryons_count INTEGER DEFAULT 0,
    stylings_count INTEGER DEFAULT 0,
    credits_used INTEGER DEFAULT 0,
    credits_purchased INTEGER DEFAULT 0,
    
    -- Engagement metrics
    time_spent_seconds INTEGER DEFAULT 0,
    features_used JSONB DEFAULT '{}',
    user_ratings JSONB DEFAULT '{}',
    
    -- Revenue metrics
    revenue_generated DECIMAL(10,2) DEFAULT 0,
    affiliate_commissions DECIMAL(10,2) DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Unique constraint to prevent duplicates
    UNIQUE(user_id, date)
);

-- Indexes
CREATE INDEX idx_user_analytics_user_id ON user_analytics(user_id);
CREATE INDEX idx_user_analytics_date ON user_analytics(date);
CREATE INDEX idx_user_analytics_created_at ON user_analytics(created_at);

-- Comments
COMMENT ON TABLE user_analytics IS 'Daily user activity and engagement analytics';
COMMENT ON COLUMN user_analytics.features_used IS 'JSON object tracking which features were used';
COMMENT ON COLUMN user_analytics.user_ratings IS 'JSON object with rating distributions';
```

### 8. System Configuration

#### System Settings Table
```sql
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value JSONB NOT NULL,
    setting_type VARCHAR(50) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert default settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, description) VALUES
('credit_packages_rub', '{"basic": {"credits": 50, "price": 299, "currency": "RUB"}, "premium": {"credits": 150, "price": 799, "currency": "RUB"}}', 'payment', 'Credit packages for Russian market'),
('credit_packages_usd', '{"basic": {"credits": 50, "price": 4.99, "currency": "USD"}, "premium": {"credits": 150, "price": 12.99, "currency": "USD"}}', 'payment', 'Credit packages for international market'),
('credit_costs', '{"tryon": 3, "styling": 5, "recommendations": 2}', 'credits', 'Credit costs for different features'),
('ai_model_settings', '{"dalle_version": "dall-e-3", "gpt4_vision": "gpt-4-vision-preview", "gemini_version": "gemini-pro-vision"}', 'ai', 'AI model versions and settings'),
('session_timeout_minutes', '30', 'system', 'Session timeout in minutes'),
('max_image_size_mb', '10', 'system', 'Maximum image upload size in MB');

-- Comments
COMMENT ON TABLE system_settings IS 'System-wide configuration settings';
```

### 9. Database Functions and Triggers

#### Update User Credits Function
```sql
CREATE OR REPLACE FUNCTION update_user_credits(
    p_user_id BIGINT,
    p_credits_change INTEGER,
    p_transaction_type VARCHAR(20),
    p_feature_used VARCHAR(50) DEFAULT NULL,
    p_session_id UUID DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    new_balance INTEGER;
BEGIN
    -- Update user credits
    UPDATE users 
    SET credits = credits + p_credits_change,
        updated_at = NOW()
    WHERE id = p_user_id
    RETURNING credits INTO new_balance;
    
    -- Record transaction
    INSERT INTO credit_transactions (
        user_id, 
        transaction_type, 
        credits_amount, 
        credits_balance_after,
        feature_used,
        session_id
    ) VALUES (
        p_user_id, 
        p_transaction_type, 
        p_credits_change, 
        new_balance,
        p_feature_used,
        p_session_id
    );
    
    RETURN new_balance;
END;
$$ LANGUAGE plpgsql;

-- Comments
COMMENT ON FUNCTION update_user_credits IS 'Safely update user credits and record transaction';
```

#### Auto-update Timestamps Trigger
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 10. Row Level Security (RLS) Policies

#### Enable RLS on User Tables
```sql
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE fashion_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE virtual_tryons ENABLE ROW LEVEL SECURITY;
ALTER TABLE style_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_analytics ENABLE ROW LEVEL SECURITY;

-- Create policies (example for users table)
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid()::text = telegram_id::text);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid()::text = telegram_id::text);

-- Note: Additional RLS policies should be created based on specific security requirements
```

### 11. Initial Data and Indexes

#### Performance Indexes
```sql
-- Composite indexes for common queries
CREATE INDEX idx_fashion_sessions_user_type_status ON fashion_sessions(user_id, session_type, status);
CREATE INDEX idx_virtual_tryons_user_created ON virtual_tryons(user_id, created_at DESC);
CREATE INDEX idx_style_analyses_user_created ON style_analyses(user_id, created_at DESC);
CREATE INDEX idx_credit_transactions_user_type_created ON credit_transactions(user_id, transaction_type, created_at DESC);

-- Full-text search indexes
CREATE INDEX idx_product_recommendations_search ON product_recommendations USING gin(to_tsvector('english', product_data::text));
```

## Migration Execution Instructions

### 1. Pre-Migration Checklist
- [ ] Create new Supabase project for MODERA.FASHION
- [ ] Ensure PostgreSQL version 14+ is available
- [ ] Backup any existing data (if applicable)
- [ ] Verify required extensions are available

### 2. Execution Steps
1. **Connect to Supabase:** Use Supabase SQL editor or psql client
2. **Run Extensions:** Execute extension creation commands first
3. **Create Tables:** Run table creation commands in order
4. **Create Functions:** Execute function definitions
5. **Create Triggers:** Set up automated triggers
6. **Enable RLS:** Configure row-level security
7. **Create Indexes:** Add performance indexes
8. **Insert Settings:** Add default system settings

### 3. Post-Migration Verification
```sql
-- Verify all tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check table relationships
SELECT 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';

-- Verify system settings
SELECT setting_key, setting_type, is_active FROM system_settings;
```

### 4. Rollback Script (if needed)
```sql
-- WARNING: This will delete all data
DROP TABLE IF EXISTS user_analytics CASCADE;
DROP TABLE IF EXISTS system_settings CASCADE;
DROP TABLE IF EXISTS payment_invoices CASCADE;
DROP TABLE IF EXISTS credit_transactions CASCADE;
DROP TABLE IF EXISTS product_recommendations CASCADE;
DROP TABLE IF EXISTS style_analyses CASCADE;
DROP TABLE IF EXISTS virtual_tryons CASCADE;
DROP TABLE IF EXISTS fashion_sessions CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS update_user_credits CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;
```

## Schema Summary

### Table Count: 8 core tables
1. **users** - User accounts and profiles
2. **fashion_sessions** - Session management
3. **virtual_tryons** - Try-on results and data
4. **style_analyses** - AI styling analysis
5. **product_recommendations** - Product suggestions
6. **credit_transactions** - Payment and usage tracking
7. **payment_invoices** - Payment processing
8. **user_analytics** - Usage analytics
9. **system_settings** - Configuration management

### Key Features
- **Complete audit trail** for all user actions
- **Flexible JSONB storage** for AI results and metadata
- **Comprehensive indexing** for performance
- **Row-level security** for data protection
- **Automated triggers** for data consistency
- **Credit system** with transaction tracking
- **Multi-currency support** (RUB/USD)
- **Analytics foundation** for business intelligence

---

**Migration Status:** Ready for execution on new Supabase project for MODERA.FASHION service.