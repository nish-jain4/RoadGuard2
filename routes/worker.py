from flask import Blueprint, request, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Request
from database import db_session
from utils.notifications import send_notification

bp = Blueprint('worker', __name__, url_prefix='/worker')

@bp.route('/tasks', methods=['GET'])
@jwt_required()
def tasks_page():
    identity = get_jwt_identity()
    tasks = db_session.query(Request).filter_by(worker_id=identity['id']).all()
    return render_template('worker_tasks.html', tasks=tasks)  # Calendar/list view

@bp.route('/request_details/<int:request_id>', methods=['GET', 'POST'])
@jwt_required()
def request_details(request_id):
    identity = get_jwt_identity()
    req = db_session.query(Request).filter_by(id=request_id, worker_id=identity['id']).first()
    if not req:
        return 'Not found', 404
    if request.method == 'GET':
        return render_template('worker_request_details.html', request=req)
    data = request.form
    req.status = data['status']
    req.comments = data.get('comments')
    db_session.commit()
    send_notification('user', f'Your request {req.id} status: {req.status}', user_id=req.user_id)
    return redirect(url_for('worker.tasks_page'))