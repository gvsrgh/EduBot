"""
Script to update existing @pvpsiddhartha.ac.in users to have admin privileges.
Run this script to grant admin access to existing users with the correct domain.
"""
import asyncio
from sqlalchemy import select, update
from app.db.database import get_session
from app.db.models import User


async def update_admin_users():
    """Update all @pvpsiddhartha.ac.in users to have admin privileges."""
    async for session in get_session():
        try:
            # Find all users with @pvpsiddhartha.ac.in email
            result = await session.execute(
                select(User).where(User.email.like('%@pvpsiddhartha.ac.in'))
            )
            users = result.scalars().all()
            
            if not users:
                print("No users found with @pvpsiddhartha.ac.in domain")
                return
            
            print(f"Found {len(users)} user(s) with @pvpsiddhartha.ac.in domain:")
            for user in users:
                print(f"  - {user.email} (currently admin: {user.is_admin})")
            
            # Update them to be admins
            await session.execute(
                update(User)
                .where(User.email.like('%@pvpsiddhartha.ac.in'))
                .values(is_admin=True)
            )
            
            await session.commit()
            print("\n✓ Successfully updated all @pvpsiddhartha.ac.in users to admin status")
            
        except Exception as e:
            print(f"Error updating users: {e}")
            await session.rollback()
        finally:
            break  # Only use the first session


if __name__ == "__main__":
    print("Updating admin privileges for @pvpsiddhartha.ac.in users...\n")
    asyncio.run(update_admin_users())
