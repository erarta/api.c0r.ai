# MODERA.FASHION - Architecture Design

**Date:** 2025-01-27  
**Purpose:** Define the complete architecture for MODERA.FASHION service  
**Domain:** https://modera.fashion  

## Service Architecture Overview

### **CRITICAL: Complete Service Separation**
The architecture maintains complete separation between bot and services (api/ml/pay), following the existing c0r.ai pattern.

```
┌─────────────────────────────────────────────────────────────────┐
│                        MODERA.FASHION                           │
│                     https://modera.fashion                      │
└─────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
         ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
         │   API Service   │ │   ML Service    │ │  Pay Service    │
         │   Port: 8000    │ │   Port: 8001    │ │   Port: 8002    │
         │                 │ │                 │ │                 │
         │ • Telegram Bot  │ │ • DALL-E 3      │ │ • YooKassa      │
         │ • FastAPI       │ │ • GPT-4 Vision  │ │ • Stripe        │
         │ • FSM States    │ │ • Gemini Pro    │ │ • Webhooks      │
         │ • User Auth     │ │ • Image Proc    │ │ • Validation    │
         │ • Keyboards     │ │ • Style Engine  │ │ • Credits       │
         └─────────────────┘ └─────────────────┘ └─────────────────┘
                  │                    │                    │
                  └────────────────────┼────────────────────┘
                                       │
                          ┌─────────────────┐
                          │   Supabase DB   │
                          │   (PostgreSQL)  │
                          │                 │
                          │ • Users         │
                          │ • Fashion Data  │
                          │ • Transactions  │
                          │ • Style Profiles│
                          └─────────────────┘
                                       │
                          ┌─────────────────┐
                          │  Cloudflare R2  │
                          │   (Storage)     │
                          │                 │
                          │ • User Photos   │
                          │ • Clothing Imgs │
                          │ • Generated Imgs│
                          │ • Style Assets  │
                          └─────────────────┘
```

## Service Specifications

### API Service (Port 8000)
**URL:** https://api.modera.fashion  
**Responsibilities:**
- Telegram bot interface
- User authentication and session management
- FSM state management (3 states)
- Request routing to ML and Payment services
- Response formatting and delivery

**Key Components:**
```
services/api/
├── bot/
│   ├── handlers/
│   │   ├── fashion.py          # Virtual try-on handlers
│   │   ├── styling.py          # AI stylist handlers
│   │   ├── main_menu.py        # Default state handlers
│   │   ├── payments.py         # Payment handlers
│   │   └── profile.py          # User profile handlers
│   ├── keyboards/
│   │   ├── fashion.py          # Try-on keyboards
│   │   ├── styling.py          # Stylist keyboards
│   │   ├── main.py             # Main menu keyboards
│   │   └── payments.py         # Payment keyboards
│   ├── states/
│   │   ├── fashion.py          # Try-on FSM states
│   │   ├── styling.py          # Stylist FSM states
│   │   └── main.py             # Default FSM states
│   └── middleware/
│       ├── auth.py             # User authentication
│       ├── i18n.py             # Language middleware
│       └── credits.py          # Credit validation
└── edge/
    └── main.py                 # Cloudflare Worker API
```

### ML Service (Port 8001)
**URL:** https://ml.modera.fashion  
**Responsibilities:**
- Virtual try-on image generation
- AI style analysis and recommendations
- Image processing and optimization
- Fashion AI model management

**Key Components:**
```
services/ml/
├── fashion/
│   ├── virtual_tryon.py        # DALL-E 3 virtual fitting
│   ├── style_analysis.py       # GPT-4 Vision styling
│   ├── image_processor.py      # Image preprocessing
│   └── quality_checker.py      # Output validation
├── gemini/
│   ├── client.py               # Gemini Pro Vision client
│   ├── image_analysis.py       # Image understanding
│   └── fit_assessment.py       # Fit quality analysis
├── openai/
│   ├── client.py               # OpenAI client
│   ├── dalle_integration.py    # DALL-E 3 integration
│   └── gpt4_vision.py          # GPT-4 Vision integration
└── utils/
    ├── image_utils.py          # Image manipulation
    ├── cache_manager.py        # Result caching
    └── cost_optimizer.py       # AI usage optimization
```

### Payment Service (Port 8002)
**URL:** https://pay.modera.fashion  
**Responsibilities:**
- Credit-based payment processing
- YooKassa integration (Russian market)
- Stripe integration (International market)
- Webhook handling and validation
- Credit management and tracking

**Key Components:**
```
services/pay/
├── yookassa/
│   ├── client.py               # YooKassa API client
│   ├── webhooks.py             # Payment webhooks
│   └── credit_packages.py      # RUB pricing packages
├── stripe/
│   ├── client.py               # Stripe API client
│   ├── webhooks.py             # Payment webhooks
│   └── credit_packages.py      # USD pricing packages
├── credits/
│   ├── manager.py              # Credit balance management
│   ├── validator.py            # Credit usage validation
│   └── tracker.py              # Usage analytics
└── utils/
    ├── currency.py             # Currency conversion
    ├── validation.py           # Payment validation
    └── security.py             # Webhook security
```

## FSM State Management Architecture

### 3-State Fashion Workflow

```python
from aiogram.fsm.state import State, StatesGroup

class FashionStates(StatesGroup):
    # === DEFAULT STATE ===
    default = State()                    # Main menu, help, profile
    
    # === VIRTUAL TRY-ON WORKFLOW ===
    tryon_waiting_clothing = State()     # Waiting for clothing image
    tryon_waiting_person = State()       # Waiting for person image
    tryon_processing = State()           # AI processing in progress
    tryon_result = State()               # Showing result, options
    
    # === AI STYLIST WORKFLOW ===
    stylist_waiting_photo = State()      # Waiting for person photo
    stylist_preferences = State()        # Collecting style preferences
    stylist_processing = State()         # AI analysis in progress
    stylist_results = State()            # Showing recommendations
    stylist_shopping = State()           # Shopping interface
```

### State Transition Rules

#### Default State Transitions
```
Default State:
├── "Virtual Try-On" → tryon_waiting_clothing
├── "AI Stylist" → stylist_waiting_photo
├── "Profile" → (stay in default)
├── "Help" → (stay in default)
└── "Settings" → (stay in default)
```

#### Virtual Try-On Flow
```
Try-On Flow:
tryon_waiting_clothing → [clothing image] → tryon_waiting_person
tryon_waiting_person → [person image] → tryon_processing
tryon_processing → [AI complete] → tryon_result
tryon_result → [user action] → default OR new try-on
```

#### AI Stylist Flow
```
Stylist Flow:
stylist_waiting_photo → [person photo] → stylist_preferences
stylist_preferences → [preferences] → stylist_processing
stylist_processing → [AI complete] → stylist_results
stylist_results → [shopping] → stylist_shopping
stylist_shopping → [purchase/back] → default
```

### State Persistence Strategy
- **Session Storage:** Redis for temporary state data
- **User Context:** PostgreSQL for persistent user preferences
- **Image Storage:** Cloudflare R2 with temporary URLs
- **State Timeout:** 30 minutes of inactivity returns to default

## Database Schema Design

### Core Tables

#### Users Table (Enhanced)
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
    style_profile JSONB,
    preferences JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Fashion Sessions Table (New)
```sql
CREATE TABLE fashion_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(id),
    session_type VARCHAR(20) NOT NULL, -- 'tryon' or 'styling'
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'expired'
    input_data JSONB,
    result_data JSONB,
    credits_used INTEGER DEFAULT 0,
    processing_time INTEGER, -- seconds
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

#### Virtual Try-Ons Table (New)
```sql
CREATE TABLE virtual_tryons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES fashion_sessions(id),
    user_id BIGINT REFERENCES users(id),
    clothing_image_url TEXT NOT NULL,
    person_image_url TEXT NOT NULL,
    result_image_url TEXT,
    fit_analysis JSONB,
    quality_score DECIMAL(3,2),
    user_rating INTEGER, -- 1-5 stars
    credits_used INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Style Analyses Table (New)
```sql
CREATE TABLE style_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES fashion_sessions(id),
    user_id BIGINT REFERENCES users(id),
    input_image_url TEXT NOT NULL,
    style_profile JSONB NOT NULL,
    recommendations JSONB NOT NULL,
    user_feedback JSONB,
    credits_used INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Product Recommendations Table (New)
```sql
CREATE TABLE product_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    style_analysis_id UUID REFERENCES style_analyses(id),
    product_id VARCHAR(255) NOT NULL,
    partner_name VARCHAR(100) NOT NULL, -- 'wildberries', 'lamoda', etc.
    product_url TEXT NOT NULL,
    product_data JSONB NOT NULL,
    recommendation_score DECIMAL(3,2),
    user_clicked BOOLEAN DEFAULT FALSE,
    user_purchased BOOLEAN DEFAULT FALSE,
    affiliate_commission DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Credit Transactions Table (Enhanced)
```sql
CREATE TABLE credit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT REFERENCES users(id),
    transaction_type VARCHAR(20) NOT NULL, -- 'purchase', 'usage', 'refund'
    credits_amount INTEGER NOT NULL,
    cost_amount DECIMAL(10,2),
    currency VARCHAR(3), -- 'RUB', 'USD'
    payment_provider VARCHAR(20), -- 'yookassa', 'stripe'
    payment_id VARCHAR(255),
    feature_used VARCHAR(50), -- 'tryon', 'styling', 'recommendations'
    session_id UUID,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API Contract Specifications

### API ↔ ML Service Contract
```python
# shared/contracts/api_ml_fashion.py

class FashionMLContract:
    # Virtual Try-On Endpoints
    VIRTUAL_TRYON = "/api/v1/fashion/virtual-tryon"
    TRYON_STATUS = "/api/v1/fashion/tryon-status/{session_id}"
    
    # AI Stylist Endpoints
    STYLE_ANALYSIS = "/api/v1/fashion/style-analysis"
    STYLE_RECOMMENDATIONS = "/api/v1/fashion/recommendations"
    
    # Image Processing
    IMAGE_PREPROCESS = "/api/v1/fashion/preprocess-image"
    IMAGE_VALIDATE = "/api/v1/fashion/validate-image"

class VirtualTryonRequest:
    clothing_image_url: str
    person_image_url: str
    user_id: int
    session_id: str
    quality_level: str = "standard"  # standard, high, premium

class StyleAnalysisRequest:
    person_image_url: str
    user_id: int
    session_id: str
    preferences: dict = None
    budget_range: tuple = None
```

### API ↔ Payment Service Contract
```python
# shared/contracts/api_pay_fashion.py

class FashionPayContract:
    # Credit Management
    CREDIT_BALANCE = "/api/v1/credits/balance/{user_id}"
    CREDIT_PURCHASE = "/api/v1/credits/purchase"
    CREDIT_USAGE = "/api/v1/credits/use"
    
    # Payment Processing
    CREATE_INVOICE = "/api/v1/invoice/create"
    WEBHOOK_YOOKASSA = "/webhook/yookassa"
    WEBHOOK_STRIPE = "/webhook/stripe"

class CreditPurchaseRequest:
    user_id: int
    package_type: str  # 'basic', 'premium'
    currency: str      # 'RUB', 'USD'
    payment_provider: str  # 'yookassa', 'stripe'

class CreditUsageRequest:
    user_id: int
    credits_amount: int
    feature_used: str  # 'tryon', 'styling', 'recommendations'
    session_id: str
```

## External Service Integration

### AI Model Integration

#### OpenAI Integration
```python
# services/ml/openai/fashion_client.py

class FashionOpenAIClient:
    def __init__(self):
        self.dalle_client = OpenAI()
        self.gpt4_client = OpenAI()
    
    async def generate_virtual_tryon(
        self, 
        clothing_image: bytes, 
        person_image: bytes
    ) -> str:
        """Generate virtual try-on using DALL-E 3"""
        
    async def analyze_style(
        self, 
        person_image: bytes, 
        preferences: dict = None
    ) -> dict:
        """Analyze personal style using GPT-4 Vision"""
```

#### Gemini Integration
```python
# services/ml/gemini/fashion_client.py

class FashionGeminiClient:
    def __init__(self):
        self.client = genai.GenerativeModel('gemini-pro-vision')
    
    async def assess_fit_quality(
        self, 
        tryon_image: bytes
    ) -> dict:
        """Assess virtual try-on quality"""
        
    async def analyze_body_type(
        self, 
        person_image: bytes
    ) -> dict:
        """Analyze body type and measurements"""
```

### E-commerce Partner Integration

#### Wildberries API Integration
```python
# services/ml/partners/wildberries.py

class WildberriesClient:
    async def search_products(
        self, 
        query: str, 
        filters: dict = None
    ) -> list:
        """Search products in Wildberries catalog"""
        
    async def get_product_details(
        self, 
        product_id: str
    ) -> dict:
        """Get detailed product information"""
```

## Security Architecture

### Authentication & Authorization
- **User Authentication:** Telegram-based authentication
- **Service Authentication:** Internal API tokens
- **Image Security:** Signed URLs with expiration
- **Payment Security:** Webhook signature validation

### Data Privacy
- **Image Storage:** Temporary storage with auto-deletion
- **User Data:** GDPR-compliant data handling
- **Analytics:** Anonymized usage tracking
- **Consent Management:** Explicit user consent for AI processing

### Rate Limiting
- **API Endpoints:** 100 requests/minute per user
- **AI Processing:** Credit-based limiting
- **Image Upload:** 10MB max file size
- **Session Timeout:** 30 minutes inactivity

## Performance Optimization

### Caching Strategy
- **Redis Cache:** User sessions and temporary data
- **CDN Cache:** Static assets and processed images
- **Database Cache:** Query result caching
- **AI Cache:** Similar request result caching

### Scalability Considerations
- **Horizontal Scaling:** Load balancer for multiple instances
- **Database Scaling:** Read replicas for analytics
- **Storage Scaling:** Cloudflare R2 auto-scaling
- **AI Scaling:** Queue-based processing for high load

## Monitoring & Analytics

### Technical Monitoring
- **Service Health:** Uptime and response time monitoring
- **AI Performance:** Processing time and success rates
- **Database Performance:** Query performance and connection pooling
- **Storage Monitoring:** Usage and access patterns

### Business Analytics
- **User Behavior:** Feature usage and conversion tracking
- **Revenue Tracking:** Credit purchases and affiliate commissions
- **AI Effectiveness:** User satisfaction and recommendation accuracy
- **Market Analysis:** Geographic and demographic insights

---

**Architecture Summary:** MODERA.FASHION maintains the proven service separation architecture from c0r.ai while introducing sophisticated fashion AI capabilities. The 3-state FSM provides clear user workflows, and the credit-based system enables flexible monetization across Russian and international markets.