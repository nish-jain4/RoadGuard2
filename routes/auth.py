from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from models import User
from database import db_session
from werkzeug.security import generate_password_hash, check_password_hash
# Import twilio for OTP (simplified)

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')  # Render your login HTML
    data = request.form  # Assume form submission
    user = db_session.query(User).filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        # Send OTP (mocked)
        # twilio_client.messages.create(to=user.phone, from_=Config.TWILIO_PHONE, body='Your OTP: 123456')
        access_token = create_access_token(identity={'id': user.id, 'role': user.role})
        # Store token in session or cookie if needed; for now, redirect based on role
        if user.role == 'user':
            return redirect(url_for('user.workshops_page'))
        elif user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'worker':
            return redirect(url_for('worker.tasks_page'))
        return jsonify(access_token=access_token)  # Fallback for API
    return render_template('login.html', error='Invalid credentials')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')  # Add if you have a register page
    data = request.form
    hashed_pw = generate_password_hash(data['password'])
    new_user = User(username=data['username'], email=data['email'], phone=data['phone'], password_hash=hashed_pw, role=data['role'])
    db_session.add(new_user)
    db_session.commit()
    return redirect(url_for('auth.login'))