# Схема базы данных AIDI.APP

*Дата создания: 27 января 2025*
*Цель: Полная SQL схема для создания базы данных AIDI.APP*

## 📋 Обзор схемы

База данных AIDI.APP построена на PostgreSQL и включает следующие основные компоненты:

- **Пользовательские таблицы** - управление пользователями и профилями
- **Анализ репутации** - хранение результатов репутационного анализа
- **Детекция дипфейков** - результаты проверки медиафайлов
- **KYC верификация** - процессы знай-своего-клиента
- **Система кредитов** - внутренняя валюта и платежи
- **Аналитические представления** - для отчетности и мониторинга

## 🗄️ Полная SQL схема

### 1. Пользовательские таблицы

#### Таблица users
```sql
-- =====================================================
-- AIDI.APP Database Schema
-- Создание: 27 января 2025
-- Описание: Полная схема базы данных для сервиса репутации и KYC
-- =====================================================

-- Включаем расширения PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- =====================================================
-- 1. ПОЛЬЗОВАТЕЛЬСКИЕ ТАБЛИЦЫ
-- =====================================================

-- Основная таблица пользователей
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10) DEFAULT 'ru',
    timezone VARCHAR(50) DEFAULT 'Europe/Moscow',
    
    -- Статус и репутация
    is_premium BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    reputation_score INTEGER CHECK (reputation_score >= 0 AND reputation_score <= 100),
    verification_status VARCHAR(50) DEFAULT 'unverified' 
        CHECK (verification_status IN ('unverified', 'pending', 'verified', 'rejected')),
    
    -- Активность
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    registration_source VARCHAR(100) DEFAULT 'telegram',
    referral_code VARCHAR(20) UNIQUE,
    referred_by_user_id UUID REFERENCES users(id),
    
    -- Временные метки
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы для таблицы users
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_username ON users(username) WHERE username IS NOT NULL;
CREATE INDEX idx_users_last_activity ON users(last_activity_at DESC);
CREATE INDEX idx_users_verification_status ON users(verification_status);
CREATE INDEX idx_users_referral_code ON users(referral_code) WHERE referral_code IS NOT NULL;
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- Комментарии для таблицы users
COMMENT ON TABLE users IS 'Основная таблица пользователей системы';
COMMENT ON COLUMN users.telegram_id IS 'Уникальный ID пользователя в Telegram';
COMMENT ON COLUMN users.reputation_score IS 'Собственный рейтинг репутации пользователя (0-100)';
COMMENT ON COLUMN users.verification_status IS 'Статус KYC верификации пользователя';
COMMENT ON COLUMN users.referral_code IS 'Реферальный код пользователя для привлечения новых клиентов';
```

#### Таблица user_profiles
```sql
-- Профили пользователей с настройками
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Настройки анализа
    analysis_preferences JSONB DEFAULT '{
        "reputation_depth": "basic",
        "deepfake_sensitivity": "medium",
        "auto_save_reports": true,
        "notification_frequency": "immediate"
    }',
    
    -- Настройки приватности
    privacy_settings JSONB DEFAULT '{
        "data_sharing": false,
        "anonymous_analytics": true,
        "report_sharing": false,
        "profile_visibility": "private"
    }',
    
    -- Настройки уведомлений
    notification_settings JSONB DEFAULT '{
        "reputation_alerts": true,
        "deepfake_alerts": true,
        "payment_notifications": true,
        "marketing_emails": false,
        "security_alerts": true
    }',
    
    -- Подписка и доступ
    subscription_type VARCHAR(50) DEFAULT 'free' 
        CHECK (subscription_type IN ('free', 'basic', 'professional', 'enterprise')),
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    data_retention_days INTEGER DEFAULT 30 
        CHECK (data_retention_days >= 1 AND data_retention_days <= 365),
    
    -- API доступ
    api_access_enabled BOOLEAN DEFAULT FALSE,
    api_key VARCHAR(255) UNIQUE,
    api_rate_limit INTEGER DEFAULT 100, -- запросов в час
    api_calls_made_today INTEGER DEFAULT 0,
    api_calls_reset_at TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_DATE + INTERVAL '1 day'),
    
    -- Статистика использования
    usage_statistics JSONB DEFAULT '{
        "analyses_count": 0,
        "deepfake_checks": 0,
        "kyc_verifications": 0,
        "api_calls_total": 0,
        "credits_purchased": 0,
        "credits_used": 0
    }',
    
    -- Временные метки
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы для таблицы user_profiles
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_subscription ON user_profiles(subscription_type, subscription_expires_at);
CREATE INDEX idx_user_profiles_api_key ON user_profiles(api_key) WHERE api_key IS NOT NULL;
CREATE INDEX idx_user_profiles_api_reset ON user_profiles(api_calls_reset_at) WHERE api_access_enabled = TRUE;

-- Комментарии для таблицы user_profiles
COMMENT ON TABLE user_profiles IS 'Расширенные профили пользователей с настройками и статистикой';
COMMENT ON COLUMN user_profiles.analysis_preferences IS 'Пользовательские настройки для анализа репутации и дипфейков';
COMMENT ON COLUMN user_profiles.data_retention_days IS 'Количество дней хранения данных анализов (GDPR compliance)';
COMMENT ON COLUMN user_profiles.api_key IS 'API ключ для программного доступа к сервису';
COMMENT ON COLUMN user_profiles.usage_statistics IS 'Статистика использования сервиса пользователем';
```

### 2. Анализ репутации

#### Таблица reputation_analyses
```sql
-- =====================================================
-- 2. АНАЛИЗ РЕПУТАЦИИ
-- =====================================================

-- Основная таблица анализов репутации
CREATE TABLE reputation_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Данные цели анализа
    target_name VARCHAR(255),
    target_phone VARCHAR(50),
    target_email VARCHAR(255),
    target_photo_url TEXT,
    target_social_profiles JSONB DEFAULT '{}', -- {"vk": "id123", "telegram": "@username"}
    target_additional_info JSONB DEFAULT '{}', -- дополнительная информация
    
    -- Параметры анализа
    analysis_type VARCHAR(50) NOT NULL 
        CHECK (analysis_type IN ('basic', 'extended', 'deep', 'forensic')),
    search_depth VARCHAR(50) DEFAULT 'standard' 
        CHECK (search_depth IN ('surface', 'standard', 'deep', 'comprehensive')),
    data_sources JSONB DEFAULT '["social_media", "public_records"]', -- источники для поиска
    geographic_scope VARCHAR(100) DEFAULT 'russia', -- географический охват поиска
    time_range_months INTEGER DEFAULT 12, -- временной диапазон поиска в месяцах
    
    -- Статус и прогресс
    status VARCHAR(50) DEFAULT 'pending' 
        CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled', 'expired')),
    progress_percentage INTEGER DEFAULT 0 
        CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    current_stage VARCHAR(100), -- текущий этап обработки
    
    -- Результаты скоринга (0-100)
    risk_score INTEGER CHECK (risk_score >= 0 AND risk_score <= 100),
    credibility_score INTEGER CHECK (credibility_score >= 0 AND credibility_score <= 100),
    activity_score INTEGER CHECK (activity_score >= 0 AND activity_score <= 100),
    professional_score INTEGER CHECK (professional_score >= 0 AND professional_score <= 100),
    
    -- Дополнительные метрики
    sentiment_score DECIMAL(3,2) CHECK (sentiment_score >= -1.00 AND sentiment_score <= 1.00),
    influence_score INTEGER CHECK (influence_score >= 0 AND influence_score <= 100),
    controversy_score INTEGER CHECK (controversy_score >= 0 AND controversy_score <= 100),
    
    -- Результаты анализа
    results JSONB DEFAULT '{}', -- детальные результаты
    executive_summary TEXT, -- краткое резюме
    detailed_report TEXT, -- подробный отчет
    recommendations TEXT, -- рекомендации
    
    -- Найденные данные
    sources_found INTEGER DEFAULT 0,
    profiles_found INTEGER DEFAULT 0,
    mentions_found INTEGER DEFAULT 0,
    documents_found INTEGER DEFAULT 0,
    
    -- Индикаторы
    red_flags JSONB DEFAULT '[]', -- негативные индикаторы
    positive_indicators JSONB DEFAULT '[]', -- позитивные индикаторы
    neutral_facts JSONB DEFAULT '[]', -- нейтральные факты
    
    -- Техническая информация
    credits_used INTEGER DEFAULT 1,
    processing_time_ms INTEGER,
    ai_model_version VARCHAR(50),
    data_quality_score DECIMAL(3,2) CHECK (data_quality_score >= 0.00 AND data_quality_score <= 1.00),
    confidence_level DECIMAL(3,2) CHECK (confidence_level >= 0.00 AND confidence_level <= 1.00),
    
    -- Ошибки и предупреждения
    error_message TEXT,
    warnings JSONB DEFAULT '[]',
    
    -- Временные метки
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days')
);

-- Индексы для таблицы reputation_analyses
CREATE INDEX idx_reputation_analyses_user_id ON reputation_analyses(user_id);
CREATE INDEX idx_reputation_analyses_status ON reputation_analyses(status);
CREATE INDEX idx_reputation_analyses_created_at ON reputation_analyses(created_at DESC);
CREATE INDEX idx_reputation_analyses_target_phone ON reputation_analyses(target_phone) WHERE target_phone IS NOT NULL;
CREATE INDEX idx_reputation_analyses_target_email ON reputation_analyses(target_email) WHERE target_email IS NOT NULL;
CREATE INDEX idx_reputation_analyses_expires_at ON reputation_analyses(expires_at);
CREATE INDEX idx_reputation_analyses_risk_score ON reputation_analyses(risk_score DESC) WHERE risk_score IS NOT NULL;
CREATE INDEX idx_reputation_analyses_analysis_type ON reputation_analyses(analysis_type);

-- Полнотекстовый поиск
CREATE INDEX idx_reputation_analyses_target_name_gin ON reputation_analyses USING gin(to_tsvector('russian', target_name)) WHERE target_name IS NOT NULL;

-- Комментарии для таблицы reputation_analyses
COMMENT ON TABLE reputation_analyses IS 'Анализы репутации пользователей и результаты';
COMMENT ON COLUMN reputation_analyses.risk_score IS 'Общий риск-скор (0-100, выше = более рискованно)';
COMMENT ON COLUMN reputation_analyses.credibility_score IS 'Скор достоверности (0-100, выше = более достоверно)';
COMMENT ON COLUMN reputation_analyses.sentiment_score IS 'Общая тональность упоминаний (-1.0 до 1.0)';
COMMENT ON COLUMN reputation_analyses.expires_at IS 'Дата автоматического удаления данных анализа';
```

#### Таблица reputation_sources
```sql
-- Источники данных для анализа репутации
CREATE TABLE reputation_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES reputation_analyses(id) ON DELETE CASCADE,
    
    -- Информация об источнике
    source_type VARCHAR(100) NOT NULL, -- 'vk', 'telegram', 'instagram', 'court_records', etc.
    source_name VARCHAR(255), -- "VKontakte", "Судебные решения", "РИА Новости"
    source_url TEXT,
    source_category VARCHAR(50) 
        CHECK (source_category IN ('social_media', 'public_records', 'news', 'professional', 'legal', 'financial')),
    
    -- Найденные данные
    data_found JSONB DEFAULT '{}',
    content_type VARCHAR(50) 
        CHECK (content_type IN ('profile', 'post', 'comment', 'article', 'record', 'document', 'image', 'video')),
    content_summary TEXT,
    content_full_text TEXT,
    content_date TIMESTAMP WITH TIME ZONE,
    content_language VARCHAR(10) DEFAULT 'ru',
    
    -- Анализ данных
    relevance_score DECIMAL(3,2) CHECK (relevance_score >= 0.00 AND relevance_score <= 1.00),
    credibility_score DECIMAL(3,2) CHECK (credibility_score >= 0.00 AND credibility_score <= 1.00),
    sentiment DECIMAL(3,2) CHECK (sentiment >= -1.00 AND sentiment <= 1.00),
    impact_score DECIMAL(3,2) CHECK (impact_score >= 0.00 AND impact_score <= 1.00),
    
    -- Классификация контента
    risk_indicators JSONB DEFAULT '[]',
    positive_indicators JSONB DEFAULT '[]',
    tags JSONB DEFAULT '[]',
    categories JSONB DEFAULT '[]',
    
    -- Техническая информация
    extraction_method VARCHAR(50) 
        CHECK (extraction_method IN ('api', 'scraping', 'manual', 'partner_feed')),
    data_quality VARCHAR(50) DEFAULT 'good' 
        CHECK (data_quality IN ('poor', 'fair', 'good', 'excellent')),
    verification_status VARCHAR(50) DEFAULT 'unverified' 
        CHECK (verification_status IN ('unverified', 'verified', 'disputed', 'fake')),
    
    -- Метаданные
    metadata JSONB DEFAULT '{}',
    processing_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы для таблицы reputation_sources
CREATE INDEX idx_reputation_sources_analysis_id ON reputation_sources(analysis_id);
CREATE INDEX idx_reputation_sources_source_type ON reputation_sources(source_type);
CREATE INDEX idx_reputation_sources_source_category ON reputation_sources(source_category);
CREATE INDEX idx_reputation_sources_relevance ON reputation_sources(relevance_score DESC);
CREATE INDEX idx_reputation_sources_content_date ON reputation_sources(content_date DESC) WHERE content_date IS NOT NULL;
CREATE INDEX idx_reputation_sources_sentiment ON reputation_sources(sentiment);

-- Полнотекстовый поиск по контенту
CREATE INDEX idx_reputation_sources_content_gin ON reputation_sources USING gin(to_tsvector('russian', content_summary)) WHERE content_summary IS NOT NULL;

-- Комментарии для таблицы reputation_sources
COMMENT ON TABLE reputation_sources IS 'Отдельные источники данных, найденные при анализе репутации';
COMMENT ON COLUMN reputation_sources.relevance_score IS 'Насколько релевантен источник к целевому лицу (0.0-1.0)';
COMMENT ON COLUMN reputation_sources.impact_score IS 'Влияние источника на общую репутацию (0.0-1.0)';
```

### 3. Детекция дипфейков

#### Таблица deepfake_detections
```sql
-- =====================================================
-- 3. ДЕТЕКЦИЯ ДИПФЕЙКОВ
-- =====================================================

-- Основная таблица детекции дипфейков
CREATE TABLE deepfake_detections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Информация о медиафайле
    media_url TEXT NOT NULL,
    media_type VARCHAR(20) NOT NULL 
        CHECK (media_type IN ('image', 'video', 'audio')),
    file_size_bytes BIGINT,
    file_format VARCHAR(20), -- 'mp4', 'jpg', 'png', 'wav', etc.
    file_hash VARCHAR(64), -- SHA-256 хеш файла
    
    -- Характеристики медиа
    duration_seconds DECIMAL(10,3), -- для видео/аудио
    resolution VARCHAR(20), -- "1920x1080"
    frame_rate DECIMAL(6,3), -- для видео
    bitrate INTEGER, -- битрейт
    codec VARCHAR(50), -- кодек
    
    -- Параметры анализа
    analysis_type VARCHAR(50) NOT NULL 
        CHECK (analysis_type IN ('quick', 'standard', 'detailed', 'forensic')),
    detection_models JSONB DEFAULT '["face_detection", "temporal_analysis", "compression_artifacts"]',
    analysis_settings JSONB DEFAULT '{}',
    
    -- Статус обработки
    status VARCHAR(50) DEFAULT 'pending' 
        CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    progress_percentage INTEGER DEFAULT 0 
        CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    current_stage VARCHAR(100),
    
    -- Основные результаты детекции
    deepfake_probability DECIMAL(5,4) 
        CHECK (deepfake_probability >= 0.0000 AND deepfake_probability <= 1.0000),
    authenticity_score DECIMAL(5,4) 
        CHECK (authenticity_score >= 0.0000 AND authenticity_score <= 1.0000),
    confidence_score DECIMAL(5,4) 
        CHECK (confidence_score >= 0.0000 AND confidence_score <= 1.0000),
    
    -- Детальные результаты анализа
    face_analysis JSONB DEFAULT '{}', -- анализ лиц
    temporal_analysis JSONB DEFAULT '{}', -- временные несоответствия
    compression_analysis JSONB DEFAULT '{}', -- артефакты сжатия
    metadata_analysis JSONB DEFAULT '{}', -- анализ метаданных
    technical_analysis JSONB DEFAULT '{}', -- технический анализ
    
    -- Найденные артефакты
    artifacts_found JSONB DEFAULT '[]',
    inconsistencies JSONB DEFAULT '[]',
    anomalies JSONB DEFAULT '[]',
    
    -- Заключение
    verdict VARCHAR(50) 
        CHECK (verdict IN ('authentic', 'likely_authentic', 'suspicious', 'likely_deepfake', 'deepfake', 'inconclusive')),
    verdict_confidence DECIMAL(3,2) 
        CHECK (verdict_confidence >= 0.00 AND verdict_confidence <= 1.00),
    explanation TEXT,
    technical_details TEXT,
    recommendations TEXT,
    
    -- Дополнительная информация
    detection_details JSONB DEFAULT '{}',
    quality_assessment JSONB DEFAULT '{}',
    risk_assessment JSONB DEFAULT '{}',
    
    -- Техническая информация
    credits_used INTEGER DEFAULT 1,
    processing_time_ms INTEGER,
    ai_model_version VARCHAR(50),
    detection_engine VARCHAR(50) DEFAULT 'aidi_v1',
    
    -- Ошибки
    error_message TEXT,
    warnings JSONB DEFAULT '[]',
    
    -- Временные метки
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days')
);

-- Индексы для таблицы deepfake_detections
CREATE INDEX idx_deepfake_detections_user_id ON deepfake_detections(user_id);
CREATE INDEX idx_deepfake_detections_status ON deepfake_detections(status);
CREATE INDEX idx_deepfake_detections_created_at ON deepfake_detections(created_at DESC);
CREATE INDEX idx_deepfake_detections_media_type ON deepfake_detections(media_type);
CREATE INDEX idx_deepfake_detections_verdict ON deepfake_detections(verdict);
CREATE INDEX idx_deepfake_detections_expires_at ON deepfake_detections(expires_at);
CREATE INDEX idx_deepfake_detections_file_hash ON deepfake_detections(file_hash) WHERE file_hash IS NOT NULL;
CREATE INDEX idx_deepfake_detections_deepfake_prob ON deepfake_detections(deepfake_probability DESC) WHERE deepfake_probability IS NOT NULL;

-- Комментарии для таблицы deepfake_detections
COMMENT ON TABLE deepfake_detections IS 'Анализы медиафайлов на предмет дипфейков';
COMMENT ON COLUMN deepfake_detections.deepfake_probability IS 'Вероятность того, что медиа является дипфейком (0.0-1.0)';
COMMENT ON COLUMN deepfake_detections.authenticity_score IS 'Вероятность подлинности медиа (0.0-1.0)';
COMMENT ON COLUMN deepfake_detections.confidence_score IS 'Уверенность в результате детекции (0.0-1.0)';
```

### 4. KYC верификация

#### Таблица kyc_verifications
```sql
-- =====================================================
-- 4. KYC ВЕРИФИКАЦИЯ
-- =====================================================

-- Таблица KYC верификаций
CREATE TABLE kyc_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Тип верификации
    verification_type VARCHAR(50) NOT NULL 
        CHECK (verification_type IN ('document', 'selfie', 'video', 'biometric', 'full_kyc')),
    document_type VARCHAR(50) 
        CHECK (document_type IN ('passport', 'driver_license', 'id_card', 'foreign_passport')),
    
    -- Загруженные файлы
    document_front_url TEXT,
    document_back_url TEXT,
    selfie_url TEXT,
    video_url TEXT,
    additional_documents JSONB DEFAULT '[]',
    
    -- Статус верификации
    status VARCHAR(50) DEFAULT 'pending' 
        CHECK (status IN ('pending', 'processing', 'approved', 'rejected', 'expired', 'requires_review')),
    verification_level VARCHAR(50) DEFAULT 'basic' 
        CHECK (verification_level IN ('basic', 'enhanced', 'premium', 'institutional')),
    
    -- Результаты автоматической проверки
    document_authenticity_score DECIMAL(3,2) 
        CHECK (document_authenticity_score >= 0.00 AND document_authenticity_score <= 1.00),
    face_match_score DECIMAL(3,2) 
        CHECK (face_match_score >= 0.00 AND face_match_score <= 1.00),
    liveness_score DECIMAL(3,2) 
        CHECK (liveness_score >= 0.00 AND liveness_score <= 1.00),
    overall_confidence DECIMAL(3,2) 
        CHECK (overall_confidence >= 0.00 AND overall_confidence <= 1.00),
    
    -- Извлеченные данные из документов
    extracted_data JSONB DEFAULT '{}', -- имя, дата рождения, номер документа и т.д.
    document_data JSONB DEFAULT '{}', -- структурированные данные документа
    biometric_data JSONB DEFAULT '{}', -- биометрические данные (хешированные)
    
    -- Результаты проверок
    verification_details JSONB DEFAULT '{}',
    security_checks JSONB DEFAULT '{}',
    fraud_indicators JSONB DEFAULT '[]',
    
    -- Причины отклонения и заметки
    rejection_reasons JSONB DEFAULT '[]',
    manual_review_notes TEXT,
    reviewer_id UUID REFERENCES users(id),
    compliance_notes TEXT,
    
    -- Техническая информация
    credits_used INTEGER DEFAULT 2,
    processing_time_ms INTEGER,
    ai_model_version VARCHAR(50),
    verification_provider VARCHAR(50) DEFAULT 'aidi_internal',
    
    -- Временные метки
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    submitted_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '1 year')
);

-- Индексы для таблицы kyc_verifications
CREATE INDEX idx_kyc_verifications_user_id ON kyc_verifications(user_id);
CREATE INDEX idx_kyc_verifications_status ON kyc_verifications(status);
CREATE INDEX idx_kyc_verifications_verification_type ON kyc_verifications(verification_type);
CREATE INDEX idx_kyc_verifications_verification_level ON kyc_verifications(verification_level);
CREATE INDEX idx_kyc_verifications_expires_at ON kyc_verifications(expires_at);
CREATE INDEX idx_kyc_verifications_created_at ON kyc_verifications(created_at DESC);

-- Комментарии для таблицы kyc_verifications
COMMENT ON TABLE kyc_verifications IS 'KYC (Know Your Customer) верификации пользователей';
COMMENT ON COLUMN kyc_verifications.document_authenticity_score IS 'Оценка подлинности документа (0.0-1.0)';
COMMENT ON COLUMN kyc_verifications.face_match_score IS 'Соответствие селфи фото в документе (0.0-1.0)';
COMMENT ON COLUMN kyc_verifications.liveness_score IS 'Оценка живости для селфи/видео (0.0-1.0)';
```

### 5. Система кредитов и платежей

#### Таблица credits
```sql
-- =====================================================
-- 5. СИСТЕМА КРЕДИТОВ И ПЛАТЕЖЕЙ
-- =====================================================

-- Система кредитов (внутренняя валюта)
CREATE TABLE credits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Информация о транзакции
    amount INTEGER NOT NULL, -- может быть отрицательным для списаний
    transaction_type VARCHAR(50) NOT NULL 
        CHECK (transaction_type IN (
            'purchase', 'usage', 'refund', 'bonus', 'promotion',
            'reputation_analysis', 'deepfake_detection', 'kyc_verification',
            'api_usage', 'premium_feature', 'referral_bonus', 'cashback'
        )),
    
    -- Детали использования
    service_type VARCHAR(50) 
        CHECK (service_type IN ('reputation', 'deepfake', 'kyc', 'api', 'premium', 'other')),
    analysis_complexity VARCHAR(50) 
        CHECK (analysis_complexity IN ('basic', 'extended', 'deep', 'forensic')),
    
    -- Связанные объекты
    related_analysis_id UUID, -- может ссылаться на reputation_analyses или deepfake_detections
    related_payment_id UUID, -- ссылка на платеж
    related_verification_id UUID REFERENCES kyc_verifications(id),
    
    -- Описание и метаданные
    description TEXT,
    metadata JSONB DEFAULT '{}',
    
    -- Баланс после транзакции
    balance_after INTEGER NOT NULL,
    
    -- Временные метки
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE -- для бонусных кредитов
);

-- Индексы для таблицы credits
CREATE INDEX idx_credits_user_id ON credits(user_id);
CREATE INDEX idx_credits_transaction_type ON credits(transaction_type);
CREATE INDEX idx_credits_service_type ON credits(service_type);
CREATE INDEX idx_credits_created_at ON credits(created_at DESC);
CREATE INDEX idx_credits_expires_at ON credits(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX idx_credits_related_analysis ON credits(related_analysis_id) WHERE related_analysis_id IS NOT NULL;

-- Комментарии для таблицы credits
COMMENT ON TABLE credits IS 'Система кредитов - внутренняя валюта для оплаты услуг';
COMMENT ON COLUMN credits.amount IS 'Количество кредитов (положительное - пополнение, отрицательное - списание)';
COMMENT ON COLUMN credits.service_type IS 'Тип сервиса: reputation, deepfake, kyc, api, premium';
COMMENT ON COLUMN credits.analysis_complexity IS 'Сложность анализа, влияющая на стоимость в кредитах';
COMMENT ON COLUMN credits.balance_after IS 'Баланс пользователя после данной транзакции';
```

#### Таблица payments
```sql
-- Платежи (покупка кредитов)
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Информация о платеже
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT