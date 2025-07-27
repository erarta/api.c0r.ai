# Current Architecture Analysis - c0r.ai

## Date: 2025-01-26
## Purpose: Analyze existing architecture for MODERA.FASHION adaptation

## Current System Overview

### Service Architecture (Already Properly Separated)
```
c0r.ai
├── services/
│   ├── api/          # Telegram Bot + FastAPI (Port 8000)
│   ├── ml/           # AI/ML processing (Port 8001)
│   └── pay/          # Payment processing (Port 8002)
├── shared/           # Common utilities
├── common/           # Database models & configs
├── i18n/            # Internationalization
└── migrations/      # Database schema
```

### Service Separation Architecture ✅
**VERIFIED:** The current c0r.ai architecture already has proper service separation:

- **API Service (Port 8000):** Telegram bot + FastAPI endpoints
- **ML Service (Port 8001):** AI/ML processing (nutrition analysis, recipe generation)
- **Pay Service (Port 8002):** Payment processing (Yookassa, Stripe)

**Communication Pattern:** Services communicate via HTTP API calls, not direct imports

### Current Features (c0r.ai)
1. **Nutrition Analysis:** Photo-based food analysis
2. **Recipe Generation:** AI-powered recipe suggestions
3. **User Profiles:** Personal nutrition data
4. **Payment System:** Yookassa integration
5. **Multi-language:** EN/RU support
6. **Credit System:** Pay-per-use model

### Database Schema (Current)
- `users` - User accounts and credits
- `user_profiles` - Nutrition preferences
- `logs` - User activity tracking
- `payments` - Payment history

### Technology Stack (Current)
- **AI:** OpenAI GPT-4, Gemini
- **Backend:** FastAPI, Python 3.10+
- **Database:** PostgreSQL (Supabase)
- **Payments:** Yookassa
- **Storage:** Cloudflare R2
- **Deployment:** Docker Compose

## Reusable Components

### ✅ Keep As-Is
1. **Service Architecture:** 3-service microservices pattern
2. **Payment System:** Yookassa integration
3. **Multi-language Support:** i18n framework
4. **Docker Setup:** Containerization strategy
5. **Health Checks:** Service monitoring
6. **Authentication:** Internal service auth
7. **Logging:** Structured logging system
8. **Testing Framework:** pytest setup

### 🔄 Adapt/Modify
1. **Database Schema:** New tables for fashion data
2. **AI Models:** Switch from nutrition to fashion AI
3. **User Profiles:** Fashion preferences instead of nutrition
4. **API Endpoints:** New fashion-specific endpoints
5. **Telegram Bot:** New commands and flows
6. **Business Logic:** Fashion-specific processing

### ❌ Remove/Replace
1. **Nutrition Calculations:** Not needed for fashion
2. **Recipe Generation:** Replace with style recommendations
3. **Food Analysis:** Replace with clothing analysis
4. **Calorie Tracking:** Replace with style tracking

## Migration Strategy

### Phase 1: Core Infrastructure
- Keep service architecture
- Adapt database schema
- Update environment variables

### Phase 2: AI Integration
- Replace nutrition AI with fashion AI
- Implement virtual fitting algorithms
- Add style recommendation engine

### Phase 3: User Experience
- Redesign Telegram bot flows
- Update user profiles for fashion
- Implement new payment plans

### Phase 4: E-commerce Integration
- Add shopping links
- Implement affiliate tracking
- Create retailer partnerships

## Estimated Effort
- **Database Migration:** 2-3 days
- **AI Model Integration:** 1-2 weeks
- **Bot Redesign:** 1 week
- **Testing & QA:** 1 week
- **Total:** 3-4 weeks 