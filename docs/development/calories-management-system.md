# Calories Management System

## Overview

The Calories Management System is a comprehensive solution for tracking user's daily, weekly, and monthly calorie consumption. It provides a centralized way to manage nutrition data and generate reports for users.

## Architecture

### Components

1. **CaloriesManager Class** (`common/calories_manager.py`)
   - Main class for managing calorie tracking
   - Handles adding calories from food analysis
   - Provides methods for getting daily, weekly, and monthly summaries

2. **Database Table** (`daily_calories`)
   - Stores aggregated daily nutrition data
   - One entry per user per day
   - Includes total calories, proteins, fats, and carbohydrates

3. **Integration Points**
   - Photo analysis handler (`services/api/bot/handlers/photo.py`)
   - Database migrations (`migrations/database/2025-08-05_daily_calories_table.sql`)

## How It Works

### 1. Adding Calories from Food Analysis

When a user uploads a photo for analysis:

```python
# Extract nutrition data from ML service response
nutrition = analysis_data["analysis"]["total_nutrition"]
calories = float(nutrition.get("calories", 0))
proteins = float(nutrition.get("proteins", 0))
fats = float(nutrition.get("fats", 0))
carbohydrates = float(nutrition.get("carbohydrates", 0))
```

The system then:
1. **Checks if entry exists for today**
   - If exists: Updates the existing entry by adding new values
   - If not exists: Creates a new entry for today

2. **Logs the individual food analysis**
   - Stores detailed information in the `logs` table
   - Includes photo URL and full analysis data

3. **Returns updated daily summary**
   - Provides current day's total consumption
   - Used for displaying progress to user

### 2. Daily Summary Retrieval

```python
# Get daily calories for user
daily_summary = await get_daily_calories(user_id, date)
```

Returns:
```json
{
    "date": "2025-08-05",
    "total_calories": 297.0,
    "total_proteins": 8.0,
    "total_fats": 3.0,
    "total_carbohydrates": 65.0,
    "food_items_count": 1,
    "food_items": []
}
```

### 3. Weekly Summary

```python
# Get weekly calories for user
weekly_summary = await get_weekly_calories(user_id, end_date)
```

Returns:
```json
{
    "start_date": "2025-07-30",
    "end_date": "2025-08-05",
    "total_calories": 2100.0,
    "average_calories": 300.0,
    "total_proteins": 56.0,
    "total_fats": 21.0,
    "total_carbohydrates": 455.0,
    "days_with_data": 7,
    "days_count": 7
}
```

### 4. Monthly Summary

```python
# Get monthly calories for user
monthly_summary = await get_monthly_calories(user_id, year, month)
```

Returns:
```json
{
    "year": 2025,
    "month": 8,
    "total_calories": 9300.0,
    "average_calories": 300.0,
    "total_proteins": 248.0,
    "total_fats": 93.0,
    "total_carbohydrates": 1950.0,
    "days_with_data": 31,
    "days_in_month": 31
}
```

## Database Schema

### daily_calories Table

```sql
CREATE TABLE daily_calories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_calories DECIMAL(10,2) DEFAULT 0,
    total_proteins DECIMAL(10,2) DEFAULT 0,
    total_fats DECIMAL(10,2) DEFAULT 0,
    total_carbohydrates DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure one entry per user per day
    UNIQUE(user_id, date)
);
```

## Key Features

### 1. **Automatic Aggregation**
- Automatically adds calories from each food analysis
- Maintains running totals for the day
- No manual intervention required

### 2. **Data Integrity**
- Uses database constraints to ensure one entry per user per day
- Handles concurrent updates safely
- Includes proper error handling and logging

### 3. **Performance Optimized**
- Aggregated data stored in dedicated table
- Fast queries for daily/weekly/monthly summaries
- Indexed for efficient lookups

### 4. **Comprehensive Reporting**
- Daily summaries for immediate feedback
- Weekly summaries for trend analysis
- Monthly summaries for long-term tracking

### 5. **Backward Compatibility**
- Still logs individual food analyses in `logs` table
- Maintains existing functionality
- Easy migration from old system

## Usage Examples

### Adding Calories from Analysis

```python
from common.calories_manager import add_calories_from_analysis

# After ML service returns analysis
daily_summary = await add_calories_from_analysis(
    user_id=str(user["id"]),
    analysis_data=result,
    photo_url=photo_url
)
```

### Getting Daily Summary

```python
from common.calories_manager import get_daily_calories

daily_data = await get_daily_calories(str(user["id"]))
daily_consumed = daily_data.get("total_calories", 0)
```

### Getting Weekly Summary

```python
from common.calories_manager import get_weekly_calories

weekly_data = await get_weekly_calories(str(user["id"]))
average_calories = weekly_data.get("average_calories", 0)
```

### Getting Monthly Summary

```python
from common.calories_manager import get_monthly_calories

monthly_data = await get_monthly_calories(str(user["id"]), 2025, 8)
total_monthly_calories = monthly_data.get("total_calories", 0)
```

## Benefits

1. **Accurate Tracking**: Ensures calories are properly added to daily totals
2. **Fast Queries**: Aggregated data provides quick access to summaries
3. **Scalable**: Efficient database design handles high user volumes
4. **Reliable**: Proper error handling and data validation
5. **Extensible**: Easy to add new features like meal tracking or goal setting

## Migration

The system automatically migrates from the old logging-based approach:

1. **Old System**: Calculated totals by summing `logs` table entries
2. **New System**: Uses dedicated `daily_calories` table for fast access
3. **Hybrid Approach**: Still logs individual analyses for detailed tracking

## Future Enhancements

1. **Meal Tracking**: Add meal-specific tracking (breakfast, lunch, dinner)
2. **Goal Setting**: Allow users to set daily calorie goals
3. **Trend Analysis**: Provide insights on eating patterns
4. **Export Features**: Allow users to export their nutrition data
5. **Notifications**: Alert users when they exceed daily limits

## Troubleshooting

### Common Issues

1. **Calories not adding**: Check if `analysis_data` contains proper `total_nutrition` structure
2. **Database errors**: Ensure `daily_calories` table exists and has proper permissions
3. **Performance issues**: Verify indexes are created on `user_id` and `date` columns

### Debug Logging

The system includes comprehensive logging:

```python
logger.info(f"Adding calories for user {user_id}: {calories} kcal")
logger.info(f"Updated daily calories for user {user_id}: {new_calories} kcal")
logger.error(f"Error adding calories for user {user_id}: {e}")
```

## Conclusion

The Calories Management System provides a robust, scalable solution for tracking user nutrition data. It ensures accurate calorie counting while maintaining fast access to summary data for reporting and user feedback. 