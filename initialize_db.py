from app import db, app
from models import User, Employee
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create tables
    db.create_all()

    # Insert some sample data
    if not User.query.filter_by(username='owner1').first():
        owner1 = User(username='owner1', password=generate_password_hash('password123'), user_type='business_owner')
        employee1 = User(username='employee1', password=generate_password_hash('password123'), user_type='employee')

        db.session.add(owner1)
        db.session.add(employee1)
        db.session.commit()

    if not Employee.query.filter_by(name='John Doe').first():
        employee_record = Employee(name='John Doe', role='Manager', created_by=1)  # Assuming `owner1.id == 1`
        db.session.add(employee_record)
        db.session.commit()

print("Database initialized and sample data added!")
