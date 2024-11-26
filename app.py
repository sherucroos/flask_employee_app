from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Employee  # Import models

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database setup
DATABASE = 'employees.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def launch():
    # Show the login/register page
    if request.method == 'POST':
        if 'login' in request.form:
            # Login Form Submission
            return redirect(url_for('login'))
        elif 'register' in request.form:
            # Register Form Submission
            return redirect(url_for('register'))

    return render_template('launch.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  # Role selected by the user
        
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            if user.user_type == role:
                # Role matches
                login_user(user)
                flash('Logged in successfully!')
                return redirect(url_for('dashboard'))
            else:
                # Role does not match
                flash('Invalid role for the selected username.')
        else:
            flash('Invalid username or password!')

    return redirect(url_for('launch'))  # If login fails, redirect to launch page


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if not username or not password or not role:
            flash('All fields are required!')
            return redirect(url_for('register'))

        # Hash password
        hashed_password = generate_password_hash(password, method='sha256')

        # Check if the user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!')
            return redirect(url_for('register'))

        new_user = User(username=username, password=hashed_password, user_type=role)
        db.session.add(new_user)
        db.session.commit()

        flash('User registered successfully!')
        return redirect(url_for('login'))

    return redirect(url_for('launch'))  # If registration fails, redirect to launch page



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

        if not name or not role:
            flash('Name and Role are required!')
            return redirect(url_for('add_employee'))

        new_employee = Employee(name=name, role=role, created_by=current_user.id)
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

# Home/Dashboard route
@app.route('/')
@login_required
def dashboard():
    conn = get_db_connection()
    total_employees = conn.execute('SELECT COUNT(*) FROM employees').fetchone()[0]
    conn.close()
    return render_template('dashboard.html', total_employees=total_employees)

# Delete employee route
@app.route('/delete_employee/<int:id>')
@login_required
def delete_employee(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM employees WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Employee deleted successfully!')
    return redirect(url_for('employee_list'))

if __name__ == '__main__':
    # Ensure tables are created within the app context
    with app.app_context():
        db.create_all()  # This creates the necessary tables based on the models
    app.run(debug=True)  # Start the Flask application
