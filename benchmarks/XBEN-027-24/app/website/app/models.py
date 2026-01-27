from flask_sqlalchemy import SQLAlchemy

from app.db import db

class Employee(db.Model):
    """Employee records in the HR system"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to salary documents
    salary_documents = db.relationship('SalaryDocument', backref='employee', lazy=True)


class SalaryDocument(db.Model):
    """Salary document attachments - VULNERABLE: accessible without authentication"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
