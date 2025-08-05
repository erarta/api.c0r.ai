"""
Calories Service Module
Handles all calorie tracking operations with proper error handling and database management
"""

import logging
from datetime import date, datetime
from typing import Dict, Optional, Tuple
from decimal import Decimal

from .db.client import get_supabase_client
from .models import User

logger = logging.getLogger(__name__)


class CaloriesService:
    """Service for managing user calorie tracking"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    def ensure_daily_calories_table(self) -> bool:
        """Ensure daily_calories table exists, create if not"""
        try:
            # Check if table exists
            result = self.supabase.table("daily_calories").select("id").limit(1).execute()
            logger.info("✅ daily_calories table exists")
            return True
        except Exception as e:
            logger.warning(f"daily_calories table doesn't exist, creating it: {e}")
            return self._create_daily_calories_table()
    
    def _create_daily_calories_table(self) -> bool:
        """Create daily_calories table"""
        try:
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS daily_calories (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                user_id UUID NOT NULL,
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
            
            -- Create index for faster queries
            CREATE INDEX IF NOT EXISTS idx_daily_calories_user_date ON daily_calories(user_id, date);
            CREATE INDEX IF NOT EXISTS idx_daily_calories_date ON daily_calories(date);
            """
            
            # Execute raw SQL
            self.supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
            logger.info("✅ daily_calories table created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create daily_calories table: {e}")
            return False
    
    def add_calories_from_analysis(self, user_id: str, calories: float, 
                                  proteins: float = 0, fats: float = 0, 
                                  carbohydrates: float = 0) -> bool:
        """Add calories from nutrition analysis to user's daily total"""
        try:
            # Ensure table exists
            if not self.ensure_daily_calories_table():
                logger.error("❌ Cannot add calories - table creation failed")
                return False
            
            today = date.today()
            
            # Try to get existing record for today
            result = self.supabase.table("daily_calories").select("*").eq("user_id", user_id).eq("date", today.isoformat()).execute()
            
            if result.data:
                # Update existing record
                record = result.data[0]
                new_calories = float(record['total_calories']) + calories
                new_proteins = float(record['total_proteins']) + proteins
                new_fats = float(record['total_fats']) + fats
                new_carbohydrates = float(record['total_carbohydrates']) + carbohydrates
                
                update_result = self.supabase.table("daily_calories").update({
                    'total_calories': new_calories,
                    'total_proteins': new_proteins,
                    'total_fats': new_fats,
                    'total_carbohydrates': new_carbohydrates,
                    'updated_at': datetime.now().isoformat()
                }).eq("id", record['id']).execute()
                
                logger.info(f"✅ Updated calories for user {user_id}: +{calories} kcal (total: {new_calories})")
                return True
            else:
                # Create new record for today
                insert_result = self.supabase.table("daily_calories").insert({
                    'user_id': user_id,
                    'date': today.isoformat(),
                    'total_calories': calories,
                    'total_proteins': proteins,
                    'total_fats': fats,
                    'total_carbohydrates': carbohydrates
                }).execute()
                
                logger.info(f"✅ Created new daily record for user {user_id}: {calories} kcal")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error adding calories for user {user_id}: {e}")
            return False
    
    def get_daily_summary(self, user_id: str) -> Optional[Dict]:
        """Get user's daily calorie summary"""
        try:
            # Ensure table exists
            if not self.ensure_daily_calories_table():
                logger.error("❌ Cannot get daily summary - table creation failed")
                return None
            
            today = date.today()
            
            result = self.supabase.table("daily_calories").select("*").eq("user_id", user_id).eq("date", today.isoformat()).execute()
            
            if result.data:
                record = result.data[0]
                return {
                    'total_calories': float(record['total_calories']),
                    'total_proteins': float(record['total_proteins']),
                    'total_fats': float(record['total_fats']),
                    'total_carbohydrates': float(record['total_carbohydrates'])
                }
            else:
                # Return zero values if no record exists
                return {
                    'total_calories': 0.0,
                    'total_proteins': 0.0,
                    'total_fats': 0.0,
                    'total_carbohydrates': 0.0
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting daily summary for user {user_id}: {e}")
            return None
    
    def get_user_target_calories(self, user_id: str) -> Optional[int]:
        """Get user's daily calorie target from profile"""
        try:
            result = self.supabase.table("user_profiles").select("daily_calories_target").eq("user_id", user_id).execute()
            
            if result.data and result.data[0]['daily_calories_target']:
                return int(result.data[0]['daily_calories_target'])
            else:
                # Default target if not set
                return 2000
                
        except Exception as e:
            logger.error(f"❌ Error getting target calories for user {user_id}: {e}")
            return 2000  # Default fallback
    
    def calculate_daily_progress(self, user_id: str) -> Dict:
        """Calculate user's daily calorie progress"""
        try:
            daily_summary = self.get_daily_summary(user_id)
            target_calories = self.get_user_target_calories(user_id)
            
            if daily_summary is None or target_calories is None:
                return {
                    'eaten_calories': 0,
                    'target_calories': target_calories or 2000,
                    'remaining_calories': target_calories or 2000,
                    'progress_percentage': 0
                }
            
            eaten_calories = daily_summary['total_calories']
            remaining_calories = max(0, target_calories - eaten_calories)
            progress_percentage = min(100, (eaten_calories / target_calories) * 100) if target_calories > 0 else 0
            
            return {
                'eaten_calories': eaten_calories,
                'target_calories': target_calories,
                'remaining_calories': remaining_calories,
                'progress_percentage': progress_percentage
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating daily progress for user {user_id}: {e}")
            return {
                'eaten_calories': 0,
                'target_calories': 2000,
                'remaining_calories': 2000,
                'progress_percentage': 0
            }


# Global instance
calories_service = CaloriesService() 