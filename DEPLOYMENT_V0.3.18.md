# 🚀 Deployment Guide - v0.3.18

## Overview

Version 0.3.18 introduces **complete multilingual support** for the c0r.ai Telegram bot, with all features now fully translated to English and Russian, plus language-aware OpenAI prompts.

## ✅ What's New

### Complete Multilingual Support
- **100% Translation Coverage**: All bot messages, buttons, and error messages translated
- **Profile Setup**: Complete translation of age, gender, height, weight, activity, goals setup
- **Photo Analysis**: All analysis messages, tips, and error messages translated
- **Daily Plan**: Progress tracking, recommendations, and status messages translated
- **Nutrition Insights**: All nutrition analysis and recommendations translated
- **OpenAI Language-Aware**: ML service now uses Russian prompts for Russian users

### Enhanced User Experience
- **Seamless Language Switching**: Users can change language without losing functionality
- **Consistent Interface**: All features work identically in both languages
- **Regional Detection**: Smart language detection based on country and phone number
- **Error Localization**: All error messages and rate limiting in user's language

## 🔧 Technical Changes

### Files Modified
- `api.c0r.ai/app/handlers/i18n.py` - Enhanced with comprehensive translations
- `api.c0r.ai/app/handlers/profile.py` - All profile setup messages translated
- `api.c0r.ai/app/handlers/photo.py` - Photo analysis messages translated
- `api.c0r.ai/app/handlers/daily.py` - Daily plan interface translated
- `api.c0r.ai/app/handlers/nutrition.py` - Nutrition insights translated
- `ml.c0r.ai/app/main.py` - Added language-aware OpenAI prompts
- `CHANGELOG.md` - Updated with v0.3.18 changes

### New Files
- `REGIONAL_IDENTIFICATION_PROPOSAL.md` - Future regional identification proposal
- `test_language_simple.py` - Language detection test suite

## 🚀 Deployment Steps

### 1. Database Migration (Already Done)
The multilingual database migration was already applied in v0.3.16:
- ✅ `language` column added to `users` table
- ✅ `country` and `phone_number` columns added
- ✅ Language detection indexes created

### 2. Code Deployment

```bash
# 1. Pull latest changes
git pull origin main

# 2. Verify version
grep "## \[0.3.18\]" CHANGELOG.md

# 3. Rebuild containers
docker-compose build

# 4. Restart services
docker-compose down
docker-compose up -d

# 5. Check logs
docker-compose logs -f api
docker-compose logs -f ml
```

### 3. Verification Steps

#### Test Language Detection
```bash
# Run language detection tests
python3 test_language_simple.py
```

Expected output:
```
🎉 ALL TESTS PASSED!
✅ Language detection works correctly
✅ Translations are complete
✅ Language names are correct
```

#### Test Bot Functionality
1. **Start Bot**: Send `/start` - should detect language automatically
2. **Language Switch**: Send `/language` - should show language selection menu
3. **Profile Setup**: Send `/profile` - all messages should be in user's language
4. **Photo Analysis**: Send a food photo - analysis should be in user's language
5. **Daily Plan**: Send `/daily` - plan should display in user's language

## 🔍 Testing Checklist

### Language Detection
- [ ] Russian users (RU, BY, KZ, etc.) get Russian by default
- [ ] English users (US, GB, DE, etc.) get English by default
- [ ] Phone number detection works (+7, +375, etc.)
- [ ] Language switching works correctly

### Profile Setup
- [ ] Age input messages in correct language
- [ ] Gender selection in correct language
- [ ] Height/weight validation in correct language
- [ ] Activity level selection in correct language
- [ ] Goal selection in correct language
- [ ] Success messages in correct language

### Photo Analysis
- [ ] Upload messages in correct language
- [ ] "No food detected" messages in correct language
- [ ] Analysis errors in correct language
- [ ] Service unavailable messages in correct language
- [ ] OpenAI responses in user's language

### Daily Plan
- [ ] Plan title and headers in correct language
- [ ] Progress status messages in correct language
- [ ] Recommendations in correct language
- [ ] Button labels in correct language

### Nutrition Insights
- [ ] Profile completion prompts in correct language
- [ ] Analysis results in correct language
- [ ] Error messages in correct language

## 🐛 Known Issues

### None Known
- All tests pass successfully
- No breaking changes introduced
- Backward compatibility maintained

## 📊 Monitoring

### Key Metrics to Watch
1. **Language Distribution**: Monitor user language preferences
2. **Error Rates**: Check for any translation-related errors
3. **User Engagement**: Compare engagement between languages
4. **Photo Analysis Success**: Ensure analysis works in both languages

### Log Monitoring
```bash
# Monitor API logs
docker-compose logs -f api | grep -i "language\|translation"

# Monitor ML service logs
docker-compose logs -f ml | grep -i "language\|prompt"
```

## 🔄 Rollback Plan

If issues arise, rollback is simple:

```bash
# 1. Revert to previous version
git checkout v0.3.17

# 2. Rebuild and restart
docker-compose build
docker-compose down
docker-compose up -d

# 3. Verify rollback
docker-compose logs api | head -20
```

## 📈 Post-Deployment

### Analytics
- Monitor user language preferences in database
- Track feature usage by language
- Analyze user engagement patterns

### Feedback Collection
- Monitor user feedback about language experience
- Check for any missing translations
- Gather suggestions for improvements

### Future Enhancements
- Review `REGIONAL_IDENTIFICATION_PROPOSAL.md` for next steps
- Consider adding more languages based on user demand
- Implement region-specific features

## ✅ Success Criteria

Deployment is successful when:
1. ✅ All language detection tests pass
2. ✅ Bot responds in correct language for all features
3. ✅ No translation-related errors in logs
4. ✅ User engagement remains stable or improves
5. ✅ Photo analysis works correctly in both languages

## 🆘 Support

If issues arise:
1. Check logs: `docker-compose logs -f`
2. Run tests: `python3 test_language_simple.py`
3. Verify database: Check `users` table language column
4. Contact development team with specific error details

---

**Deployment Status**: ✅ Ready for Production
**Risk Level**: 🟢 Low (backward compatible, well-tested)
**Estimated Downtime**: 2-3 minutes (container restart) 