from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database setup
DATABASE = 'employees.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Home/Dashboard route
@app.route('/')
def dashboard():
    conn = get_db_connection()
    total_employees = conn.execute('SELECT COUNT(*) FROM employees').fetchone()[0]
    conn.close()
    return render_template('dashboard.html', total_employees=total_employees)

# Employee list route
@app.route('/employees')
def employee_list():
    conn = get_db_connection()
    employees = conn.execute('SELECT * FROM employees').fetchall()
    conn.close()
    return render_template('employee_list.html', employees=employees)

# Add employee route
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']

        if not name or not role:
            flash('Name and Role are required!')
            return redirect(url_for('add_employee'))

        conn = get_db_connection()
        conn.execute('INSERT INTO employees (name, role) VALUES (?, ?)', (name, role))
        conn.commit()
        conn.close()

        flash('Employee added successfully!')
        return redirect(url_for('employee_list'))

    return render_template('employee_form.html')

# Delete employee route
@app.route('/delete_employee/<int:id>')
def delete_employee(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM employees WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Employee deleted successfully!')
    return redirect(url_for('employee_list'))

if __name__ == '__main__':
    app.run(debug=True)
