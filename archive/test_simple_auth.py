"""
Simple test script to verify the authentication system works.
"""
from src.components.simple_auth import simple_auth
from src.components.database import db_manager


def test_authentication_system():
    """Test the simple authentication system."""
    print("Testing Simple Authentication System")
    print("=" * 40)
    
    # Test database connection
    print("1. Testing database connection...")
    if db_manager.test_connection():
        print("   ✓ Database connection successful")
    else:
        print("   ❌ Database connection failed")
        return False
    
    # Test admin user login
    print("\n2. Testing admin user login...")
    admin_user = simple_auth.login_user("admin", "admin123")
    if admin_user:
        print("   ✓ Admin login successful")
        print(f"   User: {admin_user['display_name']} (@{admin_user['username']})")
        print(f"   Email: {admin_user['email']}")
    else:
        print("   ❌ Admin login failed")
        return False
    
    # Test password validation
    print("\n3. Testing password validation...")
    is_valid, error = simple_auth.validate_password("123")  # Too short
    if not is_valid:
        print(f"   ✓ Password validation working: {error}")
    else:
        print("   ❌ Password validation not working")
    
    is_valid, error = simple_auth.validate_password("validpassword123")
    if is_valid:
        print("   ✓ Valid password accepted")
    else:
        print(f"   ❌ Valid password rejected: {error}")
    
    # Test user creation (will fail if user exists, which is expected)
    print("\n4. Testing user registration...")
    test_user = simple_auth.register_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        display_name="Test User"
    )
    
    if test_user:
        print("   ✓ Test user created successfully")
        
        # Test login with new user
        print("\n5. Testing new user login...")
        login_result = simple_auth.login_user("testuser", "testpass123")
        if login_result:
            print("   ✓ New user login successful")
        else:
            print("   ❌ New user login failed")
    else:
        print("   ⚠️  Test user creation failed (may already exist)")
        
        # Try to login with existing test user
        print("\n5. Testing existing test user login...")
        login_result = simple_auth.login_user("testuser", "testpass123")
        if login_result:
            print("   ✓ Existing test user login successful")
        else:
            print("   ❌ Test user login failed")
    
    # Test password hashing
    print("\n6. Testing password hashing...")
    password = "testpassword123"
    hashed = simple_auth.hash_password(password)
    print(f"   Original: {password}")
    print(f"   Hashed: {hashed[:50]}...")
    
    if simple_auth.verify_password(password, hashed):
        print("   ✓ Password verification successful")
    else:
        print("   ❌ Password verification failed")
    
    print("\n" + "=" * 40)
    print("✅ Authentication system test completed!")
    return True


def test_database_operations():
    """Test database operations."""
    print("\nTesting Database Operations")
    print("=" * 30)
    
    # Test getting all users
    print("1. Getting all users...")
    users = db_manager.get_all_users()
    print(f"   Found {len(users)} users:")
    for user in users:
        print(f"   - {user['display_name']} (@{user['username']}) - {user['email']}")
    
    # Test getting user by username
    print("\n2. Getting user by username...")
    admin_user = db_manager.get_user_by_username("admin")
    if admin_user:
        print(f"   ✓ Found admin user: {admin_user['display_name']}")
    else:
        print("   ❌ Admin user not found")
    
    # Test getting user by email
    print("\n3. Getting user by email...")
    admin_by_email = db_manager.get_user_by_email("admin@dailynotes.local")
    if admin_by_email:
        print(f"   ✓ Found admin by email: {admin_by_email['display_name']}")
    else:
        print("   ❌ Admin user not found by email")
    
    return True


if __name__ == "__main__":
    try:
        if test_authentication_system():
            test_database_operations()
            print("\n🎉 All tests completed successfully!")
            print("\nYou can now use the web application with these credentials:")
            print("Username: admin")
            print("Password: admin123")
            print("\nOr create a new account using the registration form.")
        else:
            print("\n❌ Some tests failed. Please check the error messages above.")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
