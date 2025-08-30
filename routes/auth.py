from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from models import User
from database import db_session
from werkzeug.security import generate_password_hash, check_password_hash
# Import twilio for OTP (simplified)

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = db_session.query(User).filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        # Send OTP (mocked)
        # twilio_client.messages.create(to=user.phone, from_=Config.TWILIO_PHONE, body='Your OTP: 123456')
        access_token = create_access_token(identity={'id': user.id, 'role': user.role})
        return jsonify(access_token=access_token)
    return jsonify({'msg': 'Invalid credentials'}), 401

@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_pw = generate_password_hash(data['password'])
    new_user = User(username=data['username'], email=data['email'], phone=data['phone'], password_hash=hashed_pw, role=data['role'])
    db_session.add(new_user)
    db_session.commit()
    return jsonify({'msg': 'User registered'})