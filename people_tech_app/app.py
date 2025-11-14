# app.py
from flask import Flask
from flask_login import LoginManager
from models import db, User
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change_this_in_production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='adminpass', is_admin=True)
        db.session.add(admin)
        db.session.commit()

# Import routes
try:
    from routes import *
    print("Routes loaded successfully!")
except Exception as e:
    print(f"Failed to load routes: {e}")

if __name__ == '__main__':
    app.run(debug=True)