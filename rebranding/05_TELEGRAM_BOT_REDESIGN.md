# Telegram Bot Redesign - MODERA.FASHION

## Date: 2025-01-26
## Purpose: Redesign Telegram bot for fashion service

## New Bot Commands & Features

### Core Commands
```
/start - Welcome and onboarding
/help - Show available commands
/profile - Manage fashion profile
/credits - Check remaining credits
/buy - Purchase credits or subscription
/language - Change language (EN/RU)
```

### Virtual Fitting Commands
```
/fitting - Start virtual fitting process
/fitting_history - View past fittings
/fitting_status - Check current fitting status
```

### AI Stylist Commands
```
/stylist - Start AI stylist consultation
/style_analysis - Analyze current style
/recommendations - Get style recommendations
/recommendation_history - View past recommendations
```

### Profile Management
```
/profile_setup - Complete fashion profile setup
/body_type - Set body type
/style_preferences - Set style preferences
/budget - Set budget range
/occasions - Set occasion preferences
```

## User Flow Design

### 1. Welcome Flow (/start)
```
Welcome to MODERA.FASHION! 👗✨

Your AI-powered virtual fitting room and personal stylist.

What would you like to do?

[Virtual Fitting] [AI Stylist] [Profile Setup] [Help]
```

### 2. Virtual Fitting Flow (/fitting)
```
Let's create your virtual fitting! 📸

Step 1: Send me a photo of the clothing item you want to try on
(Please send a clear photo of the clothing on a plain background)

[Cancel] [Help]
```

```
Great! Now send me a photo of yourself
(Please send a full-body photo in good lighting)

[Use Previous Photo] [Cancel] [Help]
```

```
Perfect! Processing your virtual fitting...

⏳ This may take up to 30 seconds

[Check Status] [Cancel]
```

### 3. AI Stylist Flow (/stylist)
```
Welcome to your AI Stylist! 👔

I'll help you discover your perfect style and find amazing clothes.

What would you like to do?

[Analyze My Style] [Get Recommendations] [Style Consultation] [Back]
```

### 4. Profile Setup Flow (/profile_setup)
```
Let's set up your fashion profile! 📋

This helps me give you better recommendations.

Step 1: What's your body type?

[Hourglass] [Rectangle] [Triangle] [Inverted Triangle] [Oval] [Skip]
```

## Keyboard Layouts

### Main Menu Keyboard
```
┌─────────────────┬─────────────────┐
│   👗 Virtual    │   👔 AI Stylist │
│    Fitting      │                 │
├─────────────────┼─────────────────┤
│   👤 Profile    │   💳 Credits    │
│                 │                 │
├─────────────────┼─────────────────┤
│   🛒 Buy        │   ❓ Help        │
└─────────────────┴─────────────────┘
```

### Virtual Fitting Keyboard
```
┌─────────────────┬─────────────────┐
│   📸 Start      │   📚 History    │
│   Fitting       │                 │
├─────────────────┼─────────────────┤
│   📊 Status     │   ⚙️ Settings   │
│                 │                 │
├─────────────────┼─────────────────┤
│   🔙 Back       │   ❓ Help        │
└─────────────────┴─────────────────┘
```

### AI Stylist Keyboard
```
┌─────────────────┬─────────────────┐
│   🔍 Analyze    │   💡 Get        │
│   My Style      │ Recommendations │
├─────────────────┼─────────────────┤
│   💬 Style      │   📚 History    │
│ Consultation    │                 │
├─────────────────┼─────────────────┤
│   🔙 Back       │   ❓ Help        │
└─────────────────┴─────────────────┘
```

## Message Templates

### Welcome Message
```
🎉 Welcome to MODERA.FASHION!

Your personal AI-powered fashion assistant is here to help you:

✨ **Virtual Fitting Room**
Try on clothes virtually with AI technology

👔 **AI Personal Stylist**
Get personalized style recommendations

🎯 **Smart Shopping**
Find perfect clothes with direct purchase links

Start by setting up your profile or try a virtual fitting!

[Setup Profile] [Try Virtual Fitting] [Learn More]
```

### Virtual Fitting Result
```
🎉 Your virtual fitting is ready!

Here's how you look in that outfit:

[Generated Image]

✨ **Outfit Details:**
• Style: [Style Type]
• Fit: [Fit Description]
• Colors: [Color Analysis]

💡 **Styling Tips:**
[AI-generated styling advice]

🛒 **Similar Items:**
[Links to similar items]

[Try Another Fitting] [Get Styling Advice] [Save to Profile]
```

### Style Recommendation
```
👔 Your AI Stylist Recommendations

Based on your style profile, here are perfect items for you:

**🎯 Perfect Match:**
[Item 1] - $XX.XX
[Item 2] - $XX.XX
[Item 3] - $XX.XX

**💡 Why These Work:**
[AI explanation of why these items match your style]

**🛒 Shop Now:**
[Direct purchase links]

[Get More Recommendations] [Adjust Preferences] [Save to Wishlist]
```

## Error Handling

### Insufficient Credits
```
❌ Insufficient Credits

You need more credits to use this feature.

Current credits: [X]
Required credits: [Y]

[Buy Credits] [View Plans] [Back to Menu]
```

### Processing Error
```
⚠️ Processing Error

Sorry, we couldn't process your request. This might be due to:

• Image quality issues
• Server temporarily unavailable
• Invalid image format

[Try Again] [Contact Support] [Back to Menu]
```

### Invalid Image
```
📸 Image Requirements

Please send a photo that meets these requirements:

**For Clothing:**
• Clear, well-lit photo
• Plain background
• Item fully visible

**For Person:**
• Full-body photo
• Good lighting
• Neutral pose

[Try Again] [View Examples] [Get Help]
```

## State Management (FSM - Finite State Machine)

### Core States (Similar to Current c0r.ai Implementation)
MODERA.FASHION will use the same FSM pattern as the current c0r.ai bot, with three main states:

#### 1. **Default State (IDLE)**
- User is in main menu
- No specific action selected
- Photos trigger choice menu (Virtual Fitting vs AI Stylist)

#### 2. **Virtual Fitting State (TRY_ON)**
- User selected virtual fitting
- Waiting for clothing photo
- Waiting for person photo
- Processing virtual fitting

#### 3. **AI Stylist State (AI_STYLIST)**
- User selected AI stylist
- Waiting for person photo
- Processing style analysis
- Generating recommendations

### FSM State Classes
```python
# Virtual Fitting States
class VirtualFittingStates(StatesGroup):
    waiting_for_clothing_photo = State()
    waiting_for_person_photo = State()
    processing_fitting = State()

# AI Stylist States
class AIStylistStates(StatesGroup):
    waiting_for_photo = State()
    processing_analysis = State()
    generating_recommendations = State()

# Profile Setup States (replaces nutrition profile)
class FashionProfileStates(StatesGroup):
    waiting_for_body_type = State()
    waiting_for_style_preferences = State()
    waiting_for_budget = State()
    waiting_for_occasions = State()
```

### State Transition Flow
```python
# Default State Flow
IDLE → User sends photo → Choice menu (Virtual Fitting / AI Stylist)

# Virtual Fitting Flow
IDLE → User clicks "Virtual Fitting" → VirtualFittingStates.waiting_for_clothing_photo
→ User sends clothing photo → VirtualFittingStates.waiting_for_person_photo
→ User sends person photo → VirtualFittingStates.processing_fitting
→ Processing complete → IDLE

# AI Stylist Flow
IDLE → User clicks "AI Stylist" → AIStylistStates.waiting_for_photo
→ User sends photo → AIStylistStates.processing_analysis
→ Analysis complete → AIStylistStates.generating_recommendations
→ Recommendations ready → IDLE

# Profile Setup Flow
IDLE → User clicks "Profile Setup" → FashionProfileStates.waiting_for_body_type
→ User selects body type → FashionProfileStates.waiting_for_style_preferences
→ User sets preferences → FashionProfileStates.waiting_for_budget
→ User sets budget → FashionProfileStates.waiting_for_occasions
→ User sets occasions → IDLE
```

### State Management Implementation
```python
# Handler registration (similar to current c0r.ai)
# FSM handlers (MUST be registered BEFORE general photo handler)
dp.message.register(process_clothing_photo, VirtualFittingStates.waiting_for_clothing_photo)
dp.message.register(process_person_photo, VirtualFittingStates.waiting_for_person_photo)
dp.message.register(process_stylist_photo, AIStylistStates.waiting_for_photo)

# Photo handler (only for photos when no FSM state is set)
dp.message.register(photo_handler, lambda message: message.photo)
```

### State Validation Logic
```python
async def validate_current_state(state: FSMContext) -> str:
    """Validate current state and return appropriate action"""
    current_state = await state.get_state()
    
    if current_state == "VirtualFittingStates:waiting_for_clothing_photo":
        return "expecting_clothing_photo"
    elif current_state == "VirtualFittingStates:waiting_for_person_photo":
        return "expecting_person_photo"
    elif current_state == "AIStylistStates:waiting_for_photo":
        return "expecting_stylist_photo"
    else:
        return "show_choice_menu"
```

## Integration Points

### ML Service Integration
- Send photos to ML service for processing
- Receive virtual fitting results
- Get style analysis and recommendations

### Payment Integration
- Credit purchase flow
- Subscription management
- Payment status updates

### Database Integration
- User profile management
- Session tracking
- Recommendation history

## Internationalization (i18n) Requirements

### Multi-language Support
**CRITICAL:** All new functionality must support both English and Russian languages.

### Translation Requirements
```python
# All new text must be added to i18n system
# Example structure for new features:

# i18n/en/virtual_fitting.py
VIRTUAL_FITTING_WELCOME = "Let's create your virtual fitting! 📸"
VIRTUAL_FITTING_CLOTHING_STEP = "Step 1: Send me a photo of the clothing item you want to try on"
VIRTUAL_FITTING_PERSON_STEP = "Step 2: Send me a photo of yourself"

# i18n/ru/virtual_fitting.py
VIRTUAL_FITTING_WELCOME = "Давайте создадим вашу виртуальную примерку! 📸"
VIRTUAL_FITTING_CLOTHING_STEP = "Шаг 1: Отправьте мне фото одежды, которую хотите примерить"
VIRTUAL_FITTING_PERSON_STEP = "Шаг 2: Отправьте мне ваше фото"

# Usage in handlers
from i18n.i18n import i18n

async def virtual_fitting_handler(message: types.Message, state: FSMContext):
    user_language = get_user_language(message.from_user.id)
    welcome_text = i18n.get_text("VIRTUAL_FITTING_WELCOME", user_language)
    await message.answer(welcome_text)
```

### Required Translation Files
- `i18n/en/virtual_fitting.py` - Virtual fitting messages
- `i18n/en/ai_stylist.py` - AI stylist messages
- `i18n/en/fashion_profile.py` - Fashion profile messages
- `i18n/ru/virtual_fitting.py` - Russian virtual fitting messages
- `i18n/ru/ai_stylist.py` - Russian AI stylist messages
- `i18n/ru/fashion_profile.py` - Russian fashion profile messages

### Translation Checklist
- [ ] All user-facing text translated to EN/RU
- [ ] Error messages translated
- [ ] Button labels translated
- [ ] Help text translated
- [ ] Validation messages translated

## Performance Considerations

### Image Handling
- Compress images before processing
- Validate image format and size
- Store processed images in R2

### Response Time
- Quick acknowledgment messages
- Progress indicators for long operations
- Async processing for AI operations

### Error Recovery
- Graceful handling of service failures
- Retry mechanisms for failed operations
- Clear error messages to users

## Testing Requirements

### Test Coverage Requirements
**CRITICAL:** All new functionality must have comprehensive test coverage.

### Test Structure (Similar to Current c0r.ai)
```python
# Test files structure for MODERA.FASHION
tests/
├── unit/
│   ├── test_virtual_fitting_fsm.py      # FSM tests for virtual fitting
│   ├── test_ai_stylist_fsm.py           # FSM tests for AI stylist
│   ├── test_fashion_profile_fsm.py      # FSM tests for profile setup
│   ├── test_virtual_fitting_handlers.py # Handler tests
│   ├── test_ai_stylist_handlers.py      # Handler tests
│   └── test_fashion_profile_handlers.py # Handler tests
├── integration/
│   ├── test_virtual_fitting_integration.py
│   ├── test_ai_stylist_integration.py
│   └── test_fashion_profile_integration.py
└── mocks/
    └── fashion_services.py              # Mock fashion services
```

### FSM Test Requirements
```python
# Example FSM test structure
class TestVirtualFittingFSM:
    """Test virtual fitting FSM state management"""
    
    @pytest.mark.asyncio
    async def test_virtual_fitting_state_transitions(self, state):
        """Test complete virtual fitting flow"""
        # Test state transitions
        # Test photo processing
        # Test error handling
        
    @pytest.mark.asyncio
    async def test_ai_stylist_state_transitions(self, state):
        """Test complete AI stylist flow"""
        # Test state transitions
        # Test photo processing
        # Test recommendations generation
```

### Test Implementation Timeline
- **Phase 1:** Implement core functionality (Week 3-5)
- **Phase 2:** Write comprehensive tests (Week 6-7)
- **Phase 3:** Test and fix issues (Week 8)

### Test Coverage Targets
- **FSM State Management:** 100%
- **Handler Functions:** 95%
- **Integration Points:** 90%
- **Error Handling:** 100%
- **i18n Support:** 100%
