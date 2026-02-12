import sqlite3
import os
from config import DATABASE_PATH


def get_db():
    """Get a database connection."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Initialize the database schema and seed data."""
    conn = get_db()
    cursor = conn.cursor()

    # Services table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ea_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            duration INTEGER NOT NULL DEFAULT 30,
            price REAL NOT NULL DEFAULT 0.00,
            currency TEXT NOT NULL DEFAULT 'USD',
            description TEXT,
            availabilities_type TEXT DEFAULT 'flexible',
            attendants_number INTEGER DEFAULT 1,
            is_private INTEGER DEFAULT 0
        )
    ''')

    # Service categories
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ea_service_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')

    # Providers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ea_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            mobile_number TEXT,
            phone_number TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            notes TEXT,
            id_roles INTEGER NOT NULL,
            timezone TEXT DEFAULT 'UTC'
        )
    ''')

    # Roles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ea_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            appointments INTEGER DEFAULT 0,
            customers INTEGER DEFAULT 0,
            services INTEGER DEFAULT 0,
            users INTEGER DEFAULT 0,
            system_settings INTEGER DEFAULT 0,
            user_settings INTEGER DEFAULT 0
        )
    ''')

    # Appointments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ea_appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_datetime TEXT,
            start_datetime TEXT NOT NULL,
            end_datetime TEXT NOT NULL,
            location TEXT,
            notes TEXT,
            hash TEXT,
            is_unavailable INTEGER DEFAULT 0,
            id_users_provider INTEGER,
            id_users_customer INTEGER,
            id_services INTEGER,
            id_google_calendar TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Customers (separate from providers/admins)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ea_users_customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone_number TEXT,
            address TEXT,
            city TEXT,
            zip_code TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ea_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            value TEXT
        )
    ''')

    # Seed roles
    cursor.execute("SELECT COUNT(*) FROM ea_roles")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO ea_roles (name, slug, is_admin, appointments, customers, services, users, system_settings, user_settings) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ('Administrator', 'admin', 1, 15, 15, 15, 15, 15, 15),
                ('Provider', 'provider', 0, 15, 15, 0, 0, 0, 15),
                ('Customer', 'customer', 0, 0, 0, 0, 0, 0, 0),
                ('Secretary', 'secretary', 0, 15, 15, 0, 0, 0, 15),
            ]
        )

    # Seed service categories
    cursor.execute("SELECT COUNT(*) FROM ea_service_categories")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO ea_service_categories (name, description) VALUES (?, ?)",
            [
                ('General', 'General consultation services'),
                ('Specialist', 'Specialist consultation services'),
            ]
        )

    # Seed services
    cursor.execute("SELECT COUNT(*) FROM ea_services")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO ea_services (name, duration, price, currency, description) VALUES (?, ?, ?, ?, ?)",
            [
                ('General Consultation', 30, 50.00, 'USD', 'Standard general consultation appointment'),
                ('Extended Consultation', 60, 90.00, 'USD', 'Extended consultation for complex cases'),
                ('Follow-up Visit', 15, 25.00, 'USD', 'Quick follow-up on previous consultation'),
                ('New Patient Intake', 45, 75.00, 'USD', 'Initial intake appointment for new patients'),
            ]
        )

    # Seed providers
    cursor.execute("SELECT COUNT(*) FROM ea_users")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO ea_users (first_name, last_name, email, mobile_number, id_roles, timezone) VALUES (?, ?, ?, ?, ?, ?)",
            [
                ('Admin', 'User', 'admin@example.org', '+1-555-0100', 1, 'America/New_York'),
                ('Jane', 'Smith', 'jane.smith@example.org', '+1-555-0101', 2, 'America/New_York'),
                ('Robert', 'Johnson', 'robert.johnson@example.org', '+1-555-0102', 2, 'America/Chicago'),
            ]
        )

    # Seed settings
    cursor.execute("SELECT COUNT(*) FROM ea_settings")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO ea_settings (name, value) VALUES (?, ?)",
            [
                ('company_name', 'Easy!Appointments Demo'),
                ('company_email', 'info@easyappointments.org'),
                ('company_link', 'https://easyappointments.org'),
                ('company_working_plan', '{"monday":{"start":"09:00","end":"18:00","breaks":[{"start":"12:00","end":"13:00"}]},"tuesday":{"start":"09:00","end":"18:00","breaks":[{"start":"12:00","end":"13:00"}]},"wednesday":{"start":"09:00","end":"18:00","breaks":[{"start":"12:00","end":"13:00"}]},"thursday":{"start":"09:00","end":"18:00","breaks":[{"start":"12:00","end":"13:00"}]},"friday":{"start":"09:00","end":"17:00","breaks":[{"start":"12:00","end":"13:00"}]},"saturday":null,"sunday":null}'),
                ('date_format', 'DMY'),
                ('time_format', 'regular'),
                ('google_analytics_code', ''),
                ('matomo_analytics_url', ''),
                ('display_cookie_notice', '0'),
                ('cookie_notice_content', 'This website uses cookies to ensure you get the best experience.'),
                ('display_terms_and_conditions', '0'),
                ('terms_and_conditions_content', ''),
                ('display_privacy_policy', '0'),
                ('privacy_policy_content', ''),
            ]
        )

    # Seed some existing appointments for realism
    cursor.execute("SELECT COUNT(*) FROM ea_appointments")
    if cursor.fetchone()[0] == 0:
        import hashlib
        cursor.executemany(
            "INSERT INTO ea_users_customers (first_name, last_name, email, phone_number, address, city, zip_code, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ('Alice', 'Williams', 'alice.w@example.com', '+1-555-2001', '123 Oak St', 'Springfield', '62704', 'Regular patient'),
                ('Bob', 'Davis', 'bob.d@example.com', '+1-555-2002', '456 Elm Ave', 'Shelbyville', '62565', 'Prefers morning appointments'),
                ('Carol', 'Martinez', 'carol.m@example.com', '+1-555-2003', '789 Pine Rd', 'Capital City', '62701', ''),
            ]
        )
        cursor.executemany(
            "INSERT INTO ea_appointments (start_datetime, end_datetime, notes, hash, id_users_provider, id_users_customer, id_services) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ('2024-03-15 09:00:00', '2024-03-15 09:30:00', 'Routine checkup', hashlib.md5(b'appt1').hexdigest(), 2, 1, 1),
                ('2024-03-15 10:00:00', '2024-03-15 11:00:00', 'Follow-up on previous visit', hashlib.md5(b'appt2').hexdigest(), 2, 2, 2),
                ('2024-03-16 14:00:00', '2024-03-16 14:15:00', 'Quick follow-up', hashlib.md5(b'appt3').hexdigest(), 3, 3, 3),
            ]
        )

    conn.commit()
    conn.close()
