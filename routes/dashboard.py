# ============================================
# routes/dashboard.py - Dashboard Stats Route
# ============================================

from flask import Blueprint, jsonify
from database import get_connection
from routes.auth import token_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/stats', methods=['GET'])
@token_required
def get_stats():
    """Return summary stats for the dashboard."""
    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total FROM Student")
        total_students = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) AS total FROM Room")
        total_rooms = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) AS total FROM Hostel")
        total_hostels = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) AS total FROM Visitors")
        total_visitors = cursor.fetchone()['total']

        # Recent visitors (last 5)
        cursor.execute("""
            SELECT v.visitor_name, v.visit_date, v.in_time, v.out_time,
                   CONCAT(s.fname,' ',s.lname) AS student_name
            FROM Visitors v
            LEFT JOIN Student s ON v.student_id = s.student_id
            ORDER BY v.visit_date DESC, v.in_time DESC
            LIMIT 5
        """)
        recent_visitors = cursor.fetchall()
        for v in recent_visitors:
            v['in_time'] = str(v['in_time'])
            if v['out_time']:
                v['out_time'] = str(v['out_time'])
            v['visit_date'] = str(v['visit_date'])

        return jsonify({
            "total_students": total_students,
            "total_rooms": total_rooms,
            "total_hostels": total_hostels,
            "total_visitors": total_visitors,
            "recent_visitors": recent_visitors
        }), 200
    finally:
        cursor.close()
        conn.close()
