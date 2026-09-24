# ============================================
# routes/auth.py - Authentication Routes
# ============================================

from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from database import get_connection

auth_bp = Blueprint('auth', __name__)
SECRET_KEY = os.getenv("SECRET_KEY", "hostel_secret")

def generate_token(admin_id, username):
    """Generate a JWT token for a logged-in admin."""
    payload = {
        "id": admin_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=8)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    """Decode and verify a JWT token."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to protect routes with JWT authentication."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Token missing"}), 401
        data = verify_token(token)
        if not data:
            return jsonify({"error": "Invalid or expired token"}), 401
        request.admin = data
        return f(*args, **kwargs)
    return decorated


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new administrator account."""
    data = request.get_json()
    fname = data.get('fname', '').strip()
    lname = data.get('lname', '').strip()
    mob_no = data.get('mob_no', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not all([fname, lname, mob_no, username, password]):
        return jsonify({"error": "All fields are required"}), 400

    # Hash password with bcrypt
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Administrator (fname, lname, mob_no, username, password_hash) VALUES (%s, %s, %s, %s, %s)",
            (fname, lname, mob_no, username, hashed)
        )
        conn.commit()
        return jsonify({"message": "Admin registered successfully"}), 201
    except Exception as e:
        if "Duplicate entry" in str(e):
            return jsonify({"error": "Username already exists"}), 409
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with username and password, returns JWT token."""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    conn = get_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Administrator WHERE username = %s", (username,))
        admin = cursor.fetchone()

        if not admin:
            return jsonify({"error": "Invalid credentials"}), 401

        # Verify password with bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
            token = generate_token(admin['id'], admin['username'])
            return jsonify({
                "token": token,
                "admin": {
                    "id": admin['id'],
                    "name": f"{admin['fname']} {admin['lname']}",
                    "username": admin['username']
                }
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    finally:
        cursor.close()
        conn.close()
