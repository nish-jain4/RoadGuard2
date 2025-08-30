from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Request, Workshop
from database import db_session
from geopy.distance import geodesic  # For distance filtering
from utils.notifications import send_notification

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/workshops', methods=['GET'])
@jwt_required()
def list_workshops():
    # Filters: distance, status, sort by nearby/rating
    lat = float(request.args.get('lat'))
    long = float(request.args.get('long'))
    radius = int(request.args.get('radius', 10))  # km
    workshops = db_session.query(Workshop).all()
    filtered = [w for w in workshops if geodesic((lat, long), (w.location_lat, w.location_long)).km <= radius]
    filtered.sort(key=lambda w: geodesic((lat, long), (w.location_lat, w.location_long)).km)  # Sort by nearby
    return jsonify([{'id': w.id, 'name': w.name, 'rating': w.rating} for w in filtered])

@bp.route('/submit_request', methods=['POST'])
@jwt_required()
def submit_request():
    identity = get_jwt_identity()
    data = request.json
    new_request = Request(user_id=identity['id'], vehicle_info=data['vehicle_info'], service_type=data['service_type'],
                          location_lat=data['lat'], location_long=data['long'], photos=','.join(data.get('photos', [])))
    db_session.add(new_request)
    db_session.commit()
    send_notification('admin', f'New request {new_request.id} submitted')  # Notify admin
    # Multi-workshop: Optionally send to multiple workshops
    return jsonify({'msg': 'Request submitted', 'id': new_request.id})