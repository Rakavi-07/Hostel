# ============================================
# routes/visitors.py - Visitor Management Routes
# ============================================

from flask import Blueprint, request, jsonify
from database import get_connection
from routes.auth import token_required

visitors_bp = Blueprint('visitors', __name__)


@visitors_bp.route('/', methods=['GET'])
@token_required
def get_visitors():
    """Get all visitor entries with linked student info."""
    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT v.*, CONCAT(s.fname,' ',s.lname) AS student_name
            FROM Visitors v
            LEFT JOIN Student s ON v.student_id = s.student_id
            ORDER BY v.visit_date DESC, v.in_time DESC
        """)
        visitors = cursor.fetchall()
        # Convert time objects to strings for JSON serialization
        for v in visitors:
            if v.get('in_time'):
                v['in_time'] = str(v['in_time'])
            if v.get('out_time'):
                v['out_time'] = str(v['out_time'])
            if v.get('visit_date'):
                v['visit_date'] = str(v['visit_date'])
        return jsonify(visitors), 200
    finally:
        cursor.close()
        conn.close()


@visitors_bp.route('/', methods=['POST'])
@token_required
def add_visitor():
    """Add a new visitor entry."""
    data = request.get_json()
    visitor_name = data.get('visitor_name', '').strip()
    visit_date = data.get('visit_date', '').strip()
    in_time = data.get('in_time', '').strip()
    out_time = data.get('out_time', '').strip() or None
    student_id = data.get('student_id')

    if not all([visitor_name, visit_date, in_time, student_id]):
        return jsonify({"error": "Name, date, in_time, and student are required"}), 400

    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Visitors (visitor_name, visit_date, in_time, out_time, student_id) VALUES (%s,%s,%s,%s,%s)",
            (visitor_name, visit_date, in_time, out_time, student_id)
        )
        conn.commit()
        return jsonify({"message": "Visitor added", "visitor_id": cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@visitors_bp.route('/<int:visitor_id>', methods=['PUT'])
@token_required
def update_visitor(visitor_id):
    """Update visitor out_time."""
    data = request.get_json()
    out_time = data.get('out_time', '').strip()

    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE Visitors SET out_time = %s WHERE visitor_id = %s",
            (out_time or None, visitor_id)
        )
        conn.commit()
        return jsonify({"message": "Visitor updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@visitors_bp.route('/<int:visitor_id>', methods=['DELETE'])
@token_required
def delete_visitor(visitor_id):
    """Delete a visitor entry."""
    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Visitors WHERE visitor_id = %s", (visitor_id,))
        conn.commit()
        return jsonify({"message": "Visitor deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
