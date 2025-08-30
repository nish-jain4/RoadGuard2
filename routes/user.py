from flask import Blueprint, request, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Request, Workshop
from database import db_session
from geopy.distance import geodesic
from utils.notifications import send_notification

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/workshops', methods=['GET'])
@jwt_required()
def workshops_page():
    identity = get_jwt_identity()
    lat = float(request.args.get('lat', 0))  # Default or from user location
    long = float(request.args.get('long', 0))
    radius = int(request.args.get('radius', 10))
    workshops = db_session.query(Workshop).all()
    filtered = [w for w in workshops if geodesic((lat, long), (w.location_lat, w.location_long)).km <= radius]
    filtered.sort(key=lambda w: geodesic((lat, long), (w.location_lat, w.location_long)).km)
    return render_template('workshops.html', workshops=filtered)  # Pass data to your workshops.html

@bp.route('/workshop_details/<int:workshop_id>', methods=['GET'])
@jwt_required()
def workshop_details(workshop_id):
    workshop = db_session.query(Workshop).filter_by(id=workshop_id).first()
    if not workshop:
        return 'Not found', 404
    return render_template('workshop_details.html', workshop=workshop)

@bp.route('/request_form', methods=['GET', 'POST'])
@jwt_required()
def request_form():
    if request.method == 'GET':
        return render_template('request_form.html')
    identity = get_jwt_identity()
    data = request.form
    new_request = Request(user_id=identity['id'], vehicle_info=data['vehicle_info'], service_type=data['service_type'],
                          location_lat=float(data['lat']), location_long=float(data['long']), photos=data.get('photos'))
    db_session.add(new_request)
    db_session.commit()
    send_notification('admin', f'New request {new_request.id} submitted')
    return redirect(url_for('user.request_status'))

@bp.route('/request_status', methods=['GET'])
@jwt_required()
def request_status():
    identity = get_jwt_identity()
    requests = db_session.query(Request).filter_by(user_id=identity['id']).all()
    return render_template('request_status.html', requests=requests)

@bp.route('/request_details/<int:request_id>', methods=['GET'])
@jwt_required()
def request_details(request_id):
    identity = get_jwt_identity()
    req = db_session.query(Request).filter_by(id=request_id, user_id=identity['id']).first()
    if not req:
        return 'Not found', 404
    return render_template('request_details.html', request=req)