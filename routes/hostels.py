# ============================================
# routes/hostels.py - Hostel Management Routes
# ============================================

from flask import Blueprint, request, jsonify
from database import get_connection
from routes.auth import token_required

hostels_bp = Blueprint('hostels', __name__)


@hostels_bp.route('/', methods=['GET'])
@token_required
def get_hostels():
    """Get all hostels with admin details."""
    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT h.*, CONCAT(a.fname,' ',a.lname) AS admin_name
            FROM Hostel h
            LEFT JOIN Administrator a ON h.admin_id = a.id
            ORDER BY h.hostel_id
        """)
        return jsonify(cursor.fetchall()), 200
    finally:
        cursor.close()
        conn.close()


@hostels_bp.route('/<int:hostel_id>', methods=['GET'])
@token_required
def get_hostel(hostel_id):
    """Get a single hostel by ID."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT h.*, CONCAT(a.fname,' ',a.lname) AS admin_name
            FROM Hostel h LEFT JOIN Administrator a ON h.admin_id = a.id
            WHERE h.hostel_id = %s
        """, (hostel_id,))
        hostel = cursor.fetchone()
        if not hostel:
            return jsonify({"error": "Hostel not found"}), 404
        return jsonify(hostel), 200
    finally:
        cursor.close()
        conn.close()


@hostels_bp.route('/', methods=['POST'])
@token_required
def add_hostel():
    """Add a new hostel."""
    data = request.get_json()
    name = data.get('hostel_name', '').strip()
    no_of_rooms = data.get('no_of_rooms', 0)
    admin_id = data.get('admin_id')

    if not name or not no_of_rooms:
        return jsonify({"error": "Hostel name and number of rooms are required"}), 400

    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Hostel (hostel_name, no_of_rooms, admin_id) VALUES (%s, %s, %s)",
            (name, no_of_rooms, admin_id or None)
        )
        conn.commit()
        return jsonify({"message": "Hostel added", "hostel_id": cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@hostels_bp.route('/<int:hostel_id>', methods=['PUT'])
@token_required
def update_hostel(hostel_id):
    """Update hostel details."""
    data = request.get_json()
    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE Hostel SET hostel_name=%s, no_of_rooms=%s, admin_id=%s WHERE hostel_id=%s",
            (data.get('hostel_name'), data.get('no_of_rooms'), data.get('admin_id'), hostel_id)
        )
        conn.commit()
        return jsonify({"message": "Hostel updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@hostels_bp.route('/<int:hostel_id>', methods=['DELETE'])
@token_required
def delete_hostel(hostel_id):
    """Delete a hostel."""
    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Hostel WHERE hostel_id = %s", (hostel_id,))
        conn.commit()
        return jsonify({"message": "Hostel deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
