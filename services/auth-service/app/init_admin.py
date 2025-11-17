"""
Initialize default admin user from environment variables.
This script runs on startup to ensure a default admin user exists.
"""
import os
from sqlalchemy import select
from app.db import User, async_session_maker
from fastapi_users.password import PasswordHelper


async def create_default_admin():
    """
    Create a default admin user if it doesn't exist.
    Credentials are read from environment variables:
    - DEFAULT_ADMIN_EMAIL
    - DEFAULT_ADMIN_PASSWORD
    """
    default_email = os.getenv("DEFAULT_ADMIN_EMAIL")
    default_password = os.getenv("DEFAULT_ADMIN_PASSWORD")
    
    # Skip if env variables are not set
    if not default_email or not default_password:
        print("⚠️  Default admin credentials not configured. Skipping default admin creation.")
        return
    
    try:
        async with async_session_maker() as session:
            # Check if admin user already exists
            stmt = select(User).where(User.email == default_email)
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                # Update role to admin if user exists but is not admin
                if existing_user.role != 'admin':
                    print(f"👤 User {default_email} exists but is not admin. Promoting to admin.")
                    existing_user.role = 'admin'
                    await session.commit()
                    print(f"✅ User {default_email} promoted to admin role")
                else:
                    print(f"✅ Default admin user {default_email} already exists")
                return
            
            # Create the default admin user
            password_helper = PasswordHelper()
            hashed_password = password_helper.hash(default_password)
            
            new_admin = User(
                email=default_email,
                hashed_password=hashed_password,
                role='admin',
                is_active=True,
                is_verified=True,
                is_superuser=False
            )
            
            session.add(new_admin)
            await session.commit()
            await session.refresh(new_admin)
            
            print(f"✅ Default admin user created successfully")
            print(f"   📧 Email: {default_email}")
            print(f"   👑 Role: admin")
            print(f"   🆔 User ID: {new_admin.id}")
            
    except Exception as e:
        print(f"❌ Error creating default admin user: {e}")
        raise
