"""
Database initialization script for the Daily Notes application.
Run this script to create tables and populate sample data.

This script now uses the centralized secrets management system.
Make sure your .streamlit/secrets.toml file is properly configured.
"""
from src.components.database import db_manager

def initialize_database():
    """Initialize the database with tables and sample data."""
    print("Initializing database...")
    
    # Create tables
    print("Creating tables...")
    if db_manager.create_tables():
        print("✓ Tables created successfully")
    else:
        print("✗ Failed to create tables")
        return False
    
    # Insert sample users
    print("Inserting sample users...")
    try:
        if db_manager.insert_sample_users():
            print("✓ Sample users inserted successfully")
        else:
            print("✗ Failed to insert sample users")
            return False
    except Exception as e:
        print(f"✗ Error inserting sample users: {e}")
        return False
    
    print("Database initialization completed successfully!")
    return True

if __name__ == "__main__":
    initialize_database()
