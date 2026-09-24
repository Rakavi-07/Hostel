# ============================================
# routes/furniture.py - Furniture Management Routes
# ============================================

from flask import Blueprint, request, jsonify
from database import get_connection
from routes.auth import token_required

furniture_bp = Blueprint('furniture', __name__)


@furniture_bp.route('/', methods=['GET'])
@token_required
def get_furniture():
    """Get all furniture with room and hostel info."""
    room_id = request.args.get('room_id', '')
    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT f.*, r.room_no, h.hostel_name
            FROM Furniture f
            LEFT JOIN Room r ON f.room_id = r.room_id
            LEFT JOIN Hostel h ON r.hostel_id = h.hostel_id
            WHERE 1=1
        """
        params = []
        if room_id:
            query += " AND f.room_id = %s"
            params.append(room_id)
        query += " ORDER BY f.furniture_id DESC"

        cursor.execute(query, params)
        return jsonify(cursor.fetchall()), 200
    finally:
        cursor.close()
        conn.close()


@furniture_bp.route('/', methods=['POST'])
@token_required
def add_furniture():
    """Add furniture and assign it to a room."""
    data = request.get_json()
    furniture_type = data.get('furniture_type', '').strip()
    room_id = data.get('room_id')

    if not furniture_type or not room_id:
        return jsonify({"error": "Furniture type and room are required"}), 400

    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Furniture (furniture_type, room_id) VALUES (%s, %s)",
            (furniture_type, room_id)
        )
        conn.commit()
        return jsonify({"message": "Furniture added", "furniture_id": cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@furniture_bp.route('/<int:furniture_id>', methods=['DELETE'])
@token_required
def delete_furniture(furniture_id):
    """Delete a furniture item."""
    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Furniture WHERE furniture_id = %s", (furniture_id,))
        conn.commit()
        return jsonify({"message": "Furniture deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
