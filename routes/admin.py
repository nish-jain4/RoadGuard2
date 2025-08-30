from flask import Blueprint, request, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Request, User
from database import db_session
from utils.notifications import send_notification

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    identity = get_jwt_identity()
    if identity['role'] != 'admin':
        return 'Unauthorized', 403
    pending = db_session.query(Request).filter_by(status='pending').count()
    completed = db_session.query(Request).filter_by(status='completed').count()
    return render_template('admin_dashboard.html', pending=pending, completed=completed)  # Stats for dashboard

@bp.route('/assignment_panel', methods=['GET', 'POST'])
@jwt_required()
def assignment_panel():
    identity = get_jwt_identity()
    if identity['role'] != 'admin':
        return 'Unauthorized', 403
    if request.method == 'GET':
        requests = db_session.query(Request).filter_by(status='pending').all()
        workers = db_session.query(User).filter_by(role='worker').all()
        return render_template('assignment_panel.html', requests=requests, workers=workers)
    data = request.form
    req = db_session.query(Request).filter_by(id=data['request_id']).first()
    req.worker_id = data['worker_id']
    req.status = 'assigned'
    db_session.commit()
    send_notification('worker', f'Assigned to request {req.id}', user_id=req.worker_id)
    send_notification('user', f'Your request {req.id} has been assigned', user_id=req.user_id)
    return redirect(url_for('admin.dashboard'))