"""Debug authentication to see what's happening."""

from backend.auth import authenticate_user, register_user

# Test registration
print("Testing registration...")
success, user, message = register_user(
    email="shubham.8130@outlook.com",
    password="test123",
    full_name="Test User"
)
print(f"Register result: success={success}, message={message}")

if success:
    print(f"User created: {user.email}")
    
# Test authentication
print("\nTesting authentication...")
success, user, message = authenticate_user(
    email="shubham.8130@outlook.com",
    password="test123"
)
print(f"Auth result: success={success}, message={message}")

if success:
    print(f"Authenticated as: {user.email}")
else:
    print(f"Auth failed: {message}")

