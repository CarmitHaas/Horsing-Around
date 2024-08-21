from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import time
from pymongo.errors import ServerSelectionTimeoutError
from prometheus_client import generate_latest, REGISTRY, Counter, Histogram, Gauge

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')

# Prometheus metrics
REQUEST_COUNT = Counter('request_count', 'App Request Count', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency', ['endpoint'])

# Custom metrics
TOTAL_HORSES = Gauge('total_horses', 'Total number of horses')
TOTAL_CHORES = Gauge('total_chores', 'Total number of chores')
COMPLETED_CHORES = Gauge('completed_chores', 'Number of completed chores')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.before_request
def clear_session():
    if 'first_request' not in session:
        logout_user()
        session.clear()
        session['first_request'] = True

@app.after_request
def after_request(response):
    request_latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(request.endpoint).observe(request_latency)
    REQUEST_COUNT.labels(request.method, request.endpoint, response.status_code).inc()
    return response

# MongoDB connection with retry logic
def connect_to_mongo(max_retries=5, delay=5):
    for attempt in range(max_retries):
        try:
            client = MongoClient(os.environ.get('MONGO_URI', 'mongodb://localhost:27017/'), serverSelectionTimeoutMS=5000)
            client.server_info()  # This will raise an exception if it can't connect
            return client
        except ServerSelectionTimeoutError:
            if attempt < max_retries - 1:
                print(f"Couldn't connect to MongoDB. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise

client = connect_to_mongo()
db = client['horsing_around']
horses_collection = db['horses']
chores_collection = db['chores']
users_collection = db['users']
logs_collection = db['logs']

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, username):
        self.username = username

    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(username):
    user = users_collection.find_one({'username': username})
    if not user:
        return None
    return User(username=user['username'])

def reset_checkboxes():
    horses_collection.update_many({}, {'$set': {'chores.$[].completed': False}})

# Scheduler to reset checkboxes at midnight
scheduler = BackgroundScheduler()
scheduler.add_job(func=reset_checkboxes, trigger="cron", hour=0)
scheduler.start()

def convert_objectid(data):
    if isinstance(data, list):
        for item in data:
            convert_objectid(item)
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
            elif isinstance(value, (list, dict)):
                convert_objectid(value)
    return data

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_template('admin_welcome.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            login_user(User(username=username))
            return redirect(url_for('index'))
        return 'Invalid username or password'
    return render_template('login.html')

@app.route('/admin_welcome')
@login_required
def admin_welcome():
    return render_template('admin_welcome.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('welcome'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/index')
def index():
    horses = list(horses_collection.find())
    chores = list(chores_collection.find())
    return render_template('index.html', horses=horses, chores=chores, is_admin=current_user.is_authenticated)

@app.route('/add_horse', methods=['POST'])
@login_required
def add_horse():
    horse_data = request.json
    result = horses_collection.insert_one(horse_data)
    return jsonify({'success': True, 'id': str(result.inserted_id)})

@app.route('/add_chore', methods=['POST'])
@login_required
def add_chore():
    chore_data = request.json
    assign_all = chore_data.pop('assign_all', False)
    horse_ids = chore_data.pop('horse_ids', [])
    chore_id = ObjectId()
    chore_data['_id'] = chore_id
    
    # Insert the chore into the chores collection
    chores_collection.insert_one(chore_data)
    
    # Prepare the chore data for insertion into horses
    horse_chore_data = {
        '_id': chore_id,
        'name': chore_data['name'],
        'category': chore_data['category'],
        'completed': False
    }
    
    if assign_all:
        # Assign to all horses
        horses_collection.update_many(
            {},
            {'$push': {'chores': horse_chore_data}}
        )
    else:
        # Assign to selected horses
        horses_collection.update_many(
            {'_id': {'$in': [ObjectId(horse_id) for horse_id in horse_ids]}},
            {'$push': {'chores': horse_chore_data}}
        )
    
    return jsonify({'success': True, 'id': str(chore_id), 'chore': convert_objectid(horse_chore_data)})

@app.route('/remove_chore', methods=['POST'])
@login_required
def remove_chore():
    horse_id = request.json['horse_id']
    chore_id = request.json['chore_id']
    horses_collection.update_one(
        {'_id': ObjectId(horse_id)},
        {'$pull': {'chores': {'_id': ObjectId(chore_id)}}}
    )
    return jsonify({'success': True})

@app.route('/update_chore', methods=['POST'])
def update_chore():
    horse_id = request.json['horse_id']
    chore_id = request.json['chore_id']
    completed = request.json['completed']
    
    horse = horses_collection.find_one({'_id': ObjectId(horse_id)})
    chore = next((c for c in horse['chores'] if c['_id'] == ObjectId(chore_id)), None)
    
    if horse and chore:
        horses_collection.update_one(
            {'_id': ObjectId(horse_id), 'chores._id': ObjectId(chore_id)},
            {'$set': {'chores.$.completed': completed}}
        )
        
        # Add log entry
        log_entry = {
            'horse_name': horse['name'],
            'chore_name': chore['name'],
            'completed': completed,
            'timestamp': datetime.now()
        }
        logs_collection.insert_one(log_entry)
        
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Horse or chore not found'}), 404


@app.route('/remove_horse', methods=['POST'])
@login_required
def remove_horse():
    data = request.get_json()
    horse_id = data.get('horse_id')
    
    if not horse_id:
        return jsonify({'success': False, 'message': 'Horse ID not provided'}), 400
    
    result = db.horses.delete_one({'_id': ObjectId(horse_id)})
    
    if result.deleted_count == 1:
        return jsonify({'success': True, 'message': 'Horse deleted successfully'}), 200
    else:
        return jsonify({'success': False, 'message': 'Horse not found'}), 404

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    new_password = request.json['new_password']
    users_collection.update_one(
        {'username': current_user.username},
        {'$set': {'password': generate_password_hash(new_password)}}
    )
    return jsonify({'success': True})

@app.route('/edit_chore', methods=['POST'])
@login_required
def edit_chore():
    data = request.json
    horse_id = data['horse_id']
    chore_id = data['chore_id']
    updated_data = data['updated_data']
    
    result = horses_collection.update_one(
        {'_id': ObjectId(horse_id), 'chores._id': ObjectId(chore_id)},
        {'$set': {
            'chores.$.name': updated_data['name'],
            'chores.$.category': updated_data['category']
        }}
    )
    
    if result.modified_count > 0:
        return jsonify({'success': True, 'message': 'Chore updated successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to update chore'}), 400

@app.route('/delete_chore', methods=['POST'])
@login_required
def delete_chore():
    chore_id = request.json['chore_id']
    chores_collection.delete_one({'_id': ObjectId(chore_id)})
    return jsonify({'success': True})

@app.route('/horses', methods=['GET'])
def get_horses():
    horses = list(horses_collection.find({}, {'_id': 1}))
    return jsonify([str(horse['_id']) for horse in horses])

@app.route('/get_horse/<horse_id>', methods=['GET'])
@login_required
def get_horse(horse_id):
    horse = horses_collection.find_one({'_id': ObjectId(horse_id)})
    if horse:
        return jsonify(convert_objectid(horse))
    return jsonify({'error': 'Horse not found'}), 404


@app.route('/edit_horse/<horse_id>', methods=['POST'])
@login_required
def edit_horse(horse_id):
    horse_data = request.json
    horses_collection.update_one({'_id': ObjectId(horse_id)}, {'$set': horse_data})
    if horse_data:
        horse_data = convert_objectid(horse_data)
    return jsonify({'success': True})

@app.route('/get_logs', methods=['GET'])
@login_required
def get_logs():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = {}
    if start_date and end_date:
        query['timestamp'] = {
            '$gte': datetime.strptime(start_date, '%Y-%m-%d'),
            '$lte': datetime.strptime(end_date, '%Y-%m-%d')
        }
    
    logs = list(logs_collection.find(query).sort('timestamp', -1).limit(50))
    
    return jsonify([{
        'horse_name': log.get('horse_name', 'Unknown'),
        'chore_name': log.get('chore_name', 'Unknown'),
        'completed': log.get('completed', False),
        'timestamp': log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    } for log in logs])

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/metrics')
def metrics():
    # Update custom metrics
    TOTAL_HORSES.set(horses_collection.count_documents({}))
    TOTAL_CHORES.set(sum(len(horse.get('chores', [])) for horse in horses_collection.find()))
    COMPLETED_CHORES.set(sum(
        sum(1 for chore in horse.get('chores', []) if chore.get('completed', False))
        for horse in horses_collection.find()
    ))

    # Generate and return all metrics
    return generate_latest(REGISTRY)

if __name__ == '__main__':
    # Create default admin user if not exists
    if not users_collection.find_one({'username': 'admin'}):
        users_collection.insert_one({
            'username': 'admin',
            'password': generate_password_hash('admin')
        })
    app.run(host='0.0.0.0', debug=True)
    
    
    
