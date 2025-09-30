-- Enhanced Nutrition Features Database Schema Migration
-- Adds support for Nutrition DNA, insights, predictions, and enhanced analytics

-- 1. Nutrition DNA Storage
CREATE TABLE IF NOT EXISTS nutrition_dna (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Core DNA Data
    archetype TEXT NOT NULL CHECK (archetype IN (
        'EARLY_BIRD_PLANNER', 'LATE_STARTER_IMPULSIVE', 'STRUCTURED_BALANCED',
        'STRESS_DRIVEN', 'SOCIAL_EATER', 'INTUITIVE_GRAZER',
        'BUSY_PROFESSIONAL', 'WEEKEND_WARRIOR'
    )),
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),

    -- Pattern Analysis
    energy_patterns JSONB NOT NULL DEFAULT '{}',
    social_patterns JSONB NOT NULL DEFAULT '{}',
    temporal_patterns JSONB NOT NULL DEFAULT '{}',

    -- Behavioral Learning
    triggers JSONB NOT NULL DEFAULT '[]',
    success_patterns JSONB NOT NULL DEFAULT '[]',
    optimization_zones JSONB NOT NULL DEFAULT '[]',

    -- Metrics
    diversity_score DECIMAL(3,2) NOT NULL DEFAULT 0.5,
    consistency_score DECIMAL(3,2) NOT NULL DEFAULT 0.5,
    goal_alignment_score DECIMAL(3,2) NOT NULL DEFAULT 0.5,
    data_quality_score DECIMAL(3,2) NOT NULL DEFAULT 0.5,

    -- Metadata
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    version INTEGER NOT NULL DEFAULT 1,

    UNIQUE(user_id) -- One active DNA profile per user
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_nutrition_dna_user_id ON nutrition_dna(user_id);
CREATE INDEX IF NOT EXISTS idx_nutrition_dna_archetype ON nutrition_dna(archetype);
CREATE INDEX IF NOT EXISTS idx_nutrition_dna_updated_at ON nutrition_dna(updated_at);

-- 2. Enhanced User Profiles (extends existing user_profiles table)
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS preferred_cuisines JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS disliked_foods JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS typical_portion_sizes JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS current_phase TEXT,
ADD COLUMN IF NOT EXISTS weekly_targets JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS progress_metrics JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS total_analyses INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_analysis_date DATE,
ADD COLUMN IF NOT EXISTS nutrition_dna_id UUID REFERENCES nutrition_dna(id);

-- 3. Behavioral Insights Storage
CREATE TABLE IF NOT EXISTS behavioral_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    nutrition_dna_id UUID REFERENCES nutrition_dna(id),

    -- Insight Data
    insight_type TEXT NOT NULL CHECK (insight_type IN (
        'daily', 'weekly', 'contextual', 'predictive', 'temporal'
    )),
    insight_text TEXT NOT NULL,
    confidence DECIMAL(3,2) DEFAULT 0.5,

    -- Context
    generated_for_date DATE,
    context_data JSONB DEFAULT '{}',

    -- Status
    is_active BOOLEAN DEFAULT true,
    user_feedback INTEGER CHECK (user_feedback >= 1 AND user_feedback <= 5),
    feedback_text TEXT,

    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_behavioral_insights_user_id ON behavioral_insights(user_id);
CREATE INDEX IF NOT EXISTS idx_behavioral_insights_type ON behavioral_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_behavioral_insights_date ON behavioral_insights(generated_for_date);

-- 4. Behavioral Predictions Storage
CREATE TABLE IF NOT EXISTS behavioral_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    nutrition_dna_id UUID REFERENCES nutrition_dna(id),

    -- Prediction Data
    event TEXT NOT NULL,
    probability DECIMAL(3,2) NOT NULL CHECK (probability >= 0 AND probability <= 1),
    confidence DECIMAL(3,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    recommended_action TEXT NOT NULL,
    optimal_timing TIME,

    -- Context
    prediction_date DATE NOT NULL,
    context_factors JSONB DEFAULT '{}',

    -- Validation
    actual_outcome BOOLEAN, -- null = not yet occurred, true/false = validated
    outcome_recorded_at TIMESTAMP WITH TIME ZONE,
    accuracy_score DECIMAL(3,2), -- calculated after validation

    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_behavioral_predictions_user_id ON behavioral_predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_behavioral_predictions_date ON behavioral_predictions(prediction_date);
CREATE INDEX IF NOT EXISTS idx_behavioral_predictions_event ON behavioral_predictions(event);

-- 5. Enhanced Food Logs (extends existing logs table)
ALTER TABLE logs
ADD COLUMN IF NOT EXISTS meal_type TEXT CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
ADD COLUMN IF NOT EXISTS eating_context TEXT,
ADD COLUMN IF NOT EXISTS mood_before TEXT,
ADD COLUMN IF NOT EXISTS mood_after TEXT,
ADD COLUMN IF NOT EXISTS satisfaction_level INTEGER CHECK (satisfaction_level >= 1 AND satisfaction_level <= 5),
ADD COLUMN IF NOT EXISTS aligned_with_goal BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS matched_typical_pattern BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS was_planned BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS social_context BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS immediate_feedback TEXT,
ADD COLUMN IF NOT EXISTS next_meal_suggestion TEXT,
ADD COLUMN IF NOT EXISTS nutrition_quality_score DECIMAL(3,2) DEFAULT 0.5,
ADD COLUMN IF NOT EXISTS timing_appropriateness DECIMAL(3,2) DEFAULT 0.5;

-- Indexes for enhanced food logs
CREATE INDEX IF NOT EXISTS idx_logs_meal_type ON logs(meal_type);
CREATE INDEX IF NOT EXISTS idx_logs_eating_context ON logs(eating_context);
CREATE INDEX IF NOT EXISTS idx_logs_satisfaction ON logs(satisfaction_level);

-- 6. Meal Recommendations Storage
CREATE TABLE IF NOT EXISTS meal_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    nutrition_dna_id UUID REFERENCES nutrition_dna(id),

    -- Recommendation Data
    meal_type TEXT NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    dish_name TEXT NOT NULL,
    description TEXT,
    reasoning TEXT,
    recommended_time TIME,

    -- Nutrition
    calories INTEGER NOT NULL,
    protein INTEGER NOT NULL,
    fats INTEGER NOT NULL,
    carbs INTEGER NOT NULL,
    fiber INTEGER,

    -- Preparation
    prep_time_minutes INTEGER NOT NULL,
    difficulty_level TEXT CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
    ingredients JSONB DEFAULT '[]',

    -- Personalization Matching
    matches_energy_level BOOLEAN DEFAULT false,
    addresses_typical_craving BOOLEAN DEFAULT false,
    fits_schedule_pattern BOOLEAN DEFAULT false,
    supports_current_goal BOOLEAN DEFAULT false,

    -- User Interaction
    was_used BOOLEAN DEFAULT false,
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_feedback TEXT,

    recommended_for_date DATE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days')
);

CREATE INDEX IF NOT EXISTS idx_meal_recommendations_user_id ON meal_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_meal_recommendations_meal_type ON meal_recommendations(meal_type);
CREATE INDEX IF NOT EXISTS idx_meal_recommendations_date ON meal_recommendations(recommended_for_date);

-- 7. Context Analysis Storage
CREATE TABLE IF NOT EXISTS context_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Analysis Period
    analysis_start_date DATE NOT NULL,
    analysis_end_date DATE NOT NULL,

    -- Context Impact Data
    weather_impact JSONB DEFAULT '{}',
    time_impact JSONB DEFAULT '{}',
    social_impact JSONB DEFAULT '{}',
    location_impact JSONB DEFAULT '{}',

    -- Key Findings
    strongest_influences JSONB DEFAULT '[]',
    context_sensitivity_score DECIMAL(3,2) NOT NULL DEFAULT 0.5,

    -- Recommendations
    contextual_recommendations JSONB DEFAULT '[]',

    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, analysis_start_date, analysis_end_date)
);

CREATE INDEX IF NOT EXISTS idx_context_analysis_user_id ON context_analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_context_analysis_period ON context_analysis(analysis_start_date, analysis_end_date);

-- 8. Enhanced Meal Plans (extends existing meal_plans table)
ALTER TABLE meal_plans
ADD COLUMN IF NOT EXISTS nutrition_dna_id UUID REFERENCES nutrition_dna(id),
ADD COLUMN IF NOT EXISTS daily_insights JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS weekly_insights JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS personalization_data JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS adaptive_suggestions JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS behavioral_predictions JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS context_factors JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS success_probability DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS personalization_level TEXT DEFAULT 'basic' CHECK (personalization_level IN ('basic', 'enhanced', 'maximum'));

-- 9. User Feedback and Learning
CREATE TABLE IF NOT EXISTS user_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Feedback Target
    feedback_type TEXT NOT NULL CHECK (feedback_type IN (
        'meal_recommendation', 'insight', 'prediction', 'meal_plan', 'general'
    )),
    target_id UUID, -- ID of the item being rated

    -- Feedback Data
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    improvement_suggestion TEXT,

    -- Context
    feedback_date DATE NOT NULL DEFAULT CURRENT_DATE,
    context_data JSONB DEFAULT '{}',

    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON user_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_type ON user_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_user_feedback_rating ON user_feedback(rating);

-- 10. Performance Analytics
CREATE TABLE IF NOT EXISTS nutrition_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,

    -- Time Period
    analysis_date DATE NOT NULL,
    period_type TEXT NOT NULL CHECK (period_type IN ('daily', 'weekly', 'monthly')),

    -- Performance Metrics
    goal_progress_score DECIMAL(3,2) DEFAULT 0.5,
    consistency_score DECIMAL(3,2) DEFAULT 0.5,
    diversity_score DECIMAL(3,2) DEFAULT 0.5,
    prediction_accuracy DECIMAL(3,2),
    insight_relevance_score DECIMAL(3,2),

    -- Behavioral Metrics
    trigger_frequency JSONB DEFAULT '{}',
    success_pattern_strength JSONB DEFAULT '{}',
    optimization_zone_progress JSONB DEFAULT '{}',

    -- Engagement Metrics
    recommendations_used INTEGER DEFAULT 0,
    insights_rated INTEGER DEFAULT 0,
    average_feedback_score DECIMAL(3,2),

    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, analysis_date, period_type)
);

CREATE INDEX IF NOT EXISTS idx_nutrition_analytics_user_id ON nutrition_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_nutrition_analytics_date ON nutrition_analytics(analysis_date);
CREATE INDEX IF NOT EXISTS idx_nutrition_analytics_period ON nutrition_analytics(period_type);

-- 11. Trigger to update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to nutrition_dna table
CREATE TRIGGER update_nutrition_dna_updated_at
    BEFORE UPDATE ON nutrition_dna
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 12. Views for easier data access
CREATE OR REPLACE VIEW user_nutrition_summary AS
SELECT
    up.user_id,
    up.age,
    up.gender,
    up.goal,
    up.daily_calories_target,
    nd.archetype,
    nd.confidence_score as dna_confidence,
    nd.diversity_score,
    nd.consistency_score,
    nd.goal_alignment_score,
    nd.generated_at as dna_generated_at,
    up.total_analyses,
    up.last_analysis_date
FROM user_profiles up
LEFT JOIN nutrition_dna nd ON up.nutrition_dna_id = nd.id;

-- View for recent insights
CREATE OR REPLACE VIEW recent_user_insights AS
SELECT
    bi.user_id,
    bi.insight_type,
    bi.insight_text,
    bi.confidence,
    bi.generated_for_date,
    bi.user_feedback,
    bi.created_at
FROM behavioral_insights bi
WHERE bi.is_active = true
    AND (bi.expires_at IS NULL OR bi.expires_at > NOW())
ORDER BY bi.created_at DESC;

-- View for prediction accuracy tracking
CREATE OR REPLACE VIEW prediction_accuracy_stats AS
SELECT
    user_id,
    event,
    COUNT(*) as total_predictions,
    COUNT(CASE WHEN actual_outcome IS NOT NULL THEN 1 END) as validated_predictions,
    AVG(CASE WHEN actual_outcome IS NOT NULL THEN accuracy_score END) as avg_accuracy,
    AVG(probability) as avg_predicted_probability
FROM behavioral_predictions
GROUP BY user_id, event;

-- 13. Sample data cleanup and maintenance functions
CREATE OR REPLACE FUNCTION cleanup_expired_insights()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM behavioral_insights
    WHERE expires_at IS NOT NULL AND expires_at < NOW();

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to update user analysis counts
CREATE OR REPLACE FUNCTION update_user_analysis_stats()
RETURNS VOID AS $$
BEGIN
    UPDATE user_profiles
    SET
        total_analyses = (
            SELECT COUNT(*)
            FROM logs
            WHERE logs.user_id = user_profiles.user_id
                AND logs.action_type = 'photo_analysis'
        ),
        last_analysis_date = (
            SELECT MAX(timestamp::date)
            FROM logs
            WHERE logs.user_id = user_profiles.user_id
                AND logs.action_type = 'photo_analysis'
        );
END;
$$ LANGUAGE plpgsql;

-- 14. Permissions (if using RLS)
-- ALTER TABLE nutrition_dna ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE behavioral_insights ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE behavioral_predictions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE meal_recommendations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE context_analysis ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_feedback ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE nutrition_analytics ENABLE ROW LEVEL SECURITY;

-- Sample RLS policies (uncomment if needed)
-- CREATE POLICY nutrition_dna_user_policy ON nutrition_dna FOR ALL USING (user_id = auth.uid());
-- CREATE POLICY behavioral_insights_user_policy ON behavioral_insights FOR ALL USING (user_id = auth.uid());
-- CREATE POLICY behavioral_predictions_user_policy ON behavioral_predictions FOR ALL USING (user_id = auth.uid());

COMMENT ON TABLE nutrition_dna IS 'Stores personalized nutrition DNA profiles with behavioral patterns and preferences';
COMMENT ON TABLE behavioral_insights IS 'AI-generated insights about user eating behavior';
COMMENT ON TABLE behavioral_predictions IS 'Predictive analytics for future eating behavior';
COMMENT ON TABLE meal_recommendations IS 'Personalized meal recommendations based on DNA and context';
COMMENT ON TABLE context_analysis IS 'Analysis of how external factors affect eating patterns';
COMMENT ON TABLE user_feedback IS 'User feedback on recommendations and insights for continuous learning';
COMMENT ON TABLE nutrition_analytics IS 'Performance metrics and analytics for nutrition system effectiveness';