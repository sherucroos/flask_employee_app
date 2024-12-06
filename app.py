from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime  # Import datetime to handle join_date

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)  # 'business_owner' or 'employee'

    # Relationship with Employee table (optional)
    employees = db.relationship('Employee', backref='creator', lazy=True)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)  # Added email
    phone = db.Column(db.String(20), nullable=False)  # Added phone
    department = db.Column(db.String(100), nullable=False)  # Added department
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    join_date = db.Column(db.String(20), nullable=False)  # Date the employee was added

# Initialize the login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def launch():
    if request.method == 'POST':
        if 'login' in request.form:
            return redirect(url_for('login'))
        elif 'register' in request.form:
            return redirect(url_for('register'))
    return render_template('launch.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            if user.user_type == role:
                login_user(user)
                flash('Logged in successfully!')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid role for the selected username.')
        else:
            flash('Invalid username or password!')

    return redirect(url_for('launch'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if not username or not password or not role:
            flash('All fields are required!')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='sha256')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!')
            return redirect(url_for('register'))

        new_user = User(username=username, password=hashed_password, user_type=role)
        db.session.add(new_user)
        db.session.commit()

        flash('User registered successfully!')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('login'))

@app.route('/add_employee', methods=['GET', 'POST'])
@login_required
def add_employee():
    if current_user.user_type != 'business_owner':
        flash('You do not have permission to add employees.')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        email = request.form['email']
        phone = request.form['phone']
        department = request.form['department']

        if not name or not role or not email or not phone or not department:
            flash('All fields are required!')
            return redirect(url_for('add_employee'))

        new_employee = Employee(
            name=name,
            role=role,
            email=email,
            phone=phone,
            department=department,
            created_by=current_user.id,
            join_date=datetime.now().strftime('%d-%m-%Y')  # Use current date for join_date
        )
        db.session.add(new_employee)
        db.session.commit()

        flash('Employee added successfully!')
        return redirect(url_for('employee_list'))

    return render_template('employee_form.html')

@app.route('/employees')
@login_required
def employee_list():
    employees = Employee.query.all()
    return render_template('employee_list.html', employees=employees)

@app.route('/delete_employee/<int:id>')
@login_required
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash('Employee deleted successfully!')
    return redirect(url_for('employee_list'))

@app.route('/dashboard')
@login_required
def dashboard():
    total_employees = Employee.query.count()
    return render_template('dashboard.html', total_employees=total_employees)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure database is created (run this only once)
    app.run(debug=True)
