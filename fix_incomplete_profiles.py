#!/usr/bin/env python3
"""
Script to fix existing incomplete profiles in the database
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project paths
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'common'))

load_dotenv()

from common.supabase_client import supabase

async def fix_incomplete_profiles():
    """Fix existing incomplete profiles by setting them to NULL or removing them"""
    print("🔧 Fixing incomplete profiles in database...")
    print("=" * 50)
    
    try:
        # Get all profiles
        profiles = supabase.table("user_profiles").select("*").execute()
        
        print(f"Found {len(profiles.data)} total profiles")
        
        incomplete_count = 0
        fixed_count = 0
        
        for profile in profiles.data:
            # Check if profile is incomplete (missing required fields)
            required_fields = ['age', 'gender', 'height_cm', 'weight_kg', 'activity_level', 'goal']
            missing_fields = []
            
            for field in required_fields:
                if field not in profile or profile[field] is None:
                    missing_fields.append(field)
            
            if missing_fields:
                incomplete_count += 1
                print(f"❌ Incomplete profile {profile['id']}: missing {missing_fields}")
                
                # Option 1: Delete incomplete profiles (recommended)
                # This forces users to complete the setup properly
                try:
                    supabase.table("user_profiles").delete().eq("id", profile['id']).execute()
                    print(f"   ✅ Deleted incomplete profile {profile['id']}")
                    fixed_count += 1
                except Exception as e:
                    print(f"   ❌ Error deleting profile {profile['id']}: {e}")
                
                # Option 2: Set missing fields to NULL (alternative approach)
                # This keeps the profile but marks it as incomplete
                # update_data = {}
                # for field in missing_fields:
                #     update_data[field] = None
                # 
                # try:
                #     supabase.table("user_profiles").update(update_data).eq("id", profile['id']).execute()
                #     print(f"   ✅ Updated incomplete profile {profile['id']}")
                #     fixed_count += 1
                # except Exception as e:
                #     print(f"   ❌ Error updating profile {profile['id']}: {e}")
        
        print(f"\n📊 Summary:")
        print(f"   Total profiles: {len(profiles.data)}")
        print(f"   Incomplete profiles found: {incomplete_count}")
        print(f"   Fixed profiles: {fixed_count}")
        
        if incomplete_count == 0:
            print("🎉 All profiles are complete!")
        else:
            print(f"✅ Fixed {fixed_count} incomplete profiles")
            
    except Exception as e:
        print(f"❌ Error fixing profiles: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting incomplete profile fix...")
    asyncio.run(fix_incomplete_profiles())
    print("✅ Fix completed") 