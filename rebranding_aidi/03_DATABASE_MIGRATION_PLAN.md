# План миграции базы данных c0r.ai → AIDI.APP

*Дата создания: 27 января 2025*
*Цель: Детальный план миграции схемы БД от анализа питания к репутации/KYC*

## 📊 Анализ текущей схемы c0r.ai

### Существующие таблицы (сохраняем)
```sql
-- Базовые пользовательские таблицы (адаптируем)
users                    -- ✅ Сохраняем с модификациями
user_profiles            -- ✅ Сохраняем с изменениями полей
credits                  -- ✅ Сохраняем (универсальная система)
payments                 -- ✅ Сохраняем (универсальная система)
schema_migrations        -- ✅ Сохраняем (системная таблица)

-- Таблицы для удаления (специфичны для питания)
nutrition_analyses       -- ❌ Удаляем
recipes                  -- ❌ Удаляем  
daily_stats             -- ❌ Удаляем
food_items              -- ❌ Удаляем
meal_plans              -- ❌ Удаляем
```

### Новые таблицы (создаем)
```sql
-- Основные таблицы AIDI.APP
reputation_analyses      -- ➕ Анализы репутации
deepfake_detections     -- ➕ Детекция дипфейков
reputation_sources      -- ➕ Источники данных для репутации
kyc_verifications       -- ➕ KYC верификации
analysis_reports        -- ➕ Сгенерированные отчеты
```

## 🔄 Пошаговый план миграции

### Этап 1: Подготовка (Pre-migration)

#### 1.1 Создание резервной копии
```bash
# Создание полного бэкапа текущей БД
pg_dump -h [supabase_host] -U [user] -d [database] > c0r_ai_backup_$(date +%Y%m%d).sql

# Создание схемы без данных (для тестирования)
pg_dump -h [supabase_host] -U [user] -d [database] --schema-only > c0r_ai_schema.sql
```

#### 1.2 Анализ зависимостей
```sql
-- Проверка внешних ключей
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
```

### Этап 2: Миграция пользовательских данных

#### 2.1 Обновление таблицы users
```sql
-- Миграция: 2025-01-27_update_users_for_aidi.sql
-- Добавляем новые поля для AIDI.APP

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'Europe/Moscow',
ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS reputation_score INTEGER DEFAULT NULL,
ADD COLUMN IF NOT EXISTS verification_status VARCHAR(50) DEFAULT 'unverified';

-- Создаем индексы для производительности
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_last_activity ON users(last_activity_at);
CREATE INDEX IF NOT EXISTS idx_users_verification_status ON users(verification_status);

-- Комментарии для документации
COMMENT ON COLUMN users.timezone IS 'User timezone for localized timestamps';
COMMENT ON COLUMN users.last_activity_at IS 'Last user activity timestamp';
COMMENT ON COLUMN users.reputation_score IS 'User own reputation score (0-100)';
COMMENT ON COLUMN users.verification_status IS 'KYC verification status: unverified, pending, verified, rejected';
```

#### 2.2 Обновление таблицы user_profiles
```sql
-- Миграция: 2025-01-27_update_user_profiles_for_aidi.sql
-- Адаптируем профили под AIDI.APP

-- Удаляем старые поля, специфичные для питания
ALTER TABLE user_profiles 
DROP COLUMN IF EXISTS dietary_preferences,
DROP COLUMN IF EXISTS health_goals,
DROP COLUMN IF EXISTS activity_level,
DROP COLUMN IF EXISTS daily_calorie_target;

-- Добавляем новые поля для AIDI.APP
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS analysis_preferences JSONB DEFAULT '{"reputation_depth": "basic", "deepfake_sensitivity": "medium"}',
ADD COLUMN IF NOT EXISTS data_retention_days INTEGER DEFAULT 30,
ADD COLUMN IF NOT EXISTS api_access_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS api_key VARCHAR(255) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS usage_statistics JSONB DEFAULT '{"analyses_count": 0, "deepfake_checks": 0}';

-- Обновляем существующие поля
UPDATE user_profiles 
SET notification_settings = '{"reputation_alerts": true, "deepfake_alerts": true, "payment_notifications": true}'
WHERE notification_settings = '{}' OR notification_settings IS NULL;

UPDATE user_profiles 
SET privacy_settings = '{"data_sharing": false, "anonymous_analytics": true, "report_sharing": false}'
WHERE privacy_settings = '{}' OR privacy_settings IS NULL;

-- Создаем индексы
CREATE INDEX IF NOT EXISTS idx_user_profiles_api_key ON user_profiles(api_key) WHERE api_key IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_profiles_subscription ON user_profiles(subscription_type, subscription_expires_at);

-- Комментарии
COMMENT ON COLUMN user_profiles.analysis_preferences IS 'User preferences for reputation and deepfake analysis';
COMMENT ON COLUMN user_profiles.data_retention_days IS 'How long to keep user analysis data (GDPR compliance)';
COMMENT ON COLUMN user_profiles.api_access_enabled IS 'Whether user has API access enabled';
COMMENT ON COLUMN user_profiles.api_key IS 'API key for programmatic access';
COMMENT ON COLUMN user_profiles.usage_statistics IS 'User usage statistics and quotas';
```

### Этап 3: Создание новых таблиц AIDI.APP

#### 3.1 Таблица reputation_analyses
```sql
-- Миграция: 2025-01-27_create_reputation_analyses.sql
CREATE TABLE reputation_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Данные цели анализа
    target_name VARCHAR(255),
    target_phone VARCHAR(50),
    target_email VARCHAR(255),
    target_photo_url TEXT,
    target_social_profiles JSONB DEFAULT '{}', -- {"vk": "id123", "telegram": "@username"}
    
    -- Параметры анализа
    analysis_type VARCHAR(50) NOT NULL CHECK (analysis_type IN ('basic', 'extended', 'deep')),
    search_depth VARCHAR(50) DEFAULT 'standard' CHECK (search_depth IN ('surface', 'standard', 'deep')),
    data_sources JSONB DEFAULT '[]', -- ["social_media", "public_records", "news", "courts"]
    
    -- Статус и результаты
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    
    -- Скоры и метрики
    risk_score INTEGER CHECK (risk_score >= 0 AND risk_score <= 100),
    credibility_score INTEGER CHECK (credibility_score >= 0 AND credibility_score <= 100),
    sentiment_score DECIMAL(3,2) CHECK (sentiment_score >= -1.00 AND sentiment_score <= 1.00),
    activity_score INTEGER CHECK (activity_score >= 0 AND activity_score <= 100),
    
    -- Результаты анализа
    results JSONB DEFAULT '{}',
    summary TEXT,
    recommendations TEXT,
    sources_found INTEGER DEFAULT 0,
    red_flags JSONB DEFAULT '[]',
    positive_indicators JSONB DEFAULT '[]',
    
    -- Техническая информация
    credits_used INTEGER DEFAULT 1,
    processing_time_ms INTEGER,
    ai_model_version VARCHAR(50),
    error_message TEXT,
    
    -- Временные метки
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days')
);

-- Индексы для производительности
CREATE INDEX idx_reputation_analyses_user_id ON reputation_analyses(user_id);
CREATE INDEX idx_reputation_analyses_status ON reputation_analyses(status);
CREATE INDEX idx_reputation_analyses_created_at ON reputation_analyses(created_at DESC);
CREATE INDEX idx_reputation_analyses_target_phone ON reputation_analyses(target_phone) WHERE target_phone IS NOT NULL;
CREATE INDEX idx_reputation_analyses_target_email ON reputation_analyses(target_email) WHERE target_email IS NOT NULL;
CREATE INDEX idx_reputation_analyses_expires_at ON reputation_analyses(expires_at);

-- Комментарии
COMMENT ON TABLE reputation_analyses IS 'Reputation analysis requests and results';
COMMENT ON COLUMN reputation_analyses.risk_score IS 'Overall risk score (0-100, higher = more risky)';
COMMENT ON COLUMN reputation_analyses.credibility_score IS 'Credibility score (0-100, higher = more credible)';
COMMENT ON COLUMN reputation_analyses.sentiment_score IS 'Overall sentiment (-1.0 to 1.0, negative to positive)';
COMMENT ON COLUMN reputation_analyses.expires_at IS 'When this analysis data will be automatically deleted';
```

#### 3.2 Таблица deepfake_detections
```sql
-- Миграция: 2025-01-27_create_deepfake_detections.sql
CREATE TABLE deepfake_detections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Медиафайл информация
    media_url TEXT NOT NULL,
    media_type VARCHAR(20) NOT NULL CHECK (media_type IN ('image', 'video', 'audio')),
    file_size_bytes BIGINT,
    file_format VARCHAR(20),
    duration_seconds DECIMAL(10,3), -- для видео/аудио
    resolution VARCHAR(20), -- "1920x1080"
    frame_rate DECIMAL(6,3), -- для видео
    
    -- Параметры анализа
    analysis_type VARCHAR(50) NOT NULL CHECK (analysis_type IN ('quick', 'standard', 'detailed', 'forensic')),
    detection_models JSONB DEFAULT '[]', -- ["face_detection", "temporal_analysis", "compression_artifacts"]
    
    -- Статус
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    
    -- Результаты детекции
    deepfake_probability DECIMAL(5,4) CHECK (deepfake_probability >= 0.0000 AND deepfake_probability <= 1.0000),
    confidence_score DECIMAL(5,4) CHECK (confidence_score >= 0.0000 AND confidence_score <= 1.0000),
    authenticity_score DECIMAL(5,4) CHECK (authenticity_score >= 0.0000 AND authenticity_score <= 1.0000),
    
    -- Детальные результаты
    detection_details JSONB DEFAULT '{}',
    artifacts_found JSONB DEFAULT '[]',
    technical_analysis JSONB DEFAULT '{}',
    face_analysis JSONB DEFAULT '{}',
    temporal_analysis JSONB DEFAULT '{}',
    
    -- Заключение
    verdict VARCHAR(50) CHECK (verdict IN ('authentic', 'likely_authentic', 'suspicious', 'likely_deepfake', 'deepfake')),
    explanation TEXT,
    recommendations TEXT,
    
    -- Техническая информация
    credits_used INTEGER DEFAULT 1,
    processing_time_ms INTEGER,
    ai_model_version VARCHAR(50),
    error_message TEXT,
    
    -- Временные метки
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days')
);

-- Индексы
CREATE INDEX idx_deepfake_detections_user_id ON deepfake_detections(user_id);
CREATE INDEX idx_deepfake_detections_status ON deepfake_detections(status);
CREATE INDEX idx_deepfake_detections_created_at ON deepfake_detections(created_at DESC);
CREATE INDEX idx_deepfake_detections_media_type ON deepfake_detections(media_type);
CREATE INDEX idx_deepfake_detections_verdict ON deepfake_detections(verdict);
CREATE INDEX idx_deepfake_detections_expires_at ON deepfake_detections(expires_at);

-- Комментарии
COMMENT ON TABLE deepfake_detections IS 'Deepfake detection analysis requests and results';
COMMENT ON COLUMN deepfake_detections.deepfake_probability IS 'Probability that media is a deepfake (0.0-1.0)';
COMMENT ON COLUMN deepfake_detections.confidence_score IS 'Confidence in the detection result (0.0-1.0)';
COMMENT ON COLUMN deepfake_detections.authenticity_score IS 'Probability that media is authentic (0.0-1.0)';
```

#### 3.3 Таблица reputation_sources
```sql
-- Миграция: 2025-01-27_create_reputation_sources.sql
CREATE TABLE reputation_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES reputation_analyses(id) ON DELETE CASCADE,
    
    -- Информация об источнике
    source_type VARCHAR(100) NOT NULL, -- 'vk', 'telegram', 'instagram', 'court_records', 'news', etc.
    source_name VARCHAR(255), -- "VKontakte", "Судебные решения", "РИА Новости"
    source_url TEXT,
    source_category VARCHAR(50), -- 'social_media', 'public_records', 'news', 'professional'
    
    -- Найденные данные
    data_found JSONB DEFAULT '{}',
    content_type VARCHAR(50), -- 'profile', 'post', 'comment', 'article', 'record'
    content_summary TEXT,
    content_date TIMESTAMP WITH TIME ZONE,
    
    -- Анализ данных
    relevance_score DECIMAL(3,2) CHECK (relevance_score >= 0.00 AND relevance_score <= 1.00),
    credibility_score DECIMAL(3,2) CHECK (credibility_score >= 0.00 AND credibility_score <= 1.00),
    sentiment DECIMAL(3,2) CHECK (sentiment >= -1.00 AND sentiment <= 1.00),
    impact_score DECIMAL(3,2) CHECK (impact_score >= 0.00 AND impact_score <= 1.00),
    
    -- Классификация
    risk_indicators JSONB DEFAULT '[]',
    positive_indicators JSONB DEFAULT '[]',
    tags JSONB DEFAULT '[]',
    
    -- Техническая информация
    extraction_method VARCHAR(50), -- 'api', 'scraping', 'manual'
    data_quality VARCHAR(50) DEFAULT 'good' CHECK (data_quality IN ('poor', 'fair', 'good', 'excellent')),
    verification_status VARCHAR(50) DEFAULT 'unverified' CHECK (verification_status IN ('unverified', 'verified', 'disputed')),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы
CREATE INDEX idx_reputation_sources_analysis_id ON reputation_sources(analysis_id);
CREATE INDEX idx_reputation_sources_source_type ON reputation_sources(source_type);
CREATE INDEX idx_reputation_sources_relevance ON reputation_sources(relevance_score DESC);
CREATE INDEX idx_reputation_sources_content_date ON reputation_sources(content_date DESC);

-- Комментарии
COMMENT ON TABLE reputation_sources IS 'Individual data sources found during reputation analysis';
COMMENT ON COLUMN reputation_sources.relevance_score IS 'How relevant this source is to the target person (0.0-1.0)';
COMMENT ON COLUMN reputation_sources.impact_score IS 'How much this source impacts overall reputation (0.0-1.0)';
```

#### 3.4 Таблица kyc_verifications
```sql
-- Миграция: 2025-01-27_create_kyc_verifications.sql
CREATE TABLE kyc_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Информация о верификации
    verification_type VARCHAR(50) NOT NULL CHECK (verification_type IN ('document', 'selfie', 'video', 'biometric')),
    document_type VARCHAR(50), -- 'passport', 'driver_license', 'id_card'
    
    -- Загруженные файлы
    document_front_url TEXT,
    document_back_url TEXT,
    selfie_url TEXT,
    video_url TEXT,
    
    -- Статус верификации
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'approved', 'rejected', 'expired')),
    verification_level VARCHAR(50) DEFAULT 'basic' CHECK (verification_level IN ('basic', 'enhanced', 'premium')),
    
    -- Результаты проверки
    document_authenticity_score DECIMAL(3,2),
    face_match_score DECIMAL(3,2),
    liveness_score DECIMAL(3,2),
    overall_confidence DECIMAL(3,2),
    
    -- Извлеченные данные
    extracted_data JSONB DEFAULT '{}', -- имя, дата рождения, номер документа и т.д.
    verification_details JSONB DEFAULT '{}',
    
    -- Причины отклонения
    rejection_reasons JSONB DEFAULT '[]',
    manual_review_notes TEXT,
    
    -- Техническая информация
    credits_used INTEGER DEFAULT 2,
    processing_time_ms INTEGER,
    ai_model_version VARCHAR(50),
    
    -- Временные метки
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '1 year')
);

-- Индексы
CREATE INDEX idx_kyc_verifications_user_id ON kyc_verifications(user_id);
CREATE INDEX idx_kyc_verifications_status ON kyc_verifications(status);
CREATE INDEX idx_kyc_verifications_verification_type ON kyc_verifications(verification_type);
CREATE INDEX idx_kyc_verifications_expires_at ON kyc_verifications(expires_at);

-- Комментарии
COMMENT ON TABLE kyc_verifications IS 'KYC (Know Your Customer) verification requests and results';
COMMENT ON COLUMN kyc_verifications.document_authenticity_score IS 'How authentic the document appears (0.0-1.0)';
COMMENT ON COLUMN kyc_verifications.face_match_score IS 'How well selfie matches document photo (0.0-1.0)';
COMMENT ON COLUMN kyc_verifications.liveness_score IS 'Liveness detection score for selfie/video (0.0-1.0)';
```

### Этап 4: Удаление старых таблиц

#### 4.1 Безопасное удаление таблиц питания
```sql
-- Миграция: 2025-01-27_cleanup_nutrition_tables.sql
-- ВНИМАНИЕ: Выполнять только после подтверждения успешной миграции!

-- Сначала удаляем внешние ключи
ALTER TABLE nutrition_analyses DROP CONSTRAINT IF EXISTS nutrition_analyses_user_id_fkey;
ALTER TABLE recipes DROP CONSTRAINT IF EXISTS recipes_user_id_fkey;
ALTER TABLE daily_stats DROP CONSTRAINT IF EXISTS daily_stats_user_id_fkey;

-- Создаем архивные таблицы (на случай необходимости восстановления)
CREATE TABLE IF NOT EXISTS _archive_nutrition_analyses AS SELECT * FROM nutrition_analyses;
CREATE TABLE IF NOT EXISTS _archive_recipes AS SELECT * FROM recipes;
CREATE TABLE IF NOT EXISTS _archive_daily_stats AS SELECT * FROM daily_stats;

-- Удаляем основные таблицы
DROP TABLE IF EXISTS nutrition_analyses CASCADE;
DROP TABLE IF EXISTS recipes CASCADE;
DROP TABLE IF EXISTS daily_stats CASCADE;
DROP TABLE IF EXISTS food_items CASCADE;
DROP TABLE IF EXISTS meal_plans CASCADE;

-- Удаляем связанные индексы и триггеры (если остались)
DROP INDEX IF EXISTS idx_nutrition_analyses_user_id;
DROP INDEX IF EXISTS idx_recipes_user_id;
DROP INDEX IF EXISTS idx_daily_stats_user_id;
```

### Этап 5: Обновление системы кредитов

#### 5.1 Адаптация таблицы credits
```sql
-- Миграция: 2025-01-27_update_credits_system.sql
-- Добавляем новые типы транзакций для AIDI.APP

-- Обновляем ограничения для новых типов транзакций
ALTER TABLE credits 
DROP CONSTRAINT IF EXISTS credits_transaction_type_check;

ALTER TABLE credits 
ADD CONSTRAINT credits_transaction_type_check 
CHECK (transaction_type IN (
    'purchase', 'usage', 'refund', 'bonus', 'promotion',
    'reputation_analysis', 'deepfake_detection', 'kyc_verification',
    'api_usage', 'premium_feature'
));

-- Добавляем новые поля
ALTER TABLE credits
ADD COLUMN IF NOT EXISTS service_type VARCHAR(50), -- 'reputation', 'deepfake', 'kyc'
ADD COLUMN IF NOT EXISTS analysis_complexity VARCHAR(50), -- 'basic', 'extended', 'deep'
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- Обновляем существующие записи
UPDATE credits 
SET service_type = 'legacy', 
    metadata = '{"migrated_from": "nutrition_system"}'
WHERE service_type IS NULL;

-- Создаем индексы
CREATE INDEX IF NOT EXISTS idx_credits_service_type ON credits(service_type);
CREATE INDEX IF NOT EXISTS idx_credits_transaction_type ON credits(transaction_type);

-- Комментарии
COMMENT ON COLUMN credits.service_type IS 'Type of service: reputation, deepfake, kyc, api, premium';
COMMENT ON COLUMN credits.analysis_complexity IS 'Complexity level affecting credit cost';
COMMENT ON COLUMN credits.metadata IS 'Additional transaction metadata';
```

### Этап 6: Создание представлений (Views)

#### 6.1 Представления для аналитики
```sql
-- Миграция: 2025-01-27_create_analytics_views.sql

-- Представление для пользовательской статистики
CREATE OR REPLACE VIEW user_analytics AS
SELECT 
    u.id,
    u.telegram_id,
    u.created_at as registration_date,
    u.last_activity_at,
    up.subscription_type,
    
    -- Статистика анализов репутации
    COALESCE(ra_stats.total_analyses, 0) as reputation_analyses_count,
    COALESCE(ra_stats.completed_analyses, 0) as completed_reputation_analyses,
    COALESCE(ra_stats.avg_risk_score, 0) as avg_risk_score,
    
    -- Статистика детекции дипфейков
    COALESCE(df_stats.total_detections, 0) as deepfake_detections_count,
    COALESCE(df_stats.completed_detections, 0) as completed_deepfake_detections,
    COALESCE(df_stats.avg_deepfake_probability, 0) as avg_deepfake_probability,
    
    -- Статистика кредитов
    COALESCE(credit_stats.total_purchased, 0) as total_credits_purchased,
    COALESCE(credit_stats.total_used, 0) as total_credits_used,
    COALESCE(credit_stats.current_balance, 0) as current_credit_balance

FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
LEFT JOIN (
    SELECT 
        user_id,
        COUNT(*) as total_analyses,
        COUNT(*) FILTER (WHERE status = 'completed') as completed_analyses,
        AVG(risk_score) FILTER (WHERE status = 'completed') as avg_risk_score
    FROM reputation_analyses 
    GROUP BY user_id
) ra_stats ON u.id = ra_stats.user_id
LEFT JOIN (
    SELECT 
        user_id,
        COUNT(*) as total_detections,
        COUNT(*) FILTER (WHERE status = 'completed') as completed_detections,
        AVG(deepfake_probability) FILTER (WHERE status = 'completed') as avg_deepfake_probability
    FROM deepfake_detections 
    GROUP BY user_id
) df_stats ON u.id = df_stats.user_id
LEFT JOIN (
    SELECT 
        user_id,
        SUM(amount) FILTER (WHERE transaction_type = 'purchase') as total_purchased,
        SUM(amount) FILTER (WHERE transaction_type LIKE '%usage%' OR transaction_type LIKE '%_analysis' OR transaction_type LIKE '%_detection') as total_used,
        SUM(amount) as current_balance
    FROM credits 
    GROUP BY user_id
) credit_stats ON u.id = credit_stats.user_id;

-- Представление для системной аналитики
CREATE OR REPLACE VIEW system_analytics AS
SELECT 
    -- Общая статистика
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM users WHERE created_at > NOW() - INTERVAL '30 days') as new_users_30d,
    (SELECT COUNT(*) FROM users WHERE last_activity_at > NOW() - INTERVAL '7 days') as active_users_7d,
    
    -- Статистика анализов
    (SELECT COUNT(*) FROM reputation_analyses) as total_reputation_analyses,
    (SELECT COUNT(*) FROM reputation_analyses WHERE created_at > NOW() - INTERVAL '24 hours') as reputation_analyses_24h,
    (SELECT COUNT(*) FROM deepfake_detections) as total_deepfake_detections,
    (SELECT COUNT(*) FROM deepfake_detections WHERE created_at > NOW() - INTERVAL '24 hours') as deepfake_detections_24h,
    
    -- Статистика платежей
    (SELECT COUNT(*) FROM payments WHERE status = 'completed') as successful_payments,
    (SELECT SUM(amount) FROM payments WHERE status = 'completed') as total_revenue,
    (SELECT SUM(amount) FROM payments WHERE status = 'completed' AND created_at > NOW() - INTERVAL '30 days') as revenue_30d;
```

## 🔧 Скрипт автоматической миграции

### Основной скрипт миграции
```python
# scripts/migrate_to_aidi.py
"""
Автоматическая миграция базы данных c0r.ai → AIDI.APP
"""
import os
import sys
import asyncio
from datetime import datetime
from supabase import create_client, Client
from loguru import logger

class AIDIMigration:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        
    async def run_migration(self):
        """Запуск полной миграции"""
        try:
            logger.info("🚀 Начинаем миграцию c0r.ai → AIDI.APP")
            
            # Этап 1: Создание резервной копии
            await self.create_backup()
            
            # Этап 2: Обновление пользовательских таблиц
            await self.update_user_tables()
            
            # Этап 3: Создание новых таблиц
            await self.create_new_tables()
            
            # Этап 4: Миграция данных
            await self.migrate_data()
            
            # Этап 5: Очистка старых таблиц
            await self.cleanup_old_tables()
            
            # Этап 6: Создание представлений
            await self.create_views()
            
            # Этап 7: Обновление индексов
            await self.update_indexes()
            
            logger.success("✅ Миграция успешно завершена!")
            
        except Exception as e:
            logger.error(f"❌ Ошибка миграции: {e}")
            await self.rollback()
            raise
    
    async def create_backup(self):
        """Создание резервной копии"""
        logger.info("📦 Создание резервной копии...")
        # Логика создания бэкапа
        
    async def update_user_tables(self):
        """Обновление пользовательских таблиц"""
        logger.info("👥 Обновление пользовательских таблиц...")
        # Выполнение SQL миграций для users и user_profiles
        
    async def create_new_tables(self):
        """Создание новых таблиц AIDI.APP"""
        logger.info("🆕 Создание новых таблиц...")
        # Создание reputation_analyses, deepfake_detections и т.д.
        
    async def migrate_data(self):
        """Миграция существующих данных"""
        logger.info("🔄 Миграция данных...")
        # Перенос кредитов, платежей и других данных
        
    async def cleanup_old_tables(self):
        """Очистка старых таблиц"""
        logger.info("🧹 Очистка старых таблиц...")
        # Архивирование и удаление таблиц питания
        
    async def create_views(self):
        """Создание представлений"""
        logger.info("👁️ Создание представлений...")
        # Создание