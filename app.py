# ============================================
# app.py - Main Flask Application Entry Point
# ============================================

from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Allow cross-origin requests from frontend

# ---- Register Blueprints (Modular Routes) ----
from routes.auth import auth_bp
from routes.students import students_bp
from routes.hostels import hostels_bp
from routes.rooms import rooms_bp
from routes.visitors import visitors_bp
from routes.furniture import furniture_bp
from routes.dashboard import dashboard_bp

app.register_blueprint(auth_bp,      url_prefix='/api/auth')
app.register_blueprint(students_bp,  url_prefix='/api/students')
app.register_blueprint(hostels_bp,   url_prefix='/api/hostels')
app.register_blueprint(rooms_bp,     url_prefix='/api/rooms')
app.register_blueprint(visitors_bp,  url_prefix='/api/visitors')
app.register_blueprint(furniture_bp, url_prefix='/api/furniture')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')


# ---- Serve Frontend ----
@app.route('/')
def index():
    return send_from_directory('templates', 'login.html')

@app.route('/<path:filename>')
def serve_template(filename):
    return send_from_directory('templates', filename)


if __name__ == '__main__':
    print("🏨 Hostel Management System running at http://localhost:5000")
    app.run(debug=True, port=5000)
