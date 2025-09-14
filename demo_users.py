#!/usr/bin/env python3
"""
Demo user management for Medical MCP Server
"""

import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Demo users for the medical system
DEMO_USERS = {
    "demo": {
        "password_hash": hash_password("password"),
        "role": "patient",
        "name": "Demo User",
        "description": "Basic demo account for testing"
    },
    "doctor": {
        "password_hash": hash_password("secret123"),
        "role": "healthcare_provider", 
        "name": "Dr. Smith",
        "description": "Healthcare provider account"
    },
    "admin": {
        "password_hash": hash_password("admin2024"),
        "role": "administrator",
        "name": "System Admin",
        "description": "System administrator account"
    }
}

def get_user_info(username: str) -> dict:
    """Get user information by username."""
    return DEMO_USERS.get(username, {})

def verify_password(username: str, password: str) -> bool:
    """Verify user password."""
    user = DEMO_USERS.get(username)
    if not user:
        return False
    return user["password_hash"] == hash_password(password)

if __name__ == "__main__":
    print("Demo Users for Medical MCP Server:")
    print("=" * 40)
    for username, user_data in DEMO_USERS.items():
        print(f"Username: {username}")
        print(f"Role: {user_data['role']}")
        print(f"Name: {user_data['name']}")
        print(f"Description: {user_data['description']}")
        print("-" * 40)