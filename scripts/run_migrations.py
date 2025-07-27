#!/usr/bin/env python3
"""
Database Migration Runner for c0r.ai
Automatically runs pending migrations and tracks them in schema_migrations table
"""

import os
import sys
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from loguru import logger

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class MigrationRunner:
    def __init__(self, database_url: str):
        """Initialize migration runner with database connection"""
        self.database_url = database_url
        self.migrations_dir = project_root / "migrations" / "database"
        self.rollbacks_dir = project_root / "migrations" / "rollbacks"
        
    def connect_db(self):
        """Create database connection"""
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def get_file_checksum(self, filepath: Path) -> str:
        """Calculate SHA256 checksum of file"""
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def ensure_migrations_table(self):
        """Ensure schema_migrations table exists"""
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        id SERIAL PRIMARY KEY,
                        filename VARCHAR(255) UNIQUE NOT NULL,
                        applied_at TIMESTAMP DEFAULT NOW(),
                        rollback_filename VARCHAR(255),
                        checksum VARCHAR(64),
                        status VARCHAR(20) DEFAULT 'applied',
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_schema_migrations_filename 
                    ON schema_migrations(filename);
                """)
                conn.commit()
                logger.info("✅ Schema migrations table ready")
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of already applied migrations"""
        with self.connect_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT filename FROM schema_migrations WHERE status = 'applied'"
                )
                return [row['filename'] for row in cur.fetchall()]
    
    def get_pending_migrations(self) -> List[Path]:
        """Get list of pending migration files"""
        if not self.migrations_dir.exists():
            logger.warning(f"Migrations directory not found: {self.migrations_dir}")
            return []
        
        applied = set(self.get_applied_migrations())
        all_migrations = sorted(self.migrations_dir.glob("*.sql"))
        
        pending = [m for m in all_migrations if m.name not in applied]
        logger.info(f"Found {len(pending)} pending migrations")
        return pending
    
    def run_migration(self, migration_file: Path) -> bool:
        """Run a single migration file"""
        try:
            logger.info(f"🔄 Running migration: {migration_file.name}")
            
            # Read migration content
            with open(migration_file, 'r', encoding='utf-8') as f:
                migration_sql = f.read()
            
            # Calculate checksum
            checksum = self.get_file_checksum(migration_file)
            
            # Find corresponding rollback file
            rollback_filename = migration_file.name.replace('.sql', '_rollback.sql')
            rollback_path = self.rollbacks_dir / rollback_filename
            
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    # Execute migration
                    cur.execute(migration_sql)
                    
                    # Record migration in schema_migrations
                    cur.execute("""
                        INSERT INTO schema_migrations 
                        (filename, rollback_filename, checksum, status)
                        VALUES (%s, %s, %s, 'applied')
                        ON CONFLICT (filename) DO UPDATE SET
                            applied_at = NOW(),
                            checksum = EXCLUDED.checksum,
                            status = 'applied',
                            updated_at = NOW()
                    """, (
                        migration_file.name,
                        rollback_filename if rollback_path.exists() else None,
                        checksum
                    ))
                    
                    conn.commit()
                    logger.success(f"✅ Migration completed: {migration_file.name}")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Migration failed: {migration_file.name} - {e}")
            
            # Record failure in database
            try:
                with self.connect_db() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO schema_migrations 
                            (filename, checksum, status)
                            VALUES (%s, %s, 'failed')
                            ON CONFLICT (filename) DO UPDATE SET
                                status = 'failed',
                                updated_at = NOW()
                        """, (migration_file.name, self.get_file_checksum(migration_file)))
                        conn.commit()
            except Exception as db_error:
                logger.error(f"Failed to record migration failure: {db_error}")
            
            return False
    
    def run_all_pending(self) -> Dict[str, int]:
        """Run all pending migrations"""
        logger.info("🚀 Starting migration runner...")
        
        # Ensure migrations table exists
        self.ensure_migrations_table()
        
        # Get pending migrations
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("✅ No pending migrations found")
            return {"total": 0, "success": 0, "failed": 0}
        
        results = {"total": len(pending), "success": 0, "failed": 0}
        
        for migration in pending:
            if self.run_migration(migration):
                results["success"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"📊 Migration summary: {results['success']}/{results['total']} successful")
        return results
    
    def rollback_migration(self, migration_name: str) -> bool:
        """Rollback a specific migration"""
        try:
            # Find rollback file
            rollback_filename = migration_name.replace('.sql', '_rollback.sql')
            rollback_path = self.rollbacks_dir / rollback_filename
            
            if not rollback_path.exists():
                logger.error(f"❌ Rollback file not found: {rollback_filename}")
                return False
            
            logger.info(f"🔄 Rolling back migration: {migration_name}")
            
            # Read rollback content
            with open(rollback_path, 'r', encoding='utf-8') as f:
                rollback_sql = f.read()
            
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    # Execute rollback
                    cur.execute(rollback_sql)
                    
                    # Update migration status
                    cur.execute("""
                        UPDATE schema_migrations 
                        SET status = 'rolled_back', updated_at = NOW()
                        WHERE filename = %s
                    """, (migration_name,))
                    
                    conn.commit()
                    logger.success(f"✅ Rollback completed: {migration_name}")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Rollback failed: {migration_name} - {e}")
            return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Migration Runner")
    parser.add_argument("--database-url", required=True, help="PostgreSQL database URL")
    parser.add_argument("--rollback", help="Rollback specific migration")
    parser.add_argument("--dry-run", action="store_true", help="Show pending migrations without running")
    
    args = parser.parse_args()
    
    runner = MigrationRunner(args.database_url)
    
    if args.rollback:
        success = runner.rollback_migration(args.rollback)
        sys.exit(0 if success else 1)
    
    if args.dry_run:
        pending = runner.get_pending_migrations()
        if pending:
            logger.info("Pending migrations:")
            for migration in pending:
                logger.info(f"  - {migration.name}")
        else:
            logger.info("No pending migrations")
        return
    
    results = runner.run_all_pending()
    
    # Exit with error code if any migrations failed
    sys.exit(0 if results["failed"] == 0 else 1)

if __name__ == "__main__":
    main()