#!/usr/bin/env python3
"""
Quick Migration Test Script
Tests the enhanced nutrition system migration on the actual database
"""

import os
import sys
import asyncio
from datetime import datetime

import asyncpg
from loguru import logger

# Database configuration
DATABASE_URL = "postgresql://postgres.cadeererdjwemspkeriq:xuoO4|LSaaGX5@aws-0-eu-north-1.pooler.supabase.com:6543/postgres"

async def test_migration():
    """Test the migration by running quick checks"""

    logger.info("🧪 Testing Enhanced Nutrition System Migration")

    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("✅ Connected to database")

        # Test 1: Check if new tables exist
        logger.info("📋 Testing table creation...")

        tables_to_check = [
            'nutrition_questionnaire_responses',
            'nutrition_dna',
            'meal_recommendations',
            'user_food_analysis_enhanced'
        ]

        for table in tables_to_check:
            result = await conn.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                table
            )
            if result:
                logger.info(f"✅ Table {table} exists")
            else:
                logger.error(f"❌ Table {table} missing")
                return False

        # Test 2: Check user_profiles enhancements
        logger.info("👤 Testing user_profiles enhancements...")

        required_columns = [
            'onboarding_completed',
            'favorite_foods',
            'preferred_cuisines',
            'cooking_skill',
            'social_eating_frequency'
        ]

        existing_columns = await conn.fetch(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'user_profiles'"
        )
        existing_column_names = [col['column_name'] for col in existing_columns]

        for column in required_columns:
            if column in existing_column_names:
                logger.info(f"✅ Column user_profiles.{column} exists")
            else:
                logger.error(f"❌ Column user_profiles.{column} missing")
                return False

        # Test 3: Check meal_plans enhancements
        logger.info("🍽️  Testing meal_plans enhancements...")

        meal_plan_columns = await conn.fetch(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'meal_plans'"
        )
        meal_plan_column_names = [col['column_name'] for col in meal_plan_columns]

        if 'nutrition_dna_id' in meal_plan_column_names:
            logger.info("✅ Column meal_plans.nutrition_dna_id exists")
        else:
            logger.error("❌ Column meal_plans.nutrition_dna_id missing")
            return False

        # Test 4: Check views
        logger.info("👁️  Testing views creation...")

        views_to_check = [
            'complete_nutrition_profiles',
            'recent_meal_recommendations'
        ]

        for view in views_to_check:
            result = await conn.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.views WHERE table_name = $1)",
                view
            )
            if result:
                logger.info(f"✅ View {view} exists")
            else:
                logger.error(f"❌ View {view} missing")
                return False

        # Test 5: Check indexes
        logger.info("📊 Testing indexes...")

        indexes = await conn.fetch(
            "SELECT indexname, tablename FROM pg_indexes WHERE tablename IN ('nutrition_dna', 'user_profiles', 'meal_plans')"
        )

        important_indexes = [
            'idx_nutrition_dna_user_id',
            'idx_user_profiles_onboarding_completed'
        ]

        existing_indexes = [idx['indexname'] for idx in indexes]

        for index in important_indexes:
            if index in existing_indexes:
                logger.info(f"✅ Index {index} exists")
            else:
                logger.warning(f"⚠️  Index {index} may be missing (check manually)")

        # Test 6: Insert sample data to verify constraints
        logger.info("🧪 Testing data insertion...")

        # Test nutrition_dna insertion
        try:
            # First, get a user ID to test with
            user_result = await conn.fetchrow("SELECT id FROM users LIMIT 1")
            if not user_result:
                logger.warning("⚠️  No users found - skipping data insertion test")
            else:
                test_user_id = user_result['id']

                # Try to insert a test nutrition DNA record
                await conn.execute("""
                    INSERT INTO nutrition_dna
                    (user_id, archetype, confidence_score, morning_appetite)
                    VALUES ($1, 'EARLY_BIRD_PLANNER', 0.85, 0.7)
                    ON CONFLICT (user_id) DO UPDATE SET
                        confidence_score = EXCLUDED.confidence_score,
                        last_updated = NOW()
                """, test_user_id)

                logger.info("✅ Sample nutrition_dna record inserted/updated")

                # Try to insert a questionnaire response
                await conn.execute("""
                    INSERT INTO nutrition_questionnaire_responses
                    (user_id, question_id, response_value, response_timestamp)
                    VALUES ($1, 'test_question', 'test_response', NOW())
                    ON CONFLICT (user_id, question_id) DO UPDATE SET
                        response_value = EXCLUDED.response_value,
                        updated_at = NOW()
                """, test_user_id)

                logger.info("✅ Sample questionnaire response inserted/updated")

        except Exception as e:
            logger.error(f"❌ Data insertion test failed: {e}")
            return False

        # Test 7: Test view queries
        logger.info("🔍 Testing view queries...")

        try:
            # Test complete nutrition profiles view
            profile_count = await conn.fetchval(
                "SELECT COUNT(*) FROM complete_nutrition_profiles"
            )
            logger.info(f"✅ complete_nutrition_profiles view returned {profile_count} records")

            # Test recent meal recommendations view
            rec_count = await conn.fetchval(
                "SELECT COUNT(*) FROM recent_meal_recommendations"
            )
            logger.info(f"✅ recent_meal_recommendations view returned {rec_count} records")

        except Exception as e:
            logger.error(f"❌ View query test failed: {e}")
            return False

        await conn.close()
        logger.info("📡 Disconnected from database")

        logger.success("🎉 All migration tests passed!")
        logger.info("✨ Enhanced Nutrition System database is ready!")

        return True

    except Exception as e:
        logger.error(f"💥 Migration test failed: {e}")
        return False

async def main():
    """Main entry point"""

    # Configure logger
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        level="INFO"
    )

    logger.info("🚀 Starting Enhanced Nutrition System Migration Test")
    logger.info(f"🗄️  Database: {DATABASE_URL.split('@')[1].split('/')[0]}...")  # Hide credentials
    logger.info(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    success = await test_migration()

    print("")
    print("=" * 50)

    if success:
        logger.success("✅ MIGRATION TEST: SUCCESS")
        print("")
        print("🎯 Next Steps:")
        print("1. Run the full migration: python scripts/run_migrations.py --database-url $DATABASE_URL")
        print("2. Deploy application with enhanced features enabled")
        print("3. Test user flows via Telegram bot")
        print("4. Monitor enhanced nutrition metrics")
        print("")
        print("📚 Documentation: docs/enhanced-nutrition-features.md")
        sys.exit(0)
    else:
        logger.error("❌ MIGRATION TEST: FAILED")
        print("")
        print("🔧 Troubleshooting:")
        print("1. Check database connectivity")
        print("2. Verify migration files are present")
        print("3. Review error messages above")
        print("4. Check database permissions")
        print("")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())