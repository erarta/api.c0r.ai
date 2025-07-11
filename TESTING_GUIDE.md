# 🧪 Local Testing Guide for c0r.ai Bot

## 📋 **Pre-Testing Setup**

### 1. **Environment Setup**
```bash
# Clone the repository
git clone https://github.com/your-repo/api.c0r.ai.git
cd api.c0r.ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Environment Variables**
Create `.env` file in the root directory:
```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_test_bot_token

# Supabase Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# ML Service
ML_SERVICE_URL=http://localhost:8001

# Cloudflare R2 (Optional for local testing)
CLOUDFLARE_R2_ACCOUNT_ID=your_account_id
CLOUDFLARE_R2_ACCESS_KEY=your_access_key
CLOUDFLARE_R2_SECRET_KEY=your_secret_key
CLOUDFLARE_R2_BUCKET_NAME=your_bucket_name
```

### 3. **Database Setup**
```bash
# Run database migrations (if needed)
python scripts/migrate.sh
```

## 🤖 **Testing Strategy**

### **Phase 1: Basic Commands Testing**

#### Test Cases:
1. **Start Command** (`/start`)
   - ✅ New user registration
   - ✅ Interactive menu display
   - ✅ Credits initialization (3 credits)
   - ✅ Proper logging

2. **Help Command** (`/help`)
   - ✅ Complete guide display
   - ✅ All commands listed
   - ✅ Proper formatting

3. **Status Command** (`/status`)
   - ✅ User info display
   - ✅ Credits remaining
   - ✅ Member since date
   - ✅ System version

### **Phase 2: Profile System Testing**

#### Test Cases:
1. **Profile Setup** (`/profile`)
   - ✅ New user flow
   - ✅ Age validation (10-120)
   - ✅ Height validation (100-250 cm)
   - ✅ Weight validation (30-300 kg)
   - ✅ Gender selection buttons
   - ✅ Activity level buttons
   - ✅ Goal selection buttons
   - ✅ Daily calorie calculation
   - ✅ Profile completion flow

2. **Profile Interruption Handling**
   - ✅ `/profile` command during setup (restart)
   - ✅ Invalid input handling
   - ✅ FSM state management

3. **Profile Editing**
   - ✅ Edit existing profile
   - ✅ Recalculate calories
   - ✅ Progress display

### **Phase 3: Photo Analysis Testing**

#### Test Cases:
1. **Valid Photo Analysis**
   - ✅ Food detection
   - ✅ KBZHU calculation
   - ✅ Credits deduction
   - ✅ Progress tracking (with profile)
   - ✅ R2 upload
   - ✅ Database logging

2. **Invalid Photo Scenarios**
   - ✅ No food detected
   - ✅ Photo too large (>10MB)
   - ✅ Non-photo files (documents, videos)
   - ✅ Credits not deducted on failure
   - ✅ Proper error messages

3. **No Credits Scenario**
   - ✅ Payment options display
   - ✅ Analysis blocked
   - ✅ Buy buttons functional

### **Phase 4: Anti-Spam Protection Testing**

#### Test Cases:
1. **Rate Limiting**
   - ✅ Photo analysis: 5 photos/minute limit
   - ✅ General commands: 20 commands/minute limit
   - ✅ Rate limit messages
   - ✅ Countdown timers

2. **DDOS Protection**
   - ✅ Multiple rapid requests
   - ✅ System stability
   - ✅ Fair usage enforcement

### **Phase 5: Daily Tracking Testing**

#### Test Cases:
1. **Daily Plan** (`/daily`)
   - ✅ Profile required check
   - ✅ Progress display
   - ✅ Calorie tracking
   - ✅ Macro breakdown
   - ✅ Goal progress bar

2. **Progress Tracking**
   - ✅ Daily consumption calculation
   - ✅ Multiple meals tracking
   - ✅ Progress visualization

## 🧪 **Manual Testing Script**

### **Quick Test Sequence**
```bash
# Start the bot
cd api.c0r.ai/app
python bot.py

# In Telegram, test these commands in order:
# 1. /start
# 2. /help
# 3. /status
# 4. /profile (complete setup)
# 5. Send food photo
# 6. /daily
# 7. /buy
```

### **Rate Limiting Test**
```bash
# Send 6 photos quickly to test rate limiting
# Send 21 commands quickly to test general rate limiting
```

### **Error Handling Test**
```bash
# Send non-photo files
# Send very large photos
# Send photos with no food
# Use commands during profile setup
```

## 🔧 **Local ML Service Setup**

### **Option 1: Mock ML Service**
Create `mock_ml_service.py`:
```python
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/analyze")
async def analyze_photo(image: UploadFile = File(...)):
    # Mock response
    return {
        "kbzhu": {
            "calories": 250,
            "proteins": 15,
            "fats": 10,
            "carbohydrates": 30
        },
        "food_items": [
            {
                "name": "Test Food",
                "weight": "100g",
                "calories": 250
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### **Option 2: Use Docker Compose**
```bash
# Start all services
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f api
```

## 📊 **Testing Checklist**

### **Before Release:**
- [ ] All commands work correctly
- [ ] Profile setup flow complete
- [ ] Photo analysis functional
- [ ] Rate limiting active
- [ ] Error handling proper
- [ ] Database logging working
- [ ] R2 upload functional (if configured)
- [ ] Payment flow prepared
- [ ] Anti-spam protection active

### **Performance Tests:**
- [ ] 100 concurrent users simulation
- [ ] Large photo handling
- [ ] Database query optimization
- [ ] Memory usage monitoring
- [ ] Rate limiting effectiveness

## 🚀 **Automated Testing**

### **Unit Tests**
```bash
# Run unit tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_profile.py -v

# Run with coverage
python -m pytest tests/ --cov=handlers --cov-report=html
```

### **Integration Tests**
```bash
# Test database connections
python test_db_connection.py

# Test ML service connection
python test_ml_service.py

# Test Telegram bot connection
python test_bot_connection.py
```

## 📝 **Test Data**

### **Sample Test Photos**
- ✅ Clear food photo (should detect food)
- ✅ Blurry photo (should detect food but warn)
- ✅ Non-food photo (should not detect food)
- ✅ Large photo (>10MB, should be rejected)
- ✅ Multiple dishes photo (should detect multiple items)

### **Test User Data**
```python
test_profiles = [
    {
        "age": 25,
        "gender": "male",
        "height_cm": 180,
        "weight_kg": 75,
        "activity_level": "moderately_active",
        "goal": "maintain_weight"
    },
    {
        "age": 30,
        "gender": "female", 
        "height_cm": 165,
        "weight_kg": 60,
        "activity_level": "lightly_active",
        "goal": "lose_weight"
    }
]
```

## 🐛 **Common Issues & Solutions**

### **Bot Not Starting**
```bash
# Check token
echo $TELEGRAM_BOT_TOKEN

# Check dependencies
pip list | grep aiogram

# Check logs
tail -f logs/bot.log
```

### **Database Connection Issues**
```bash
# Test Supabase connection
python -c "from common.supabase_client import supabase; print('Connected!' if supabase else 'Failed!')"
```

### **ML Service Issues**
```bash
# Check ML service
curl -X POST http://localhost:8001/analyze -F "image=@test_photo.jpg"
```

## 📈 **Performance Monitoring**

### **Key Metrics to Track**
- Response time for photo analysis
- Database query execution time
- Memory usage during peak load
- Rate limiting effectiveness
- Error rates by function

### **Logging**
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Monitor specific functions
from loguru import logger
logger.add("testing.log", rotation="1 MB")
```

## ✅ **Test Results Documentation**

Create `test_results.md` after each testing session:
```markdown
# Test Results - [Date]

## ✅ Passed Tests
- [ ] All basic commands
- [ ] Profile setup flow
- [ ] Photo analysis
- [ ] Rate limiting
- [ ] Error handling

## ❌ Failed Tests
- [ ] Issue description
- [ ] Steps to reproduce
- [ ] Expected vs actual behavior

## 🔧 Fixes Applied
- [ ] Fix description
- [ ] Code changes made
- [ ] Re-test results
```

---

**Happy Testing! 🎉**

Remember: Thorough testing prevents production issues and ensures great user experience. 