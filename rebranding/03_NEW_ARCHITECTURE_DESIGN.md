# MODERA.FASHION - New Architecture Design

## Date: 2025-01-26
## Purpose: Design new architecture for MODERA.FASHION

## Target Architecture

### Service Structure
```
modera.fashion/
├── services/
│   ├── api/              # Telegram Bot + FastAPI (Port 8000)
│   │   ├── bot/          # Telegram bot handlers
│   │   ├── handlers/     # Command handlers
│   │   │   ├── virtual_fitting.py
│   │   │   ├── ai_stylist.py
│   │   │   ├── profile.py
│   │   │   └── payments.py
│   │   └── utils/        # Utilities
│   ├── ml/               # AI/ML processing (Port 8001)
│   │   ├── virtual_fitting/
│   │   │   ├── clothing_detection.py
│   │   │   ├── person_detection.py
│   │   │   └── image_synthesis.py
│   │   ├── ai_stylist/
│   │   │   ├── style_analysis.py
│   │   │   ├── recommendation_engine.py
│   │   │   └── ecommerce_integration.py
│   │   └── models/
│   │       ├── gemini_client.py
│   │       └── openai_client.py
│   └── pay/              # Payment processing (Port 8002)
│       ├── yookassa/
│       ├── stripe/
│       └── affiliate_tracking.py
├── shared/               # Common utilities
├── common/               # Database models & configs
├── i18n/                # Internationalization
└── migrations/          # Database schema
```

### Service Separation Architecture
**CRITICAL:** Bot is completely separated from services (api/ml/pay)

- **API Service (Port 8000):** Telegram bot + FastAPI endpoints
- **ML Service (Port 8001):** AI/ML processing (virtual fitting, style analysis)
- **Pay Service (Port 8002):** Payment processing (Yookassa, Stripe)

**Communication:** Services communicate via HTTP API calls, not direct imports

## New Database Schema

### Core Tables
```sql
-- Users table (adapted)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    credits_remaining INTEGER DEFAULT 0,
    total_paid INTEGER DEFAULT 0,
    subscription_type TEXT DEFAULT 'free',
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    language TEXT DEFAULT 'en',
    country TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fashion profiles (replaces nutrition profiles)
CREATE TABLE fashion_profiles (
    id SERIAL PRIMARY KEY,
    body_type TEXT CHECK (body_type IN ('hourglass', 'rectangle', 'triangle', 'inverted_triangle', 'oval')),
    height REAL,
    weight REAL,
    preferred_style TEXT[],
    color_preferences TEXT[],
    budget_range TEXT CHECK (budget_range IN ('budget', 'mid_range', 'premium', 'luxury')),
    occasion_preferences TEXT[],
    size_preferences JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Virtual fitting sessions
CREATE TABLE virtual_fittings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    clothing_image_url TEXT NOT NULL,
    revenue_image_url TEXT NOT NULL,
    result_image_url TEXT,
    status TEXT DEFAULT 'processing',
    model_used TEXT,
    processing_time REAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Style recommendations
CREATE TABLE style_recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    recommendation_type TEXT CHECK (recommendation_type IN ('outfit', 'item', 'accessory')),
    items JSONB, -- Array of recommended items with links
    style_description TEXT,
    occasion TEXT,
    total_price REAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- E-commerce items
CREATE TABLE ecommerce_items (
    id SERIAL PRIMARY KEY,
    item_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
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
CREATE TABLE user_style_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    preference_type TEXT NOT NULL,
    preference_value TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## New API Endpoints

### Virtual Fitting Endpoints
```
POST /virtual-fitting/create
POST /virtual-fitting/status/{session_id}
GET /virtual-fitting/history/{user_id}
```

### AI Stylist Endpoints
```
POST /stylist/analyze-style
POST /stylist/get-recommendations
GET /stylist/recommendation-history/{user_id}
```

### E-commerce Endpoints
```
GET /ecommerce/search
GET /ecommerce/item/{item_id}
POST /ecommerce/track-click
```

## AI Model Integration

### Virtual Fitting Pipeline
1. **Clothing Detection:** Identify clothing items in image
2. **Person Segmentation:** Extract person from background
3. **Size Matching:** Analyze clothing fit to person
4. **Image Synthesis:** Generate realistic fitting result

### AI Stylist Pipeline
1. **Style Analysis:** Analyze user's current style
2. **Preference Learning:** Understand user preferences
3. **Recommendation Engine:** Match items to user profile
4. **E-commerce Integration:** Find available items

## Payment Plans

### Free Tier
- 3 virtual fittings per month
- Basic style recommendations
- Limited e-commerce links

### Premium Tier ($9.99/month)
- Unlimited virtual fittings
- Advanced AI styling
- Priority processing
- Detailed style analysis

### Pro Tier ($19.99/month)
- Everything in Premium
- API access
- Bulk processing
- Custom integrations

## Technology Requirements

### AI Models Needed
- **Gemini Pro Vision:** Image analysis and understanding
- **OpenAI DALL-E 3:** Image generation for virtual fitting
- **OpenAI GPT-4 Vision:** Style analysis and recommendations

### External Integrations
- **E-commerce APIs:** Wildberries, Lamoda, etc.
- **Affiliate Networks:** Commission tracking
- **Image Processing:** Advanced image manipulation

### Performance Requirements
- Virtual fitting: < 30 seconds processing time
- Style recommendations: < 5 seconds response time
- Image storage: Efficient compression and CDN delivery
