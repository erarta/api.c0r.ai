# 🔍 How to Get Your Telegram User ID

## 📱 **Method 1: Using @userinfobot (Easiest)**

1. Open Telegram
2. Search for `@userinfobot`
3. Start the bot with `/start`
4. It will send you your User ID immediately

**Example output:**
```
Your ID: 123456789
Your Username: @your_username
```

---

## 🤖 **Method 2: Using Your Bot Logs**

1. Send any command to your bot (like `/start`)
2. Check the bot logs:
   ```bash
   docker-compose logs api | grep "telegram_user_id" | tail -1
   ```
3. Your ID will be in the log message

---

## 🔧 **Method 3: Interactive Script**

Run the reset script without arguments to see recent users:
```bash
python reset_user_data.py
```

Choose option 1 to list recent users and find your ID.

---

## ⚡ **Quick Reset Commands**

### **Reset Your Data (Replace YOUR_ID with actual ID):**
```bash
# Direct reset
python reset_user_data.py YOUR_TELEGRAM_ID

# Interactive mode
python reset_user_data.py
```

### **Reset All Test Data:**
```bash
python reset_user_data.py
# Then choose option 3
```

---

## 🎯 **Complete Reset Process**

### **Step 1: Get Your Telegram ID**
```bash
# Use @userinfobot or check logs
docker-compose logs api | grep "telegram_user_id" | tail -5
```

### **Step 2: Reset Your Data**
```bash
python reset_user_data.py YOUR_TELEGRAM_ID
```

### **Step 3: Test as New User**
```bash
# Start monitoring
./monitor_bot.sh users

# In Telegram, send:
/start
```

You should see the welcome message for a new user with 3 credits!

---

## 🚨 **Alternative: Full Bot Restart**

If you want to restart the bot service completely:

```bash
# Stop bot
docker-compose down

# Clean logs (optional)
docker-compose logs api > old_logs_backup.txt

# Start fresh
docker-compose up -d

# Monitor startup
docker-compose logs -f api
```

---

## 🎮 **Testing Scenarios**

### **New User Flow Test:**
1. Reset your data: `python reset_user_data.py YOUR_ID`
2. `/start` → Should show welcome for new user
3. `/status` → Should show 3 credits
4. `/profile` → Should show setup prompt

### **Returning User Flow Test:**
1. Use bot normally (set up profile, analyze photos)
2. `/start` → Should show existing user welcome
3. `/status` → Should show remaining credits
4. `/profile` → Should show existing profile

---

**Happy Testing! 🎉** 