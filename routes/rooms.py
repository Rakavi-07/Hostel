# ============================================
# routes/rooms.py - Room & Allocation Routes
# ============================================

from flask import Blueprint, request, jsonify
from database import get_connection
from routes.auth import token_required

rooms_bp = Blueprint('rooms', __name__)


@rooms_bp.route('/', methods=['GET'])
@token_required
def get_rooms():
    """Get all rooms with hostel name and occupancy info."""
    hostel_id = request.args.get('hostel_id', '')
    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT r.*, h.hostel_name,
                   COUNT(sa.stay_id) AS occupied
            FROM Room r
            LEFT JOIN Hostel h ON r.hostel_id = h.hostel_id
            LEFT JOIN Stay_At sa ON r.room_id = sa.room_id
            WHERE 1=1
        """
        params = []
        if hostel_id:
            query += " AND r.hostel_id = %s"
            params.append(hostel_id)
        query += " GROUP BY r.room_id ORDER BY r.room_id"

        cursor.execute(query, params)
        return jsonify(cursor.fetchall()), 200
    finally:
        cursor.close()
        conn.close()


@rooms_bp.route('/', methods=['POST'])
@token_required
def add_room():
    """Add a new room to a hostel."""
    data = request.get_json()
    room_no = data.get('room_no', '').strip()
    hostel_id = data.get('hostel_id')
    capacity = data.get('capacity', 2)

    if not room_no or not hostel_id:
        return jsonify({"error": "Room number and hostel are required"}), 400

    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Room (room_no, hostel_id, capacity) VALUES (%s, %s, %s)",
            (room_no, hostel_id, capacity)
        )
        conn.commit()

        # Update hostel room count
        cursor.execute(
            "UPDATE Hostel SET no_of_rooms = (SELECT COUNT(*) FROM Room WHERE hostel_id = %s) WHERE hostel_id = %s",
            (hostel_id, hostel_id)
        )
        conn.commit()

        return jsonify({"message": "Room added", "room_id": cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@rooms_bp.route('/<int:room_id>', methods=['DELETE'])
@token_required
def delete_room(room_id):
    """Delete a room."""
    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT hostel_id FROM Room WHERE room_id = %s", (room_id,))
        room = cursor.fetchone()

        cursor.execute("DELETE FROM Room WHERE room_id = %s", (room_id,))
        conn.commit()

        if room:
            cursor.execute(
                "UPDATE Hostel SET no_of_rooms = (SELECT COUNT(*) FROM Room WHERE hostel_id = %s) WHERE hostel_id = %s",
                (room['hostel_id'], room['hostel_id'])
            )
            conn.commit()

        return jsonify({"message": "Room deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ---- Room Allocations (Stay_At) ----

@rooms_bp.route('/allocations', methods=['GET'])
@token_required
def get_allocations():
    """Get all room allocations with student and room info."""
    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT sa.stay_id, sa.student_id, sa.room_id,
                   CONCAT(s.fname,' ',s.lname) AS student_name,
                   s.dept, r.room_no, h.hostel_name
            FROM Stay_At sa
            JOIN Student s ON sa.student_id = s.student_id
            JOIN Room r ON sa.room_id = r.room_id
            JOIN Hostel h ON r.hostel_id = h.hostel_id
            ORDER BY sa.stay_id DESC
        """)
        return jsonify(cursor.fetchall()), 200
    finally:
        cursor.close()
        conn.close()


@rooms_bp.route('/allocations', methods=['POST'])
@token_required
def allocate_room():
    """Assign a student to a room (prevents duplicates)."""
    data = request.get_json()
    student_id = data.get('student_id')
    room_id = data.get('room_id')

    if not student_id or not room_id:
        return jsonify({"error": "Student ID and Room ID are required"}), 400

    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Check if student is already allocated
        cursor.execute("SELECT * FROM Stay_At WHERE student_id = %s", (student_id,))
        if cursor.fetchone():
            return jsonify({"error": "Student is already allocated to a room"}), 409

        # Check room capacity
        cursor.execute("""
            SELECT r.capacity, COUNT(sa.stay_id) AS occupied
            FROM Room r LEFT JOIN Stay_At sa ON r.room_id = sa.room_id
            WHERE r.room_id = %s GROUP BY r.room_id
        """, (room_id,))
        room = cursor.fetchone()

        if not room:
            return jsonify({"error": "Room not found"}), 404

        if room['occupied'] >= room['capacity']:
            return jsonify({"error": "Room is at full capacity"}), 409

        cursor.execute("INSERT INTO Stay_At (student_id, room_id) VALUES (%s, %s)", (student_id, room_id))
        conn.commit()
        return jsonify({"message": "Room allocated successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@rooms_bp.route('/allocations/<int:stay_id>', methods=['DELETE'])
@token_required
def deallocate_room(stay_id):
    """Remove a room allocation."""
    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Stay_At WHERE stay_id = %s", (stay_id,))
        conn.commit()
        return jsonify({"message": "Allocation removed"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
