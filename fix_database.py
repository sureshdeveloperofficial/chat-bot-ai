#!/usr/bin/env python3

import sys
import os
sys.path.append('user-service')

from user_service.database import create_tables

def main():
    print("🔧 Creating database tables...")
    try:
        create_tables()
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
    main()