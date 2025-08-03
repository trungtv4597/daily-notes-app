"""
Database migration script to convert from Firebase auth to simple authentication.
This script will update the existing app_users table structure.
"""
from src.components.database import db_manager
import psycopg2


def migrate_to_simple_auth():
    """Migrate the database to support simple authentication."""
    print("Starting database migration to simple authentication...")
    
    conn = db_manager.get_connection()
    if not conn:
        print("❌ Failed to connect to database")
        return False
    
    try:
        with conn.cursor() as cursor:
            # Check current table structure
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'app_users'
                ORDER BY ordinal_position
            """)
            
            existing_columns = [row[0] for row in cursor.fetchall()]
            print(f"Current columns: {existing_columns}")
            
            # Drop the table and recreate it with new structure
            print("Dropping existing app_users table...")
            cursor.execute("DROP TABLE IF EXISTS notes CASCADE")
            cursor.execute("DROP TABLE IF EXISTS app_users CASCADE")
            
            print("Creating new table structure...")
            
            # Create new app_users table
            cursor.execute("""
                CREATE TABLE app_users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    display_name VARCHAR(100) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP WITHOUT TIME ZONE
                )
            """)
            
            # Create notes table
            cursor.execute("""
                CREATE TABLE notes (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES app_users(id) ON DELETE CASCADE,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX idx_app_users_username ON app_users(username)")
            cursor.execute("CREATE INDEX idx_app_users_email ON app_users(email)")
            
            conn.commit()
            print("✓ Database migration completed successfully!")
            return True
            
    except psycopg2.Error as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def create_admin_user():
    """Create a default admin user for testing."""
    print("\nCreating default admin user...")
    
    try:
        from src.components.simple_auth import simple_auth
        
        # Create admin user
        admin_user = simple_auth.register_user(
            username="admin",
            email="admin@dailynotes.local",
            password="admin123",
            display_name="Administrator"
        )
        
        if admin_user:
            print("✓ Admin user created successfully!")
            print("  Username: admin")
            print("  Password: admin123")
            print("  Email: admin@dailynotes.local")
            return True
        else:
            print("❌ Failed to create admin user")
            return False
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False


def verify_migration():
    """Verify that the migration was successful."""
    print("\nVerifying migration...")
    
    conn = db_manager.get_connection()
    if not conn:
        print("❌ Failed to connect to database for verification")
        return False
    
    try:
        with conn.cursor() as cursor:
            # Check table structure
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'app_users'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print("New app_users table structure:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
            # Check if we have the required columns
            required_columns = ['username', 'email', 'password_hash', 'display_name']
            existing_columns = [col[0] for col in columns]
            
            missing_columns = [col for col in required_columns if col not in existing_columns]
            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
                return False
            
            # Check if admin user exists
            cursor.execute("SELECT COUNT(*) FROM app_users WHERE username = 'admin'")
            admin_count = cursor.fetchone()[0]
            
            if admin_count > 0:
                print("✓ Admin user found in database")
            else:
                print("⚠️  No admin user found")
            
            print("✓ Migration verification completed")
            return True
            
    except psycopg2.Error as e:
        print(f"❌ Verification failed: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    print("Simple Authentication Database Migration")
    print("=" * 50)
    
    # Test database connection first
    if not db_manager.test_connection():
        print("❌ Cannot connect to database. Please check your configuration.")
        exit(1)
    
    # Run migration
    if migrate_to_simple_auth():
        if create_admin_user():
            if verify_migration():
                print("\n🎉 Migration completed successfully!")
                print("Your database is now ready for simple authentication.")
                print("\nYou can login with:")
                print("  Username: admin")
                print("  Password: admin123")
            else:
                print("\n⚠️  Migration completed but verification had issues.")
        else:
            print("\n⚠️  Migration completed but admin user creation failed.")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        exit(1)
