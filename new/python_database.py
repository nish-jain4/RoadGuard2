from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import jwt
import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect('roadguard.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 email TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL,
                 name TEXT NOT NULL,
                 role TEXT NOT NULL,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Insert sample data if needed
    try:
        # Sample user (password: user123)
        c.execute("INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)",
                 ('user@example.com', hashlib.sha256('user123'.encode()).hexdigest(), 'John Doe', 'user'))
        
        # Sample mechanic (password: mechanic123)
        c.execute("INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)",
                 ('mechanic@example.com', hashlib.sha256('mechanic123'.encode()).hexdigest(), 'Jane Smith', 'mechanic'))
        
        # Sample admin (password: admin123)
        c.execute("INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)",
                 ('admin@example.com', hashlib.sha256('admin123'.encode()).hexdigest(), 'Admin User', 'admin'))
    except sqlite3.IntegrityError:
        # Records already exist
        pass
    
    conn.commit()
    conn.close()

def verify_password(stored_password, provided_password):
    """Verify if the provided password matches the stored hash"""
    return stored_password == hashlib.sha256(provided_password.encode()).hexdigest()

@app.route('/api/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        
        if not email or not password or not role:
            return jsonify({'error': 'Email, password and role are required'}), 400
        
        # Connect to database
        conn = sqlite3.connect('roadguard.db')
        c = conn.cursor()
        
        # Find user by email
        c.execute("SELECT id, email, password, name, role FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()
        
        if user is None:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not verify_password(user[2], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify role
        if user[4] != role:
            return jsonify({'error': 'Access denied for this role'}), 403
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user[0],
            'email': user[1],
            'role': user[4],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user_id': user[0],
            'name': user[3],
            'email': user[1],
            'role': user[4]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Server error: ' + str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)