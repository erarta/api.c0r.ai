# MODERA.FASHION - Complete Rebranding Plan (Claude Version)

## Overview
This folder contains the complete rebranding plan for transforming c0r.ai into MODERA.FASHION - a comprehensive virtual fitting room and AI stylist service.

**Date:** 2025-01-27  
**Status:** Planning Phase  
**Estimated Timeline:** 6-8 weeks  

## Service Description
MODERA.FASHION is an AI-powered fashion technology platform that combines:
- **Virtual Try-On:** Upload clothing photo + person photo → get realistic virtual fitting
- **AI Stylist:** Upload person photo → get style analysis + shopping recommendations
- **Smart Shopping:** Direct purchase links to recommended items from partner stores

## Key Features

### 🔄 State Management System
The bot supports 3 distinct states with FSM (Finite State Machine):
1. **Default State:** Main menu, general commands, help
2. **Virtual Try-On State:** Clothing fitting workflow
3. **AI Stylist State:** Style analysis and recommendations workflow

### 🌍 Internationalization
- **English (en):** Primary language
- **Russian (ru):** Full translation support
- All new features must include both language versions

### 🏗️ Service Architecture (Properly Separated)
- **API Service (Port 8000):** Telegram bot + FastAPI endpoints
- **ML Service (Port 8001):** AI/ML processing (virtual fitting, style analysis)  
- **Pay Service (Port 8002):** Payment processing (YooKassa, Stripe)
- **Communication:** Services interact via HTTP API calls only

## Documentation Structure

### 📋 Core Planning Documents
- [`01_CURRENT_STRUCTURE_ANALYSIS.md`](01_CURRENT_STRUCTURE_ANALYSIS.md) - Complete current project structure
- [`02_PROJECT_OVERVIEW.md`](02_PROJECT_OVERVIEW.md) - MODERA.FASHION specifications
- [`03_ARCHITECTURE_DESIGN.md`](03_ARCHITECTURE_DESIGN.md) - New service architecture
- [`04_DATABASE_MIGRATION.sql`](04_DATABASE_MIGRATION.sql) - Complete database schema for MODERA.FASHION
- [`05_TELEGRAM_BOT_FSM.md`](05_TELEGRAM_BOT_FSM.md) - 3-state bot design with FSM
- [`06_AI_INTEGRATION.md`](06_AI_INTEGRATION.md) - Virtual fitting + AI stylist implementation
- [`07_BUSINESS_STRATEGY.md`](07_BUSINESS_STRATEGY.md) - Russian + International pricing plans
- [`08_INFRASTRUCTURE_SETUP.md`](08_INFRASTRUCTURE_SETUP.md) - Deployment and infrastructure
- [`09_IMPLEMENTATION_CHECKLIST.md`](09_IMPLEMENTATION_CHECKLIST.md) - Complete implementation guide
- [`10_USER_SETUP_INSTRUCTIONS.md`](10_USER_SETUP_INSTRUCTIONS.md) - What user needs to create/setup

## Quick Implementation Overview

### Phase 1: Infrastructure Setup (Week 1-2)
1. Register `modera.fashion` domain
2. Set up new AWS EC2 instance
3. Create new Supabase project
4. Configure Cloudflare R2 storage
5. Create new Telegram bot (@ModeraFashionBot)
6. Run database migration script

### Phase 2: Core Development (Week 3-5)
1. Migrate and adapt existing codebase
2. Implement 3-state FSM for bot
3. Develop virtual try-on pipeline
4. Create AI stylist functionality
5. Update all i18n translations (EN/RU)
6. Integrate payment systems

### Phase 3: Testing & Launch (Week 6-8)
1. Write comprehensive tests for new functionality
2. Test FSM state transitions thoroughly
3. Security audit and optimization
4. Production deployment
5. Soft launch and monitoring

## Technology Stack

### AI Models
- **Gemini Pro Vision:** Image analysis and understanding
- **OpenAI DALL-E 3:** Virtual fitting image generation  
- **OpenAI GPT-4 Vision:** Style analysis and recommendations

### Backend Infrastructure
- **FastAPI:** High-performance API framework
- **PostgreSQL:** Primary database (Supabase)
- **Cloudflare R2:** File storage and CDN
- **Docker:** Containerization and deployment

### Domain & URLs
- **Main Domain:** https://modera.fashion
- **API Service:** https://api.modera.fashion
- **ML Service:** https://ml.modera.fashion
- **Payment Service:** https://pay.modera.fashion

## Critical Requirements

### ✅ Service Separation
Bot is completely separated from services (api/ml/pay) - already implemented in current architecture.

### ✅ State Management
3-state FSM implementation:
- Default → Virtual Try-On → Default
- Default → AI Stylist → Default
- Proper state persistence and cleanup

### ✅ Internationalization
All new text must be added to both:
- `i18n/en/` - English translations
- `i18n/ru/` - Russian translations

### ✅ Testing Requirements
After main code implementation:
- Unit tests for all new functions
- Integration tests for FSM states
- E2E tests for complete workflows
- Payment flow testing

## Next Steps

1. **Review Planning Documents:** Go through each document in order
2. **Infrastructure Setup:** Follow user setup instructions
3. **Development:** Use implementation checklist
4. **Testing:** Write comprehensive tests after code completion
5. **Deployment:** Follow infrastructure setup guide

---

**Note:** This plan builds upon the existing c0r.ai infrastructure while introducing significant new AI capabilities for the fashion industry. The service separation architecture is already in place and will be maintained.