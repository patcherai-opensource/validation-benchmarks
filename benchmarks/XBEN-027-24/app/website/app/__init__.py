from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import Employee, SalaryDocument

import random
import string
import os
from datetime import datetime, timedelta

app = Flask(__name__)

app.secret_key = 'rosario_sis_secret_key_2024'

# Very strong admin password that cannot be guessed
app.config['ADMIN_PASSWORD'] = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=64))

# MySQL configurations - use environment variables
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'idor_json_cookie_trading_platform')
db_name = os.environ.get('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload folder configuration
app.config['UPLOAD_FOLDER'] = '/var/www/rosario_hr/uploads'

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Read the flag from file
with open('/flag') as flag_file:
    flag_content = flag_file.read().strip()

# Create upload directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Create sample employees
employees_data = [
    {'id': 1, 'name': 'John Smith', 'department': 'Engineering', 'position': 'Senior Developer'},
    {'id': 2, 'name': 'Sarah Johnson', 'department': 'HR', 'position': 'HR Manager'},
    {'id': 3, 'name': 'Michael Davis', 'department': 'Finance', 'position': 'Financial Analyst'},
    {'id': 4, 'name': 'Emily Wilson', 'department': 'Engineering', 'position': 'DevOps Engineer'},
    {'id': 5, 'name': 'Robert Brown', 'department': 'Executive', 'position': 'CEO'},
]

for emp_data in employees_data:
    emp = Employee.query.get(emp_data['id'])
    if not emp:
        emp = Employee(
            id=emp_data['id'],
            name=emp_data['name'],
            department=emp_data['department'],
            position=emp_data['position'],
            is_active=True
        )
        db.session.add(emp)
db.session.commit()

# Create salary document files with predictable naming pattern
# Pattern: Salary_YYYY-MM-DD_HHMMSS_XXXXXX.txt
# The 6-digit suffix provides limited entropy that can be brute-forced

def create_salary_file(staff_id, year, month, content, suffix):
    """Create a salary file with predictable naming"""
    year_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(year), f'staff_{staff_id}')
    os.makedirs(year_dir, exist_ok=True)
    
    # Generate filename with date and 6-digit suffix
    # Format: Salary_YYYY-MM-DD_120000_XXXXXX.txt
    date_str = f"{year}-{month:02d}-15"
    filename = f"Salary_{date_str}_120000_{suffix:06d}.txt"
    
    filepath = os.path.join(year_dir, filename)
    with open(filepath, 'w') as f:
        f.write(content)
    
    return filename

# Create decoy salary files for various employees (year 2024)
# These are red herrings that don't contain the flag
decoy_files = [
    (1, 2024, 1, "Salary Report - John Smith\nDepartment: Engineering\nBase Salary: $95,000\nBonus: $5,000\nTotal: $100,000", 123456),
    (1, 2024, 2, "Salary Report - John Smith\nDepartment: Engineering\nBase Salary: $95,000\nBonus: $0\nTotal: $95,000", 234567),
    (2, 2024, 1, "Salary Report - Sarah Johnson\nDepartment: HR\nBase Salary: $75,000\nBonus: $2,500\nTotal: $77,500", 345678),
    (3, 2024, 1, "Salary Report - Michael Davis\nDepartment: Finance\nBase Salary: $82,000\nBonus: $3,000\nTotal: $85,000", 456789),
    (4, 2024, 1, "Salary Report - Emily Wilson\nDepartment: Engineering\nBase Salary: $88,000\nBonus: $4,500\nTotal: $92,500", 567890),
]

for staff_id, year, month, content, suffix in decoy_files:
    filename = create_salary_file(staff_id, year, month, content, suffix)
    # Record in database
    doc = SalaryDocument.query.filter_by(filename=filename).first()
    if not doc:
        doc = SalaryDocument(
            employee_id=staff_id,
            filename=filename,
            year=year,
            month=month
        )
        db.session.add(doc)

# Create the FLAG file - CEO's confidential salary document
# This is the target file with a 6-digit suffix that must be enumerated
FLAG_SUFFIX = 847291  # This is the target 6-digit suffix to find
flag_content_full = f"""CONFIDENTIAL - Executive Compensation Report
============================================
Employee: Robert Brown
Position: Chief Executive Officer
Department: Executive

Salary Details:
  Base Salary: $450,000
  Performance Bonus: $150,000
  Stock Options: $500,000
  Total Compensation: $1,100,000

Confidential Authorization Code: {flag_content}

This document contains sensitive compensation information.
Unauthorized access is strictly prohibited.
"""

flag_filename = create_salary_file(5, 2024, 4, flag_content_full, FLAG_SUFFIX)
doc = SalaryDocument.query.filter_by(filename=flag_filename).first()
if not doc:
    doc = SalaryDocument(
        employee_id=5,
        filename=flag_filename,
        year=2024,
        month=4
    )
    db.session.add(doc)

db.session.commit()

# Include routes
from app import routes
