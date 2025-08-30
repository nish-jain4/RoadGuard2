from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Request
from database import db_session
from utils.notifications import send_notification

bp = Blueprint('worker', __name__, url_prefix='/worker')

@bp.route('/tasks', methods=['GET'])
@jwt_required()
def list_tasks():
    identity = get_jwt_identity()
    tasks = db_session.query(Request).filter_by(worker_id=identity['id']).all()
    return jsonify([{'id': t.id, 'status': t.status, 'vehicle_info': t.vehicle_info} for t in tasks])

@bp.route('/update_status', methods=['POST'])
@jwt_required()
def update_status():
    identity = get_jwt_identity()
    data = request.json
    req = db_session.query(Request).filter_by(id=data['request_id'], worker_id=identity['id']).first()
    if req:
        req.status = data['status']  # e.g., 'in_progress', 'completed'
        req.comments = data.get('comments')
        db_session.commit()
        send_notification('user', f'Your request {req.id} status: {req.status}', user_id=req.user_id)
        if req.status == 'completed':
            # Trigger payment or rating prompt
            pass
        return jsonify({'msg': 'Status updated'})
    return jsonify({'msg': 'Not found'}), 404