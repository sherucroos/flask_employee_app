from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime  # Optional: For generating dates if needed

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)  # 'employee' or 'business_owner'
    
    # Relationship with Employee table (optional)
    employees = db.relationship('Employee', backref='creator', lazy=True)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)  # Added email
    phone = db.Column(db.String(15), nullable=True)  # Added phone, adjust length as necessary
    department = db.Column(db.String(100), nullable=True)  # Added department
    join_date = db.Column(db.Date, nullable=False, default=datetime.datetime.utcnow)  # Use default for current date
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    
    # Relationship with the User table (optional)
    creator = db.relationship('User', backref=db.backref('employees', lazy=True))
