from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import time
from pymongo.errors import ServerSelectionTimeoutError

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')

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
    horses_collection.update_many({}, {'$set': {'chores': {}}})

# Scheduler to reset checkboxes at midnight
scheduler = BackgroundScheduler()
scheduler.add_job(func=reset_checkboxes, trigger="cron", hour=0)
scheduler.start()

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            login_user(User(username=username))
            return redirect(url_for('index'))
        return 'Invalid username or password'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('welcome'))

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
    result = chores_collection.insert_one(chore_data)
    return jsonify({'success': True, 'id': str(result.inserted_id)})

@app.route('/update_chore', methods=['POST'])
def update_chore():
    chore_id = request.json['chore_id']
    horse_id = request.json['horse_id']
    completed = request.json['completed']

    horses_collection.update_one(
        {'_id': ObjectId(horse_id)},
        {'$set': {f'chores.{chore_id}': completed}}
    )
    return jsonify({'success': True})

@app.route('/remove_horse', methods=['POST'])
@login_required
def remove_horse():
    horse_id = request.json['horse_id']
    horses_collection.delete_one({'_id': ObjectId(horse_id)})
    return jsonify({'success': True})

@app.route('/remove_chore', methods=['POST'])
@login_required
def remove_chore():
    chore_id = request.json['chore_id']
    chores_collection.delete_one({'_id': ObjectId(chore_id)})
    return jsonify({'success': True})

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
    chore_id = request.json['chore_id']
    updated_data = request.json['updated_data']
    chores_collection.update_one({'_id': ObjectId(chore_id)}, {'$set': updated_data})
    return jsonify({'success': True})

@app.route('/delete_chore', methods=['POST'])
@login_required
def delete_chore():
    chore_id = request.json['chore_id']
    chores_collection.delete_one({'_id': ObjectId(chore_id)})
    return jsonify({'success': True})

@app.route('/get_horse/<horse_id>')
@login_required
def get_horse(horse_id):
    horse = horses_collection.find_one({'_id': ObjectId(horse_id)})
    return jsonify(horse)

@app.route('/edit_horse', methods=['POST'])
@login_required
def edit_horse():
    horse_id = request.json.get('horse_id')
    updated_data = request.json.get('updated_data')
    if not horse_id or not updated_data:
        return jsonify({'success': False, 'message': 'Missing horse_id or updated_data'}), 400

    horses_collection.update_one({'_id': ObjectId(horse_id)}, {'$set': updated_data})
    return jsonify({'success': True})

@app.route('/get_logs')
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
    
    logs = list(logs_collection.find(query).sort('timestamp', -1))
    return jsonify(logs)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
       # Create default admin user if not exists
       if not users_collection.find_one({'username': 'admin'}):
           users_collection.insert_one({
               'username': 'admin',
               'password': generate_password_hash('admin')
           })
       app.run(host='0.0.0.0', debug=True)
