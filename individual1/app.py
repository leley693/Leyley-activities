from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'secret500k'

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="3"
    )

@app.route('/')
def home():
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (fullname, email, phone, address, username, password)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (fullname, email, phone, address, username, password))
            conn.commit()
            flash('Account created successfully!', 'success')
            return redirect('/login')
        except mysql.connector.IntegrityError:
            flash('Username already taken!', 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and check_password_hash(user['password'], password_input):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/dashboard')
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('dashboard.html', employees=employees)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    email = request.form['email']
    position = request.form['position']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO employees (name, email, position) VALUES (%s, %s, %s)", (name, email, position))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Employee added!', 'success')
    return redirect('/dashboard')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        cursor.execute("UPDATE employees SET name=%s, email=%s, position=%s WHERE id=%s", (name, email, position, id))
        conn.commit()
        flash('Employee updated!', 'success')
        return redirect('/dashboard')
    else:
        cursor.execute("SELECT * FROM employees WHERE id = %s", (id,))
        employee = cursor.fetchone()
        return render_template('edit.html', employee=employee)

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Employee deleted.', 'warning')
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
