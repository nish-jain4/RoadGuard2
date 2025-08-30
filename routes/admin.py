from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Request, User
from database import db_session
from utils.notifications import send_notification

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/pending_requests', methods=['GET'])
@jwt_required()
def pending_requests():
    identity = get_jwt_identity()
    if identity['role'] != 'admin':
        return jsonify({'msg': 'Unauthorized'}), 403
    requests = db_session.query(Request).filter_by(status='pending').all()
    return jsonify([{'id': r.id, 'user_id': r.user_id, 'service_type': r.service_type} for r in requests])

@bp.route('/assign_worker', methods=['POST'])
@jwt_required()
def assign_worker():
    identity = get_jwt_identity()
    if identity['role'] != 'admin':
        return jsonify({'msg': 'Unauthorized'}), 403
    data = request.json
    req = db_session.query(Request).filter_by(id=data['request_id']).first()
    req.worker_id = data['worker_id']
    req.status = 'assigned'
    db_session.commit()
    send_notification('worker', f'Assigned to request {req.id}', user_id=req.worker_id)
    send_notification('user', f'Your request {req.id} has been assigned', user_id=req.user_id)
    return jsonify({'msg': 'Worker assigned'})