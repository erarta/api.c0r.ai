# 🚀 Production Testing Guide for c0r.ai Bot

## 📊 **Log Monitoring Commands**

### **Docker Container Logs**
```bash
# View all bot logs in real-time
docker-compose logs -f api

# View last 100 lines of bot logs
docker-compose logs --tail=100 api

# View logs for specific service
docker-compose logs -f ml
docker-compose logs -f pay

# View logs with timestamps
docker-compose logs -f -t api

# Filter logs by level (if using structured logging)
docker-compose logs api | grep "ERROR"
docker-compose logs api | grep "WARNING"
docker-compose logs api | grep "INFO"
```

### **Direct Bot Logs**
```bash
# If running bot directly (not in Docker)
tail -f /var/log/c0r-bot.log

# View recent errors
tail -100 /var/log/c0r-bot.log | grep ERROR

# Monitor specific user actions
tail -f /var/log/c0r-bot.log | grep "user_12345"
```

### **System Monitoring**
```bash
# Check bot process status
ps aux | grep bot.py

# Check memory usage
docker stats api.c0r.ai-api-1

# Check disk usage
df -h

# Check network connections
netstat -tulpn | grep :8000
```

## 🧪 **Step-by-Step Testing Scenarios**

### **Phase 1: Basic Bot Health Check**

#### **Test 1: Bot Responsiveness**
```
1. Open Telegram
2. Find your bot (@your_bot_name)
3. Send: /start
4. Expected: Welcome message with interactive buttons within 3 seconds
```

**Monitor logs:**
```bash
docker-compose logs -f api | grep "start_command"
```

#### **Test 2: Database Connection**
```
1. Send: /status
2. Expected: Your user info, credits, member date
3. Check logs for database queries
```

**Monitor logs:**
```bash
docker-compose logs -f api | grep "status_command"
```

---

### **Phase 2: Core Functionality Testing**

#### **Test 3: Help System**
```
1. Send: /help
2. Expected: Complete help guide with all commands
3. Verify all commands are listed
```

#### **Test 4: Profile Setup (New User)**
```
1. Send: /profile
2. Click "🚀 Start Profile Setup"
3. Enter age: 25
4. Select gender: 👨 Male
5. Enter height: 180
6. Enter weight: 75
7. Select activity: 🏃 Moderately Active
8. Select goal: ⚖️ Maintain Weight
9. Expected: Profile created with calorie calculation
```

**Monitor logs:**
```bash
# Watch profile setup flow
docker-compose logs -f api | grep "profile"
```

#### **Test 5: Photo Analysis (Success)**
```
1. Take a clear photo of food (pizza, burger, etc.)
2. Send photo to bot
3. Expected: 
   - "Uploading and analyzing..." message
   - Food analysis results with calories, protein, fats, carbs
   - Daily progress (if profile exists)
   - Credits deducted
```

**Monitor logs:**
```bash
# Watch photo processing
docker-compose logs -f api | grep "photo_handler"
docker-compose logs -f ml | grep "analyze"
```

#### **Test 6: Photo Analysis (No Food)**
```
1. Send photo without food (landscape, person, etc.)
2. Expected: "No food detected" message
3. Credits NOT deducted
```

---

### **Phase 3: Edge Cases & Error Handling**

#### **Test 7: Invalid Inputs**
```
1. Start profile setup: /profile
2. For age, enter: "abc" (invalid)
3. Expected: Error message asking for valid age
4. Enter valid age: 25
5. Continue setup normally
```

#### **Test 8: Large Photo**
```
1. Send very large photo (>10MB if possible)
2. Expected: "Photo too large" error
3. Credits NOT deducted
```

#### **Test 9: Non-Photo Files**
```
1. Send document/video/audio file
2. Expected: "File type not supported" message
3. Clear instructions to send photos only
```

#### **Test 10: No Credits**
```
1. Use all credits by analyzing photos
2. Try to analyze another photo
3. Expected: "No credits left" message with payment options
4. Payment buttons should be clickable
```

---

### **Phase 4: Advanced Features**

#### **Test 11: Daily Tracking**
```
1. Ensure you have profile setup
2. Analyze 2-3 different food photos
3. Send: /daily
4. Expected: 
   - Daily progress summary
   - Total calories consumed
   - Progress bar visualization
   - Meals analyzed count
```

#### **Test 12: Profile Management**
```
1. Send: /profile (with existing profile)
2. Click "✏️ Edit Profile"
3. Go through setup again with different values
4. Expected: Profile updated, new calorie calculation
```

#### **Test 13: Interactive Buttons**
```
1. Send: /start
2. Click each button:
   - 🍕 Analyze Food Photo
   - 📊 Check My Status
   - ℹ️ Help & Guide
   - 💳 Buy More Credits
   - 👤 My Profile
3. Expected: Each button works correctly
```

---

### **Phase 5: Anti-Spam Protection**

#### **Test 14: Rate Limiting (Photos)**
```
1. Send 6 photos quickly (within 1 minute)
2. Expected: After 5th photo, rate limit message
3. Wait 1 minute, try again
4. Expected: Should work normally
```

**Monitor logs:**
```bash
docker-compose logs -f api | grep "rate_limit"
```

#### **Test 15: Rate Limiting (Commands)**
```
1. Send /status command 21 times quickly
2. Expected: After 20th command, rate limit message
3. Wait 1 minute, try again
```

---

### **Phase 6: Performance & Reliability**

#### **Test 16: Multiple Users**
```
1. Ask 3-5 friends to test bot simultaneously
2. All users send photos at same time
3. Expected: All requests processed successfully
4. No errors or timeouts
```

#### **Test 17: Service Recovery**
```
1. Restart ML service: docker-compose restart ml
2. Send photo immediately after restart
3. Expected: Should work or show proper error message
```

## 🔍 **Log Analysis Commands**

### **Real-time Error Monitoring**
```bash
# Monitor all errors in real-time
docker-compose logs -f api | grep -E "(ERROR|EXCEPTION|Failed)"

# Monitor specific user for debugging
docker-compose logs -f api | grep "user_123456789"

# Monitor photo processing issues
docker-compose logs -f api | grep -E "(photo|analysis|ML)"

# Monitor database issues
docker-compose logs -f api | grep -E "(database|supabase|connection)"
```

### **Performance Monitoring**
```bash
# Monitor response times
docker-compose logs -f api | grep -E "(processing|completed|elapsed)"

# Monitor memory usage
docker stats --no-stream api.c0r.ai-api-1

# Monitor rate limiting
docker-compose logs -f api | grep "rate_limit"
```

### **Success Metrics**
```bash
# Count successful photo analyses
docker-compose logs api | grep "Photo analysis completed" | wc -l

# Count profile setups
docker-compose logs api | grep "Profile created" | wc -l

# Count new users
docker-compose logs api | grep "New user registered" | wc -l
```

## 📋 **Testing Checklist**

### **Before Going Live:**
- [ ] All basic commands work (/start, /help, /status)
- [ ] Profile setup flow complete
- [ ] Photo analysis working correctly
- [ ] Error handling proper
- [ ] Rate limiting active
- [ ] Database logging working
- [ ] Payment buttons clickable (even if not functional)

### **During Testing:**
- [ ] Monitor logs continuously
- [ ] Test with different photo types
- [ ] Test with invalid inputs
- [ ] Test rate limiting
- [ ] Test multiple users
- [ ] Verify database entries

### **After Testing:**
- [ ] Check error logs for issues
- [ ] Verify user data in database
- [ ] Check system resource usage
- [ ] Document any issues found

## 🚨 **Emergency Commands**

### **If Bot Stops Responding:**
```bash
# Restart bot service
docker-compose restart api

# Check if bot is running
docker-compose ps

# Check bot logs for errors
docker-compose logs --tail=50 api
```

### **If Database Issues:**
```bash
# Test database connection
python test_db_connection.py

# Check database logs
docker-compose logs db
```

### **If High Memory Usage:**
```bash
# Check memory usage
docker stats

# Restart services if needed
docker-compose down
docker-compose up -d
```

## 📊 **Success Indicators**

### **Bot is Working Well If:**
- ✅ All commands respond within 3 seconds
- ✅ Photo analysis completes within 30 seconds
- ✅ Error rate < 5% of total requests
- ✅ No memory leaks (stable memory usage)
- ✅ Rate limiting prevents spam
- ✅ Database operations successful

### **Warning Signs:**
- ⚠️ Response times > 10 seconds
- ⚠️ Frequent error messages in logs
- ⚠️ Memory usage continuously growing
- ⚠️ Database connection failures
- ⚠️ ML service timeouts

---

## 📱 **Quick Test Commands for Telegram**

**Copy and paste these into your Telegram chat:**

```
/start
/help
/status
/profile
/daily
/buy
```

**Test photos to send:**
- 🍕 Pizza slice
- 🍔 Hamburger
- 🥗 Salad
- 🍎 Apple
- 🏠 Non-food photo (should fail)

**Happy Testing! 🎉** 