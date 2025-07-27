# ⚡ Quick Production Testing - c0r.ai Bot

## 🚀 **1. Start Monitoring (Run in Terminal)**

```bash
# Option 1: All logs with colors
./monitor_bot.sh logs

# Option 2: Only errors (recommended for production)
./monitor_bot.sh errors

# Option 3: User activity only
./monitor_bot.sh users

# Option 4: Quick stats check
./monitor_bot.sh stats
```

## 📱 **2. Telegram Testing Sequence**

### **Phase 1: Basic Tests (2 minutes)**
Open Telegram → Find your bot → Test these commands:

```
/start
```
**✅ Expected:** Welcome message with buttons in 3 seconds

```
/help
```
**✅ Expected:** Complete help guide

```
/status
```
**✅ Expected:** Your user info, credits, member date

### **Phase 2: Profile Test (3 minutes)**
```
/profile
```
**✅ Steps:**
1. Click "🚀 Start Profile Setup"
2. Age: `25`
3. Gender: `👨 Male`
4. Height: `180`
5. Weight: `75`
6. Activity: `🏃 Moderately Active`
7. Goal: `⚖️ Maintain Weight`

**✅ Expected:** Profile created + calorie calculation

### **Phase 3: Photo Analysis (2 minutes)**
1. **Send food photo** (pizza, burger, etc.)
2. **✅ Expected:** 
   - "Uploading and analyzing..." message
   - Food analysis results
   - Daily progress
   - Credits deducted

3. **Send non-food photo** (landscape, person)
4. **✅ Expected:** 
   - "No food detected" message
   - Credits NOT deducted

### **Phase 4: Advanced Features (2 minutes)**
```
/daily
```
**✅ Expected:** Daily progress with calories, progress bar

```
/buy
```
**✅ Expected:** Payment options with clickable buttons

### **Phase 5: Stress Test (1 minute)**
- Send 6 photos quickly
- **✅ Expected:** Rate limit message after 5th photo

---

## 🔍 **3. Check Logs for Issues**

```bash
# Quick error check
docker-compose logs --tail=50 api | grep ERROR

# Check recent activity
docker-compose logs --tail=20 api
```

## 📊 **4. Success Indicators**

**✅ Bot is working if:**
- All commands respond within 3 seconds
- Photo analysis works
- Profile setup completes
- Rate limiting works
- No errors in logs

**❌ Issues to watch for:**
- Commands taking >10 seconds
- ERROR messages in logs
- Photo analysis failures
- Database connection issues

---

## 🚨 **5. Emergency Commands**

**If bot stops responding:**
```bash
docker-compose restart api
docker-compose ps
```

**If errors in logs:**
```bash
./monitor_bot.sh errors
```

**Check system resources:**
```bash
docker stats
df -h
```

---

## 📋 **6. Quick Test Results**

**Date:** _______  
**Time:** _______  

**✅ Tests Passed:**
- [ ] /start command
- [ ] /help command  
- [ ] /status command
- [ ] Profile setup
- [ ] Photo analysis (food)
- [ ] Photo analysis (no food)
- [ ] /daily command
- [ ] /buy command
- [ ] Rate limiting
- [ ] No errors in logs

**❌ Issues Found:**
- [ ] _________________________________
- [ ] _________________________________
- [ ] _________________________________

**📈 Performance:**
- Response time: _____ seconds
- Memory usage: _____ MB
- Error rate: _____ %

---

## 🎯 **7. One-Line Test Commands**

**Copy these to terminal:**

```bash
# Start monitoring
./monitor_bot.sh errors

# Check stats
./monitor_bot.sh stats

# Check if running
docker-compose ps

# Restart if needed
docker-compose restart api
```

**Copy these to Telegram:**

```
/start
/help
/status
/profile
/daily
/buy
```

---

**Total Test Time: ~10 minutes**  
**Happy Testing! 🎉** 