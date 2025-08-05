"""
Calories Management System

This module provides comprehensive calorie tracking functionality including:
- Adding calories from food analysis
- Getting daily, weekly, and monthly calorie consumption
- Generating reports for users
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from loguru import logger
from common.db.client import get_client


class CaloriesManager:
    """Manages calorie tracking and reporting for users"""
    
    def __init__(self):
        self.supabase = get_client()
    
    def ensure_daily_calories_table(self) -> bool:
        """Ensure daily_calories table exists"""
        try:
            # Check if table exists by trying to query it
            result = self.supabase.table("daily_calories").select("id").limit(1).execute()
            logger.info("✅ daily_calories table exists and is accessible")
            return True
        except Exception as e:
            logger.error(f"❌ daily_calories table not accessible: {e}")
            return False
    
    def add_calories_from_analysis(
        self,
        user_id: str, 
        analysis_data: Dict, 
        photo_url: str = None
    ) -> bool:
        """
        Add calories from food analysis to user's daily consumption
        
        Args:
            user_id: User UUID
            analysis_data: Analysis result from ML service
            photo_url: URL of the analyzed photo
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure table exists
            if not self.ensure_daily_calories_table():
                logger.error("❌ Cannot add calories - table creation failed")
                return False
            
            # Extract nutrition data from analysis
            if "analysis" not in analysis_data or "total_nutrition" not in analysis_data["analysis"]:
                logger.error(f"Invalid analysis data format for user {user_id}")
                return False
                
            nutrition = analysis_data["analysis"]["total_nutrition"]
            calories = float(nutrition.get("calories", 0))
            proteins = float(nutrition.get("proteins", 0))
            fats = float(nutrition.get("fats", 0))
            carbohydrates = float(nutrition.get("carbohydrates", 0))
            
            logger.info(f"Adding calories for user {user_id}: {calories} kcal")
            
            # Get current date
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # Check if entry exists for today
            existing_entry = self.supabase.table("daily_calories").select("*").eq(
                "user_id", user_id
            ).eq("date", current_date).execute()
            
            if existing_entry.data:
                # Update existing entry
                entry = existing_entry.data[0]
                new_calories = float(entry["total_calories"]) + calories
                new_proteins = float(entry["total_proteins"]) + proteins
                new_fats = float(entry["total_fats"]) + fats
                new_carbohydrates = float(entry["total_carbohydrates"]) + carbohydrates
                
                updated_entry = self.supabase.table("daily_calories").update({
                    "total_calories": new_calories,
                    "total_proteins": new_proteins,
                    "total_fats": new_fats,
                    "total_carbohydrates": new_carbohydrates,
                    "updated_at": datetime.now().isoformat()
                }).eq("id", entry["id"]).execute()
                
                logger.info(f"✅ Updated daily calories for user {user_id}: {new_calories} kcal")
                
            else:
                # Create new entry
                new_entry = self.supabase.table("daily_calories").insert({
                    "user_id": user_id,
                    "date": current_date,
                    "total_calories": calories,
                    "total_proteins": proteins,
                    "total_fats": fats,
                    "total_carbohydrates": carbohydrates,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }).execute()
                
                logger.info(f"✅ Created new daily calories entry for user {user_id}: {calories} kcal")
            
            # Also log the individual food analysis
            # Note: _log_food_analysis is async but we're calling it from sync context
            # This is a temporary fix - in production we should make this properly async
            try:
                import asyncio
                asyncio.create_task(self._log_food_analysis(
                    user_id=user_id,
                    calories=calories,
                    proteins=proteins,
                    fats=fats,
                    carbohydrates=carbohydrates,
                    photo_url=photo_url,
                    analysis_data=analysis_data
                ))
            except Exception as e:
                logger.warning(f"Could not log food analysis: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding calories for user {user_id}: {e}")
            return False
    
    async def _log_food_analysis(
        self,
        user_id: str,
        calories: float,
        proteins: float,
        fats: float,
        carbohydrates: float,
        photo_url: str = None,
        analysis_data: Dict = None
    ):
        """Log individual food analysis for tracking"""
        try:
            log_data = {
                "user_id": user_id,
                "action_type": "photo_analysis",
                "timestamp": datetime.now().isoformat(),
                "kbzhu": {
                    "calories": calories,
                    "proteins": proteins,
                    "fats": fats,
                    "carbohydrates": carbohydrates
                },
                "photo_url": photo_url,
                "metadata": analysis_data
            }
            
            self.supabase.table("logs").insert(log_data).execute()
            logger.info(f"✅ Logged food analysis for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error logging food analysis for user {user_id}: {e}")
    
    def get_daily_summary(self, user_id: str, date: str = None) -> Dict:
        """
        Get daily calorie summary for user
        
        Args:
            user_id: User UUID
            date: Date in YYYY-MM-DD format (default: today)
            
        Returns:
            Dict with daily summary
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
            
        try:
            # Ensure table exists
            if not self.ensure_daily_calories_table():
                logger.error("❌ Cannot get daily summary - table not accessible")
                return {
                    'date': date,
                    'total_calories': 0,
                    'total_proteins': 0,
                    'total_fats': 0,
                    'total_carbohydrates': 0,
                    'food_items_count': 0,
                    'food_items': []
                }
            
            # Get daily calories entry
            entry = self.supabase.table("daily_calories").select("*").eq(
                "user_id", user_id
            ).eq("date", date).execute()
            
            if entry.data:
                data = entry.data[0]
                return {
                    'date': date,
                    'total_calories': round(float(data['total_calories']), 1),
                    'total_proteins': round(float(data['total_proteins']), 1),
                    'total_fats': round(float(data['total_fats']), 1),
                    'total_carbohydrates': round(float(data['total_carbohydrates']), 1),
                    'food_items_count': 1,  # Will be updated when we add food items tracking
                    'food_items': []
                }
            else:
                return {
                    'date': date,
                    'total_calories': 0,
                    'total_proteins': 0,
                    'total_fats': 0,
                    'total_carbohydrates': 0,
                    'food_items_count': 0,
                    'food_items': []
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting daily summary for user {user_id}: {e}")
            return {
                'date': date,
                'total_calories': 0,
                'total_proteins': 0,
                'total_fats': 0,
                'total_carbohydrates': 0,
                'food_items_count': 0,
                'food_items': []
            }
    
    @staticmethod
    async def get_weekly_summary(user_id: str, end_date: str = None) -> Dict:
        """
        Get weekly calorie summary for user
        
        Args:
            user_id: User UUID
            end_date: End date in YYYY-MM-DD format (default: today)
            
        Returns:
            Dict with weekly summary
        """
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        start_dt = end_dt - timedelta(days=6)
        start_date = start_dt.strftime('%Y-%m-%d')
        
        try:
            entries = supabase.table("daily_calories").select("*").eq(
                "user_id", user_id
            ).gte("date", start_date).lte("date", end_date).execute()
            
            total_calories = 0
            total_proteins = 0
            total_fats = 0
            total_carbs = 0
            days_with_data = 0
            
            for entry in entries.data:
                total_calories += entry['total_calories']
                total_proteins += entry['total_proteins']
                total_fats += entry['total_fats']
                total_carbs += entry['total_carbohydrates']
                days_with_data += 1
            
            avg_calories = total_calories / 7 if days_with_data > 0 else 0
            
            return {
                'start_date': start_date,
                'end_date': end_date,
                'total_calories': round(total_calories, 1),
                'average_calories': round(avg_calories, 1),
                'total_proteins': round(total_proteins, 1),
                'total_fats': round(total_fats, 1),
                'total_carbohydrates': round(total_carbs, 1),
                'days_with_data': days_with_data,
                'days_count': 7
            }
            
        except Exception as e:
            logger.error(f"Error getting weekly summary for user {user_id}: {e}")
            return {
                'start_date': start_date,
                'end_date': end_date,
                'total_calories': 0,
                'average_calories': 0,
                'total_proteins': 0,
                'total_fats': 0,
                'total_carbohydrates': 0,
                'days_with_data': 0,
                'days_count': 7
            }
    
    @staticmethod
    async def get_monthly_summary(user_id: str, year: int = None, month: int = None) -> Dict:
        """
        Get monthly calorie summary for user
        
        Args:
            user_id: User UUID
            year: Year (default: current year)
            month: Month (1-12, default: current month)
            
        Returns:
            Dict with monthly summary
        """
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
            
        start_date = f"{year:04d}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1:04d}-01-01"
        else:
            end_date = f"{year:04d}-{month + 1:02d}-01"
            
        try:
            entries = supabase.table("daily_calories").select("*").eq(
                "user_id", user_id
            ).gte("date", start_date).lt("date", end_date).execute()
            
            total_calories = 0
            total_proteins = 0
            total_fats = 0
            total_carbs = 0
            days_with_data = 0
            
            for entry in entries.data:
                total_calories += entry['total_calories']
                total_proteins += entry['total_proteins']
                total_fats += entry['total_fats']
                total_carbs += entry['total_carbohydrates']
                days_with_data += 1
            
            # Calculate days in month
            if month == 12:
                next_month = datetime(year + 1, 1, 1)
            else:
                next_month = datetime(year, month + 1, 1)
            days_in_month = (next_month - datetime(year, month, 1)).days
            
            avg_calories = total_calories / days_in_month if days_with_data > 0 else 0
            
            return {
                'year': year,
                'month': month,
                'total_calories': round(total_calories, 1),
                'average_calories': round(avg_calories, 1),
                'total_proteins': round(total_proteins, 1),
                'total_fats': round(total_fats, 1),
                'total_carbohydrates': round(total_carbs, 1),
                'days_with_data': days_with_data,
                'days_in_month': days_in_month
            }
            
        except Exception as e:
            logger.error(f"Error getting monthly summary for user {user_id}: {e}")
            return {
                'year': year,
                'month': month,
                'total_calories': 0,
                'average_calories': 0,
                'total_proteins': 0,
                'total_fats': 0,
                'total_carbohydrates': 0,
                'days_with_data': 0,
                'days_in_month': days_in_month
            }


# Global instance
calories_manager = CaloriesManager()

# Convenience functions for easy access
def add_calories_from_analysis(user_id: str, analysis_data: Dict, photo_url: str = None) -> bool:
    """Add calories from food analysis"""
    return calories_manager.add_calories_from_analysis(user_id, analysis_data, photo_url)


def get_daily_calories(user_id: str, date: str = None) -> Dict:
    """Get daily calorie summary"""
    return calories_manager.get_daily_summary(user_id, date)


async def get_weekly_calories(user_id: str, end_date: str = None) -> Dict:
    """Get weekly calorie summary"""
    return await CaloriesManager.get_weekly_summary(user_id, end_date)


async def get_monthly_calories(user_id: str, year: int = None, month: int = None) -> Dict:
    """Get monthly calorie summary"""
    return await CaloriesManager.get_monthly_summary(user_id, year, month) 