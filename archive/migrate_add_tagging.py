#!/usr/bin/env python3
"""
Migration script to add tagging functionality to existing database.
This script adds the note_date column to existing notes table and creates the new tags and note_tags tables.
"""

import sys
import os
import psycopg2
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from components.database import DatabaseManager


def migrate_database():
    """Run the migration to add tagging functionality."""
    print("Starting database migration for tagging functionality...")
    
    db_manager = DatabaseManager()
    conn = db_manager.get_connection()
    
    if not conn:
        print("❌ Failed to connect to database")
        return False
    
    try:
        with conn.cursor() as cursor:
            print("📝 Adding note_date column to existing notes table...")
            
            # Check if note_date column already exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='notes' AND column_name='note_date'
            """)
            
            if not cursor.fetchone():
                # Add note_date column to existing notes table
                cursor.execute("""
                    ALTER TABLE notes 
                    ADD COLUMN note_date DATE DEFAULT CURRENT_DATE
                """)
                print("✅ Added note_date column to notes table")
                
                # Update existing notes to use created_at date as note_date
                cursor.execute("""
                    UPDATE notes 
                    SET note_date = DATE(created_at) 
                    WHERE note_date IS NULL
                """)
                print("✅ Updated existing notes with note_date values")
            else:
                print("ℹ️ note_date column already exists")
            
            print("🏷️ Creating tags and note_tags tables...")
            
            # Create tags table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES app_users(id) ON DELETE CASCADE,
                    name VARCHAR(50) NOT NULL,
                    color VARCHAR(7) DEFAULT '#1f77b4',
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, name)
                )
            """)
            print("✅ Created tags table")
            
            # Create note_tags junction table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS note_tags (
                    id SERIAL PRIMARY KEY,
                    note_id INTEGER REFERENCES notes(id) ON DELETE CASCADE,
                    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(note_id, tag_id)
                )
            """)
            print("✅ Created note_tags table")
            
            # Create indexes for better performance
            print("📊 Creating indexes...")
            
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_tags_user_id ON tags(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_note_tags_note_id ON note_tags(note_id)",
                "CREATE INDEX IF NOT EXISTS idx_note_tags_tag_id ON note_tags(tag_id)",
                "CREATE INDEX IF NOT EXISTS idx_notes_note_date ON notes(note_date)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            print("✅ Created all indexes")
            
            # Commit all changes
            conn.commit()
            print("✅ Migration completed successfully!")
            
            # Show summary
            cursor.execute("SELECT COUNT(*) FROM notes")
            note_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tags")
            tag_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM note_tags")
            note_tag_count = cursor.fetchone()[0]
            
            print(f"""
📊 Migration Summary:
   • Notes: {note_count}
   • Tags: {tag_count}
   • Note-Tag associations: {note_tag_count}
   
🎉 Your database is now ready for the tagging feature!
            """)
            
            return True
            
    except psycopg2.Error as e:
        print(f"❌ Database error during migration: {e}")
        conn.rollback()
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def main():
    """Main function to run the migration."""
    print("🚀 Database Migration for Tagging System")
    print("=" * 50)
    
    # Confirm with user
    response = input("This will modify your database structure. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return
    
    success = migrate_database()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("You can now use the tagging features in your application.")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
