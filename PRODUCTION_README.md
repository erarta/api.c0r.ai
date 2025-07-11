# 🚀 c0r.ai Bot - Production Testing & Monitoring

## ⚡ Quick Start Commands

### **1. Pre-Testing Check**
```bash
# Test environment and bot connection
python test_bot_connection.py

# Test database connection
python test_db_connection.py

# Check if services are running
docker-compose ps
```

### **2. Start Monitoring**
```bash
# Start error monitoring (recommended for production)
./monitor_bot.sh errors

# Or start comprehensive monitoring
./monitor_bot.sh all

# Quick stats check
./monitor_bot.sh stats
```

### **3. Start Bot Services**
```bash
# Start all services
docker-compose up -d

# Check if started successfully
docker-compose ps

# View startup logs
docker-compose logs api
```

---

## 📱 Telegram Testing Sequence

### **Phase 1: Basic Commands (2 min)**
```
/start    → Welcome message with buttons
/help     → Complete help guide
/status   → User info, credits, member date
```

### **Phase 2: Profile Setup (3 min)**
```
/profile  → Start profile setup
          → Age: 25
          → Gender: Male
          → Height: 180
          → Weight: 75
          → Activity: Moderately Active
          → Goal: Maintain Weight
```

### **Phase 3: Photo Analysis (2 min)**
- Send food photo → Analysis results + progress
- Send non-food photo → "No food detected" message

### **Phase 4: Advanced Features (2 min)**
```
/daily    → Daily progress with calories
/buy      → Payment options with buttons
```

### **Phase 5: Stress Test (1 min)**
- Send 6 photos quickly → Rate limit after 5th photo

---

## 🔍 Log Monitoring Commands

### **Real-time Monitoring**
```bash
# All errors (recommended)
./monitor_bot.sh errors

# User activity
./monitor_bot.sh users

# All logs with colors
./monitor_bot.sh logs

# Performance metrics
./monitor_bot.sh performance
```

### **Docker Logs**
```bash
# Real-time bot logs
docker-compose logs -f api

# Last 50 lines
docker-compose logs --tail=50 api

# Filter errors
docker-compose logs api | grep ERROR

# ML service logs
docker-compose logs -f ml
```

### **Quick Checks**
```bash
# Recent errors
docker-compose logs --tail=20 api | grep ERROR

# System stats
docker stats

# Service status
docker-compose ps
```

---

## 🚨 Emergency Commands

### **Bot Not Responding**
```bash
# Restart bot
docker-compose restart api

# Check status
docker-compose ps

# View recent logs
docker-compose logs --tail=20 api
```

### **Database Issues**
```bash
# Test database
python test_db_connection.py

# Check database service
docker-compose logs db
```

### **High Memory Usage**
```bash
# Check memory
docker stats

# Restart all services
docker-compose down
docker-compose up -d
```

---

## 📊 Success Indicators

### **✅ Bot Working Well**
- Commands respond within 3 seconds
- Photo analysis completes within 30 seconds
- Profile setup works smoothly
- Rate limiting prevents spam
- No errors in logs
- Database operations successful

### **❌ Warning Signs**
- Response times > 10 seconds
- ERROR messages in logs
- Photo analysis failures
- Database connection issues
- Memory usage growing continuously

---

## 🎯 One-Line Commands

### **Terminal Commands**
```bash
# Quick monitoring
./monitor_bot.sh errors

# Check everything is running
docker-compose ps && ./monitor_bot.sh stats

# Restart if needed
docker-compose restart api && docker-compose logs -f api
```

### **Telegram Commands**
```
/start
/help
/status
/profile
/daily
/buy
```

---

## 📋 Testing Checklist

### **Pre-Production**
- [ ] Environment variables set
- [ ] Database connection working
- [ ] Bot token valid
- [ ] ML service accessible
- [ ] Docker services running

### **During Testing**
- [ ] /start command works
- [ ] Profile setup completes
- [ ] Photo analysis functional
- [ ] Rate limiting active
- [ ] No errors in logs
- [ ] Performance acceptable

### **Post-Testing**
- [ ] Check error logs
- [ ] Verify database entries
- [ ] Monitor system resources
- [ ] Document any issues

---

## 🔧 File Structure

```
api.c0r.ai/
├── monitor_bot.sh              # Monitoring script
├── test_bot_connection.py      # Bot connection test
├── test_db_connection.py       # Database test
├── PRODUCTION_TESTING_COMMANDS.md   # Detailed testing guide
├── QUICK_PROD_TEST.md          # Quick testing checklist
├── TESTING_GUIDE.md            # Local testing guide
└── app/
    ├── bot.py                  # Main bot script
    ├── handlers/               # Command handlers
    │   ├── commands.py
    │   ├── photo.py
    │   ├── profile.py
    │   └── daily.py
    └── utils/                  # Utilities
```

---

## 🚀 Production Deployment

### **1. Environment Setup**
```bash
# Create .env file with production values
cp .env.example .env
# Edit with your production credentials
```

### **2. Start Services**
```bash
# Build and start
docker-compose up -d --build

# Verify startup
docker-compose ps
docker-compose logs api
```

### **3. Test Bot**
```bash
# Run connection tests
python test_bot_connection.py
python test_db_connection.py

# Start monitoring
./monitor_bot.sh errors
```

### **4. Go Live**
```bash
# Test in Telegram
# Follow QUICK_PROD_TEST.md checklist
# Monitor logs for any issues
```

---

## 📞 Support

### **If Issues Occur**
1. Check logs: `./monitor_bot.sh errors`
2. Restart services: `docker-compose restart api`
3. Test connections: `python test_bot_connection.py`
4. Check system resources: `docker stats`

### **Files to Check**
- `PRODUCTION_TESTING_COMMANDS.md` - Detailed testing guide
- `QUICK_PROD_TEST.md` - Quick 10-minute test
- `TESTING_GUIDE.md` - Local development testing
- `CHANGELOG.md` - Recent changes and fixes

---

**🎉 Your c0r.ai bot is ready for production!**

**Total setup time: ~5 minutes**  
**Total testing time: ~10 minutes** 