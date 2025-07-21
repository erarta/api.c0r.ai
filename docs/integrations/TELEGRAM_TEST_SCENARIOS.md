# Telegram Bot Test Scenarios - c0r.ai

## 🔍 Test Environment Setup
- **Bot**: @your_bot_name
- **Test User**: Fresh user (no previous data)
- **Expected**: All tests should pass without errors

---

## 📋 Test Scenario #1: New User Onboarding

### Step 1: Initial Contact
1. Send `/start` to bot
2. **Expected**: 
   - Welcome message with explanation
   - 4 buttons: "📊 Status", "👤 Profile", "💰 Buy Credits", "❓ Help"
   - User gets 3 free credits

### Step 2: Check Status
1. Click "📊 Status" button
2. **Expected**:
   - Shows credits: 3
   - Shows profile: Not set up
   - Message about setting up profile

### Step 3: Get Help
1. Click "❓ Help" button
2. **Expected**:
   - Detailed help message
   - Instructions for all commands
   - Examples of usage

---

## 📋 Test Scenario #2: Profile Setup

### Step 1: Start Profile Setup
1. Click "👤 Profile" button (or send `/profile`)
2. **Expected**: 
   - Message asking for age
   - Format: "Please enter your age (10-120 years):"

### Step 2: Test Age Validation
1. Enter invalid age: `5`
2. **Expected**: Error message "Age must be between 10 and 120 years"
3. Enter valid age: `25`
4. **Expected**: Message asking for gender

### Step 3: Test Gender Selection
1. Enter invalid gender: `alien`
2. **Expected**: Error message "Please enter 'male' or 'female'"
3. Enter valid gender: `male`
4. **Expected**: Message asking for height

### Step 4: Test Height Validation
1. Enter invalid height: `50`
2. **Expected**: Error message "Height must be between 100 and 250 cm"
3. Enter valid height: `180`
4. **Expected**: Message asking for weight

### Step 5: Test Weight Validation
1. Enter invalid weight: `500`
2. **Expected**: Error message "Weight must be between 30 and 300 kg"
3. Enter valid weight: `75`
4. **Expected**: Message asking for activity level

### Step 6: Test Activity Level Selection
1. Enter invalid activity: `superhuman`
2. **Expected**: Error message with valid options
3. Enter valid activity: `moderate`
4. **Expected**: Message asking for goal

### Step 7: Test Goal Selection
1. Enter invalid goal: `become_superhero`
2. **Expected**: Error message with valid options
3. Enter valid goal: `lose_weight`
4. **Expected**: Profile setup complete confirmation

### Step 8: Verify Profile Saved
1. Click "📊 Status" button
2. **Expected**:
   - Shows profile: Complete
   - Shows all entered data
   - Shows credits: 3

---

## 📋 Test Scenario #3: Daily Calories Calculation

### Step 1: Calculate TDEE
1. Send `/daily` command
2. **Expected**:
   - Calculated TDEE (Total Daily Energy Expenditure)
   - Personalized recommendations based on goal
   - Breakdown explanation

### Step 2: Test Without Profile
1. **Note**: Test this with a fresh user who hasn't set up profile
2. Send `/daily` command
3. **Expected**: Error message asking to set up profile first

---

## 📋 Test Scenario #4: Photo Analysis

### Step 1: Send Valid Food Photo
1. Send a clear photo of food (e.g., apple, sandwich)
2. **Expected**:
   - "Processing your photo..." message
   - Analysis results with:
     - Food items detected
     - Calories per item
     - Total calories
     - Nutritional breakdown
   - Credits deducted (check with `/status`)

### Step 2: Test Photo Size Limit
1. Send a photo larger than 10MB
2. **Expected**: Error message "Photo is too large. Please send a photo smaller than 10MB"
3. Credits should NOT be deducted

### Step 3: Test Non-Food Photo
1. Send a photo without food (e.g., landscape, person)
2. **Expected**: 
   - "No food detected" message
   - Credits should NOT be deducted
   - Suggestion to send food photo

### Step 4: Test No Photo
1. Send a text message instead of photo
2. **Expected**: Instructions to send a photo

---

## 📋 Test Scenario #5: Rate Limiting

### Step 1: Test Photo Rate Limit
1. Send 6 photos quickly (within 1 minute)
2. **Expected**: 
   - First 5 photos processed normally
   - 6th photo triggers rate limit message
   - Message shows countdown timer

### Step 2: Test Command Rate Limit
1. Send `/status` command 21 times quickly
2. **Expected**:
   - First 20 commands processed normally
   - 21st command triggers rate limit message
   - Message shows countdown timer

### Step 3: Wait for Rate Limit Reset
1. Wait for countdown to finish
2. Send another photo or command
3. **Expected**: Normal processing resumes

---

## 📋 Test Scenario #6: Credits System

### Step 1: Use All Free Credits
1. Send 3 food photos (use all free credits)
2. **Expected**: Each photo analysis deducts 1 credit

### Step 2: Test Zero Credits
1. Send 4th photo (when credits = 0)
2. **Expected**: 
   - "Insufficient credits" message
   - Instructions to buy more credits
   - Photo not processed

### Step 3: Buy Credits
1. Click "💰 Buy Credits" button
2. **Expected**:
   - Payment options displayed
   - Stripe and YooKassa buttons
   - Price information

---

## 📋 Test Scenario #7: Error Handling

### Step 1: Test Invalid Commands
1. Send `/invalid_command`
2. **Expected**: Helpful error message or redirection to help

### Step 2: Test Profile Reset
1. Complete profile setup
2. Send `/profile` again
3. **Expected**: Profile setup restarts from beginning

### Step 3: Test System Errors
1. Send photo when ML service is down
2. **Expected**: 
   - Error message about temporary unavailability
   - Credits not deducted
   - Instructions to try again later

---

## 📋 Test Scenario #8: Navigation Flow

### Step 1: Main Menu Navigation
1. Send `/start`
2. Test all 4 buttons work correctly
3. **Expected**: Each button leads to appropriate function

### Step 2: Command vs Button Testing
1. Test `/help` command vs "❓ Help" button
2. Test `/status` command vs "📊 Status" button
3. **Expected**: Both should produce same results

---

## 📋 Test Scenario #9: Data Persistence

### Step 1: Set Up Profile and Use Credits
1. Complete profile setup
2. Use some credits for photo analysis
3. Note current status

### Step 2: Restart Conversation
1. Send `/start` again
2. Check status
3. **Expected**: 
   - Profile data preserved
   - Credits balance preserved
   - Previous analysis history maintained

---

## 📋 Test Scenario #10: Edge Cases

### Step 1: Empty Messages
1. Send empty message
2. **Expected**: Helpful guidance message

### Step 2: Very Long Messages
1. Send very long text message
2. **Expected**: Appropriate handling without errors

### Step 3: Special Characters
1. Enter profile data with special characters
2. **Expected**: Proper validation and sanitization

---

## 🔍 Success Criteria

### ✅ All scenarios should pass with:
- No Python errors or exceptions
- Appropriate user feedback for all actions
- Correct credit deduction/preservation
- Profile data validation working
- Rate limiting functioning
- Navigation buttons working
- Data persistence maintained

### 📊 Monitor During Testing:
- Check logs: `docker-compose logs -f api`
- Monitor database entries
- Verify Cloudflare R2 photo uploads
- Check payment webhook functionality

### 🚨 Critical Issues to Watch:
- Credit deduction on failed analysis
- Profile data validation bypass
- Rate limiting not working
- Database connection errors
- Photo upload failures

---

## 📞 Emergency Commands

If bot becomes unresponsive:
```bash
# Restart bot
docker-compose restart api

# Check logs
docker-compose logs -f api

# Check database
python test_db_connection.py
```

---

**Test Duration**: ~30-45 minutes for complete testing
**Recommended**: Test with 2-3 different users for comprehensive coverage 