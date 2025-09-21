#!/usr/bin/env python3
"""
Database Initialization Script
This script sets up the database schema and creates initial data
"""

import os
import sys
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path

def load_env_file(file_path):
    """Load environment variables from .env file"""
    env_vars = {}
    if Path(file_path).exists():
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    return env_vars

def parse_database_url(url):
    """Parse PostgreSQL URL into components"""
    # Format: postgresql://user:password@host:port/database
    url = url.replace('postgresql://', '')
    
    if '@' in url:
        auth, host_db = url.split('@', 1)
        if ':' in auth:
            user, password = auth.split(':', 1)
        else:
            user, password = auth, ''
    else:
        user, password = 'postgres', ''
        host_db = url
    
    if '/' in host_db:
        host_port, database = host_db.split('/', 1)
    else:
        host_port, database = host_db, 'postgres'
    
    if ':' in host_port:
        host, port = host_port.split(':', 1)
        port = int(port)
    else:
        host, port = host_port, 5432
    
    return {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }

def wait_for_postgres(conn_params, max_attempts=30):
    """Wait for PostgreSQL to be ready"""
    print("⏳ Waiting for PostgreSQL to be ready...")
    
    for attempt in range(max_attempts):
        try:
            # Try to connect to default postgres database
            test_params = conn_params.copy()
            test_params['database'] = 'postgres'
            
            conn = psycopg2.connect(**test_params)
            conn.close()
            print("✅ PostgreSQL is ready")
            return True
        except psycopg2.OperationalError:
            print(f"   Attempt {attempt + 1}/{max_attempts} - Waiting...")
            time.sleep(2)
    
    print("❌ PostgreSQL not available after waiting")
    return False

def create_database(conn_params, database_name):
    """Create database if it doesn't exist"""
    print(f"🗄️  Creating database '{database_name}'...")
    
    try:
        # Connect to default postgres database
        test_params = conn_params.copy()
        test_params['database'] = 'postgres'
        
        conn = psycopg2.connect(**test_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {database_name}")
            print(f"✅ Database '{database_name}' created")
        else:
            print(f"✅ Database '{database_name}' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error creating database: {e}")
        return False

def init_user_service_tables(conn_params):
    """Initialize user service tables"""
    print("📊 Initializing user service tables...")
    
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create chat_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                user_id INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create chat_messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id SERIAL PRIMARY KEY,
                session_id INTEGER REFERENCES chat_sessions(id),
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON chat_sessions(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session_id ON chat_messages(session_id)")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ User service tables created")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_sample_data(conn_params):
    """Create sample users for testing"""
    print("👤 Creating sample users...")
    
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Sample users
        sample_users = [
            ("admin", "admin@example.com"),
            ("user", "user@example.com"),
            ("demo", "demo@example.com")
        ]
        
        for username, email in sample_users:
            cursor.execute("""
                INSERT INTO users (username, email) 
                VALUES (%s, %s) 
                ON CONFLICT (username) DO NOTHING
            """, (username, email))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Sample users created")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def main():
    """Main initialization function"""
    print("🗄️  Database Initialization")
    print("="*30)
    
    # Load environment variables
    env_vars = load_env_file('.env')
    
    # Get database URL
    database_url = env_vars.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/chatbot_db')
    
    # Parse database connection parameters
    conn_params = parse_database_url(database_url)
    database_name = conn_params['database']
    
    print(f"🔗 Connecting to PostgreSQL at {conn_params['host']}:{conn_params['port']}")
    
    # Wait for PostgreSQL to be ready
    if not wait_for_postgres(conn_params):
        sys.exit(1)
    
    # Create database
    if not create_database(conn_params, database_name):
        sys.exit(1)
    
    # Initialize tables
    if not init_user_service_tables(conn_params):
        sys.exit(1)
    
    # Create sample data
    if not create_sample_data(conn_params):
        sys.exit(1)
    
    print("\n✅ Database initialization complete!")
    print("\n👤 Sample users created:")
    print("   - admin (admin@example.com)")
    print("   - user (user@example.com)")  
    print("   - demo (demo@example.com)")

if __name__ == "__main__":
    main()