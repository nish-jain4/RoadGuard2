from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from datetime import datetime
import math
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'roadguard_db'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)",
                (name, email, phone, password)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            cursor.close()
            conn.close()
            return render_template('register.html', error='Email already exists')
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get active requests count
    cursor.execute("SELECT COUNT(*) as count FROM service_requests WHERE user_id = %s AND status IN ('pending', 'accepted', 'in_progress')", (user_id,))
    active_requests_count = cursor.fetchone()['count']
    
    # Get completed requests count
    cursor.execute("SELECT COUNT(*) as count FROM service_requests WHERE user_id = %s AND status = 'completed'", (user_id,))
    completed_requests_count = cursor.fetchone()['count']
    
    # Get nearby workshops count (within 10km)
    cursor.execute("SELECT latitude, longitude FROM users WHERE id = %s", (user_id,))
    user_location = cursor.fetchone()
    
    if user_location and user_location['latitude'] and user_location['longitude']:
        cursor.execute("""
            SELECT COUNT(*) as count FROM workshops 
            WHERE (6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude)))) <= 10
        """, (user_location['latitude'], user_location['longitude'], user_location['latitude']))
        nearby_workshops_count = cursor.fetchone()['count']
    else:
        nearby_workshops_count = 0
    
    # Get saved workshops count
    cursor.execute("SELECT COUNT(*) as count FROM saved_workshops WHERE user_id = %s", (user_id,))
    saved_workshops_count = cursor.fetchone()['count']
    
    # Get active requests
    cursor.execute("""
        SELECT sr.*, w.name as workshop_name 
        FROM service_requests sr 
        JOIN workshops w ON sr.workshop_id = w.id 
        WHERE sr.user_id = %s AND sr.status IN ('pending', 'accepted', 'in_progress')
        ORDER BY sr.created_at DESC LIMIT 5
    """, (user_id,))
    active_requests = cursor.fetchall()
    
    # Get nearby workshops
    if user_location and user_location['latitude'] and user_location['longitude']:
        cursor.execute("""
            SELECT *, (6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude)))) as distance 
            FROM workshops 
            WHERE (6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude)))) <= 10
            ORDER BY distance ASC LIMIT 6
        """, (user_location['latitude'], user_location['longitude'], user_location['latitude'], 
              user_location['latitude'], user_location['longitude'], user_location['latitude']))
        nearby_workshops = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM workshops ORDER BY RAND() LIMIT 6")
        nearby_workshops = cursor.fetchall()
        for workshop in nearby_workshops:
            workshop['distance'] = None
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html', 
                         active_requests_count=active_requests_count,
                         completed_requests_count=completed_requests_count,
                         nearby_workshops_count=nearby_workshops_count,
                         saved_workshops_count=saved_workshops_count,
                         active_requests=active_requests,
                         nearby_workshops=nearby_workshops)

@app.route('/workshops')
@login_required
def workshops():
    user_id = session['user_id']
    distance_filter = request.args.get('distance', '5')
    services_filter = request.args.getlist('services')
    min_rating = request.args.get('min_rating', 0)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get user location
    cursor.execute("SELECT latitude, longitude FROM users WHERE id = %s", (user_id,))
    user_location = cursor.fetchone()
    
    # Build query
    query = """
        SELECT w.*, 
               AVG(r.rating) as rating, 
               COUNT(r.id) as review_count,
               GROUP_CONCAT(DISTINCT ws.service_name) as services
        FROM workshops w
        LEFT JOIN reviews r ON w.id = r.workshop_id
        LEFT JOIN workshop_services ws ON w.id = ws.workshop_id
    """
    
    where_conditions = []
    params = []
    
    # Add services filter if specified
    if services_filter:
        service_placeholders = ', '.join(['%s'] * len(services_filter))
        where_conditions.append(f"ws.service_name IN ({service_placeholders})")
        params.extend(services_filter)
    
    # Add rating filter
    if min_rating and float(min_rating) > 0:
        where_conditions.append("(SELECT AVG(rating) FROM reviews WHERE workshop_id = w.id) >= %s")
        params.append(float(min_rating))
    
    if where_conditions:
        query += " WHERE " + " AND ".join(where_conditions)
    
    query += " GROUP BY w.id"
    
    # Add distance calculation if user location is available
    if user_location and user_location['latitude'] and user_location['longitude']:
        query = f"""
            SELECT *, 
                   (6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude)))) as distance 
            FROM ({query}) as filtered_workshops
        """
        params = [user_location['latitude'], user_location['longitude'], user_location['latitude']] + params
        
        # Apply distance filter
        if distance_filter == 'custom':
            custom_radius = request.args.get('custom_radius', 5)
            query += " HAVING distance <= %s"
            params.append(float(custom_radius))
        else:
            query += " HAVING distance <= %s"
            params.append(float(distance_filter))
        
        query += " ORDER BY distance ASC"
    else:
        query += " ORDER BY rating DESC"
    
    cursor.execute(query, params)
    workshops = cursor.fetchall()
    
    # Process services for each workshop
    for workshop in workshops:
        if workshop['services']:
            workshop['services'] = workshop['services'].split(',')
        else:
            workshop['services'] = []
    
    cursor.close()
    conn.close()
    
    return render_template('workshops.html', workshops=workshops)

@app.route('/workshops/<int:workshop_id>')
@login_required
def workshop_detail(workshop_id):
    user_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get workshop details
    cursor.execute("""
        SELECT w.*, 
               AVG(r.rating) as rating, 
               COUNT(r.id) as review_count,
               COUNT(DISTINCT sr.id) as completed_services,
               AVG(TIMESTAMPDIFF(MINUTE, sr.created_at, sr.accepted_at)) as response_time
        FROM workshops w
        LEFT JOIN reviews r ON w.id = r.workshop_id
        LEFT JOIN service_requests sr ON w.id = sr.workshop_id AND sr.status = 'completed'
        WHERE w.id = %s
        GROUP BY w.id
    """, (workshop_id,))
    workshop = cursor.fetchone()
    
    if not workshop:
        cursor.close()
        conn.close()
        return "Workshop not found", 404
    
    # Get workshop services
    cursor.execute("SELECT service_name FROM workshop_services WHERE workshop_id = %s", (workshop_id,))
    services = [row['service_name'] for row in cursor.fetchall()]
    workshop['services'] = services
    
    # Get workshop hours
    cursor.execute("SELECT day, open_time, close_time FROM workshop_hours WHERE workshop_id = %s", (workshop_id,))
    hours = {}
    for row in cursor.fetchall():
        hours[row['day']] = f"{row['open_time']} - {row['close_time']}"
    workshop['hours'] = hours
    
    # Get workshop pricing
    cursor.execute("SELECT service_name, price FROM workshop_pricing WHERE workshop_id = %s", (workshop_id,))
    pricing = {row['service_name']: row['price'] for row in cursor.fetchall()}
    workshop['pricing'] = pricing
    
    # Calculate distance if user location is available
    cursor.execute("SELECT latitude, longitude FROM users WHERE id = %s", (user_id,))
    user_location = cursor.fetchone()
    
    if user_location and user_location['latitude'] and user_location['longitude']:
        cursor.execute("""
            SELECT (6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude)))) as distance 
            FROM workshops WHERE id = %s
        """, (user_location['latitude'], user_location['longitude'], user_location['latitude'], workshop_id))
        distance_result = cursor.fetchone()
        workshop['distance'] = round(distance_result['distance'], 1) if distance_result['distance'] else None
    else:
        workshop['distance'] = None
    
    # Get reviews
    cursor.execute("""
        SELECT r.*, u.name as user_name 
        FROM reviews r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.workshop_id = %s 
        ORDER BY r.created_at DESC
    """, (workshop_id,))
    reviews = cursor.fetchall()
    
    # Check if user can review (has completed a service with this workshop)
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM service_requests 
        WHERE user_id = %s AND workshop_id = %s AND status = 'completed'
    """, (user_id, workshop_id))
    can_review = cursor.fetchone()['count'] > 0
    
    cursor.close()
    conn.close()
    
    return render_template('workshop_detail.html', workshop=workshop, reviews=reviews, can_review=can_review)

@app.route('/workshops/<int:workshop_id>/request', methods=['GET', 'POST'])
@login_required
def request_service(workshop_id):
    user_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get workshop details
    cursor.execute("SELECT * FROM workshops WHERE id = %s", (workshop_id,))
    workshop = cursor.fetchone()
    
    if not workshop:
        cursor.close()
        conn.close()
        return "Workshop not found", 404
    
    if request.method == 'POST':
        # Process service request
        vehicle_type = request.form['vehicle_type']
        vehicle_model = request.form['vehicle_model']
        service_type = request.form['service_type']
        custom_service = request.form.get('custom_service', '')
        problem_description = request.form['problem_description']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        address = request.form['address']
        urgency = request.form['urgency']
        
        # Use custom service if provided
        if service_type == 'other' and custom_service:
            service_type = custom_service
        
        # Save service request
        cursor.execute("""
            INSERT INTO service_requests 
            (user_id, workshop_id, vehicle_type, vehicle_model, service_type, problem_description, latitude, longitude, address, urgency, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
        """, (user_id, workshop_id, vehicle_type, vehicle_model, service_type, problem_description, latitude, longitude, address, urgency))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('request_confirmation', request_id=cursor.lastrowid))
    
    # Get workshop services for dropdown
    cursor.execute("SELECT service_name FROM workshop_services WHERE workshop_id = %s", (workshop_id,))
    services = [row['service_name'] for row in cursor.fetchall()]
    
    # Get workshop pricing
    cursor.execute("SELECT service_name, price FROM workshop_pricing WHERE workshop_id = %s", (workshop_id,))
    pricing = {row['service_name']: row['price'] for row in cursor.fetchall()}
    
    cursor.close()
    conn.close()
    
    return render_template('service_request.html', workshop=workshop, services=services, pricing=pricing)

@app.route('/requests')
@login_required
def my_requests():
    user_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all requests for the user
    cursor.execute("""
        SELECT sr.*, w.name as workshop_name, w.phone as workshop_phone
        FROM service_requests sr
        JOIN workshops w ON sr.workshop_id = w.id
        WHERE sr.user_id = %s
        ORDER BY sr.created_at DESC
    """, (user_id,))
    requests = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('my_requests.html', requests=requests)

@app.route('/requests/<int:request_id>')
@login_required
def request_detail(request_id):
    user_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get request details
    cursor.execute("""
        SELECT sr.*, w.name as workshop_name, w.phone as workshop_phone, w.address as workshop_address,
               u.name as mechanic_name, u.phone as mechanic_phone
        FROM service_requests sr
        JOIN workshops w ON sr.workshop_id = w.id
        LEFT JOIN users u ON sr.mechanic_id = u.id
        WHERE sr.id = %s AND sr.user_id = %s
    """, (request_id, user_id))
    
    service_request = cursor.fetchone()
    
    if not service_request:
        cursor.close()
        conn.close()
        return "Request not found", 404
    
    cursor.close()
    conn.close()
    
    return render_template('request_detail.html', request=service_request)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)