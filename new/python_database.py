# app.py - Flask backend for RoadGuard login system
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure random key for production

# Database initialization
def init_db():
    conn = sqlite3.connect('roadguard.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  role TEXT NOT NULL,
                  full_name TEXT,
                  phone TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
<<<<<<< HEAD
    # Check if we have any users, if not create sample data
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        # Create sample users for each role
        sample_users = [
            ('user@example.com', generate_password_hash('password123'), 'user', 'John Driver', '555-1234'),
            ('mechanic@example.com', generate_password_hash('password123'), 'mechanic', 'Mike Mechanic', '555-5678'),
            ('admin@example.com', generate_password_hash('password123'), 'admin', 'Admin User', '555-9012')
        ]
=======
    # Insert sample data if needed
    try:
        # Sample user (password: user123)
        c.execute("INSERT INTO nistha (email, password, name, role) VALUES (?, ?, ?, ?)",
                 ('user@example.com', hashlib.sha256('user123'.encode()).hexdigest(), 'John Doe', 'user'))
>>>>>>> 958fded (un)
        
        c.executemany('INSERT INTO users (email, password_hash, role, full_name, phone) VALUES (?, ?, ?, ?, ?)',
                      sample_users)
    
    conn.commit()
    conn.close()

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('roadguard.db')
    conn.row_factory = sqlite3.Row
    return conn

# Email validation function
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/new/login', methods=['POST'])
def login():
<<<<<<< HEAD
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    
    # Validate input
    if not email or not password or not role:
        return jsonify({'error': 'All fields are required'}), 400
    
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Check credentials against database
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        if user['role'] != role:
            return jsonify({'error': f'Invalid role for this account. Your account is for {user["role"]}s.'}), 400
=======
    """Handle user login"""
    try:
        data = request.get_json() 
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
>>>>>>> 958fded (un)
        
        # Store user in session
        session['user_id'] = user['id']
        session['email'] = user['email']
        session['role'] = user['role']
        session['full_name'] = user['full_name']
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'role': user['role'],
                'full_name': user['full_name']
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    full_name = data.get('full_name')
    phone = data.get('phone')
    
    # Validate input
    if not email or not password or not role:
        return jsonify({'error': 'Email, password, and role are required'}), 400
    
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Check if user already exists
    conn = get_db_connection()
    existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    
    if existing_user:
        conn.close()
        return jsonify({'error': 'User with this email already exists'}), 409
    
    # Create new user
    hashed_password = generate_password_hash(password)
    conn.execute('INSERT INTO users (email, password_hash, role, full_name, phone) VALUES (?, ?, ?, ?, ?)',
                 (email, hashed_password, role, full_name, phone))
    conn.commit()
    
    # Get the newly created user
    new_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    return jsonify({
        'message': 'Registration successful',
        'user': {
            'id': new_user['id'],
            'email': new_user['email'],
            'role': new_user['role'],
            'full_name': new_user['full_name']
        }
    }), 201

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    # Redirect based on role
    if session['role'] == 'user':
        return redirect(url_for('user_dashboard'))
    elif session['role'] == 'mechanic':
        return redirect(url_for('mechanic_dashboard'))
    elif session['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    return redirect(url_for('login_page'))

@app.route('/user-dashboard')
def user_dashboard():
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('login_page'))
    return f"Welcome to User Dashboard, {session['full_name']}!"

@app.route('/agent-dashboard')
def mechanic_dashboard():
    if 'user_id' not in session or session['role'] != 'mechanic':
        return redirect(url_for('login_page'))
    return f"Welcome to Mechanic Dashboard, {session['full_name']}!"

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login_page'))
    return f"Welcome to Admin Dashboard, {session['full_name']}!"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=3000)