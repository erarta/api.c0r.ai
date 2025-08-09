-- Create daily_calories table for tracking user's daily calorie consumption
-- This table will store aggregated daily nutrition data for better performance

CREATE TABLE IF NOT EXISTS daily_calories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_calories DECIMAL(10,2) DEFAULT 0,
    total_proteins DECIMAL(10,2) DEFAULT 0,
    total_fats DECIMAL(10,2) DEFAULT 0,
    total_carbohydrates DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure one entry per user per day
    UNIQUE(user_id, date)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_daily_calories_user_date ON daily_calories(user_id, date);
CREATE INDEX IF NOT EXISTS idx_daily_calories_date ON daily_calories(date);

-- Add comment to table
COMMENT ON TABLE daily_calories IS 'Stores daily aggregated calorie consumption for users';
COMMENT ON COLUMN daily_calories.user_id IS 'Reference to users table';
COMMENT ON COLUMN daily_calories.date IS 'Date in YYYY-MM-DD format';
COMMENT ON COLUMN daily_calories.total_calories IS 'Total calories consumed on this date';
COMMENT ON COLUMN daily_calories.total_proteins IS 'Total proteins consumed on this date (grams)';
COMMENT ON COLUMN daily_calories.total_fats IS 'Total fats consumed on this date (grams)';
COMMENT ON COLUMN daily_calories.total_carbohydrates IS 'Total carbohydrates consumed on this date (grams)';

-- Enable Row Level Security (RLS)
ALTER TABLE daily_calories ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE schemaname = 'public' AND tablename = 'daily_calories' 
          AND policyname = 'Users can view their own daily calories'
    ) THEN
        EXECUTE 'CREATE POLICY "Users can view their own daily calories" ON daily_calories
            FOR SELECT USING (auth.uid()::text = user_id::text)';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE schemaname = 'public' AND tablename = 'daily_calories' 
          AND policyname = 'Users can insert their own daily calories'
    ) THEN
        EXECUTE 'CREATE POLICY "Users can insert their own daily calories" ON daily_calories
            FOR INSERT WITH CHECK (auth.uid()::text = user_id::text)';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE schemaname = 'public' AND tablename = 'daily_calories' 
          AND policyname = 'Users can update their own daily calories'
    ) THEN
        EXECUTE 'CREATE POLICY "Users can update their own daily calories" ON daily_calories
            FOR UPDATE USING (auth.uid()::text = user_id::text)';
    END IF;
END$$ LANGUAGE plpgsql;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_daily_calories_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_trigger t
        JOIN pg_class c ON c.oid = t.tgrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE t.tgname = 'update_daily_calories_updated_at'
          AND c.relname = 'daily_calories'
          AND n.nspname = 'public'
    ) THEN
        EXECUTE 'CREATE TRIGGER update_daily_calories_updated_at
            BEFORE UPDATE ON daily_calories
            FOR EACH ROW
            EXECUTE FUNCTION update_daily_calories_updated_at()';
    END IF;
END$$ LANGUAGE plpgsql;