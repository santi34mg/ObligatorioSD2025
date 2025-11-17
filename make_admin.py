#!/usr/bin/env python3
"""
Script to promote a user to admin role.
Usage: python make_admin.py <email>
"""

import sys
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the services directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services', 'auth-service'))

from sqlalchemy import select, update
from app.db import User, async_session_maker


async def make_admin(email: str):
    """Promote a user to admin role."""
    async with async_session_maker() as session:
        # Check if user exists
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user is None:
            print(f"Error: User with email '{email}' not found.")
            print("Please register the user first through the application.")
            return False
        
        if user.role == 'admin':
            print(f"User '{email}' is already an admin.")
            return True
        
        # Update user role
        stmt = update(User).where(User.email == email).values(role='admin')
        await session.execute(stmt)
        await session.commit()
        
        print(f"Success! User '{email}' has been promoted to admin.")
        print(f"   User ID: {user.id}")
        print(f"   Previous role: {user.role}")
        print(f"   New role: admin")
        print("\nNote: The user needs to logout and login again to see admin features.")
        return True


async def list_users():
    """List all users and their roles."""
    async with async_session_maker() as session:
        stmt = select(User)
        result = await session.execute(stmt)
        users = result.scalars().all()
        
        if not users:
            print("No users found in database.")
            return
        
        print("\nUsers in database:")
        print("-" * 80)
        print(f"{'Email':<40} {'Role':<10} {'Active':<8} {'Verified':<10}")
        print("-" * 80)
        for user in users:
            active = "Y" if user.is_active else "N"
            verified = "Y" if user.is_verified else "N"
            print(f"{user.email:<40} {user.role:<10} {active:<8} {verified:<10}")
        print("-" * 80)
        print(f"Total users: {len(users)}")


async def demote_admin(email: str):
    """Demote an admin to student role."""
    async with async_session_maker() as session:
        # Check if user exists
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user is None:
            print(f"Error: User with email '{email}' not found.")
            return False
        
        if user.role == 'student':
            print(f"User '{email}' is already a student.")
            return True
        
        # Update user role
        stmt = update(User).where(User.email == email).values(role='student')
        await session.execute(stmt)
        await session.commit()
        
        print(f"Success! User '{email}' has been demoted to student.")
        print(f"   User ID: {user.id}")
        print(f"   Previous role: {user.role}")
        print(f"   New role: student")
        return True


def print_usage():
    """Print usage information."""
    print("Usage:")
    print("  python make_admin.py <email>           - Promote user to admin")
    print("  python make_admin.py --list            - List all users")
    print("  python make_admin.py --demote <email>  - Demote admin to student")
    print("\nExamples:")
    print("  python make_admin.py admin@example.com")
    print("  python make_admin.py --list")
    print("  python make_admin.py --demote user@example.com")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing arguments\n")
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "--list":
        asyncio.run(list_users())
    elif command == "--demote":
        if len(sys.argv) < 3:
            print("Error: Email required for --demote\n")
            print_usage()
            sys.exit(1)
        email = sys.argv[2]
        asyncio.run(demote_admin(email))
    elif command in ["--help", "-h"]:
        print_usage()
    else:
        # Assume it's an email to promote
        email = command
        asyncio.run(make_admin(email))
