"""Database initialization script - runs at build time to seed the database."""
import os
import sys

# Set FLAG environment variable before importing app
os.environ.setdefault('FLAG', 'flag{placeholder}')

from app import init_db

if __name__ == '__main__':
    init_db()
    print('Database initialized successfully.')
