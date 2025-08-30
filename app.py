from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)  # secure random key for production
from flask import flash  # add at the top with other imports

# ----------------------------
# Registration
# ----------------------------
@app.route("/api/register", methods=["POST"])
def api_register():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    role = data.get("role")
    password = data.get("password")

    if not name or not email or not role or not password:
        return jsonify({"error": "All required fields must be filled"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (email, password_hash, role, full_name, phone) VALUES (?, ?, ?, ?, ?)",
            (email, generate_password_hash(password), role, name, phone),
        )
        conn.commit()
        user_id = cur.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Email already registered"}), 400
    finally:
        conn.close()

    # set session
    session["user_id"] = user_id
    session["email"] = email
    session["role"] = role
    session["full_name"] = name

    return jsonify({
        "message": "Registration successful",
        "user": {
            "id": user_id,
            "email": email,
            "role": role,
            "full_name": name
        }
    }), 200


# ----------------------------
# Database setup
# ----------------------------
def init_db():
    conn = sqlite3.connect('roadguard.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  role TEXT NOT NULL,
                  full_name TEXT,
                  phone TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # Create default users (if DB empty)
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        sample_users = [
            ('user@example.com', generate_password_hash('password123'), 'user', 'John Driver', '555-1234'),
            ('mechanic@example.com', generate_password_hash('password123'), 'mechanic', 'Mike Mechanic', '555-5678'),
            ('admin@example.com', generate_password_hash('password123'), 'admin', 'Admin User', '555-9012')
        ]
        c.executemany('INSERT INTO users (email, password_hash, role, full_name, phone) VALUES (?, ?, ?, ?, ?)', sample_users)

    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect('roadguard.db')
    conn.row_factory = sqlite3.Row
    return conn


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# ----------------------------
# Routes
# ----------------------------
@app.route('/')
def index():
    return redirect(url_for('login_page'))


@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')  # must exist in templates/


@app.route('/api/login', methods=['POST'])
def login():
    # Check if request is JSON or form data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not email or not password or not role:
        return jsonify({'error': 'All fields are required'}), 400
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        if user['role'] != role:
            return jsonify({'error': f'Your account is registered as {user["role"]}'}), 400

        # set session
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


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    # role-based dashboards
    if session['role'] == 'user':
        return f"👤 User Dashboard — Welcome {session['email']}"
    elif session['role'] == 'mechanic':
        return f"🔧 Mechanic Dashboard — Welcome {session['email']}"
    elif session['role'] == 'admin':
        return f"🛠️ Admin Dashboard — Welcome {session['email']}"
    else:
        return redirect(url_for('logout'))


@app.route('/user-dashboard')
def user_dashboard():
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('login_page'))
    return f"Welcome to User Dashboard, {session.get('full_name', session['email'])}!"


@app.route('/agent-dashboard')
def mechanic_dashboard():
    if 'user_id' not in session or session['role'] != 'mechanic':
        return redirect(url_for('login_page'))
    return f"Welcome to Mechanic Dashboard, {session.get('full_name', session['email'])}!"


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login_page'))
    return f"Welcome to Admin Dashboard, {session.get('full_name', session['email'])}!"


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))


# ----------------------------
# Main
# ----------------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=3000)