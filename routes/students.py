# ============================================
# routes/students.py - Student Management Routes
# ============================================

from flask import Blueprint, request, jsonify
from database import get_connection
from routes.auth import token_required

students_bp = Blueprint('students', __name__)


@students_bp.route('/', methods=['GET'])
@token_required
def get_students():
    """Get all students with optional search and filter."""
    search = request.args.get('search', '')
    dept = request.args.get('dept', '')
    hostel_id = request.args.get('hostel_id', '')

    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT s.*, h.hostel_name
            FROM Student s
            LEFT JOIN Hostel h ON s.hostel_id = h.hostel_id
            WHERE 1=1
        """
        params = []

        if search:
            query += " AND (s.fname LIKE %s OR s.lname LIKE %s OR s.mob_no LIKE %s)"
            like = f"%{search}%"
            params.extend([like, like, like])

        if dept:
            query += " AND s.dept = %s"
            params.append(dept)

        if hostel_id:
            query += " AND s.hostel_id = %s"
            params.append(hostel_id)

        query += " ORDER BY s.student_id DESC"
        cursor.execute(query, params)
        students = cursor.fetchall()
        return jsonify(students), 200
    finally:
        cursor.close()
        conn.close()


@students_bp.route('/<int:student_id>', methods=['GET'])
@token_required
def get_student(student_id):
    """Get a single student by ID."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT s.*, h.hostel_name FROM Student s LEFT JOIN Hostel h ON s.hostel_id = h.hostel_id WHERE s.student_id = %s",
            (student_id,)
        )
        student = cursor.fetchone()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        return jsonify(student), 200
    finally:
        cursor.close()
        conn.close()


@students_bp.route('/', methods=['POST'])
@token_required
def add_student():
    """Add a new student."""
    data = request.get_json()
    fname = data.get('fname', '').strip()
    lname = data.get('lname', '').strip()
    mob_no = data.get('mob_no', '').strip()
    dept = data.get('dept', '').strip()
    year_of_study = data.get('year_of_study')
    hostel_id = data.get('hostel_id')

    if not all([fname, lname, mob_no, dept, year_of_study]):
        return jsonify({"error": "All fields are required"}), 400

    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Student (fname, lname, mob_no, dept, year_of_study, hostel_id) VALUES (%s,%s,%s,%s,%s,%s)",
            (fname, lname, mob_no, dept, year_of_study, hostel_id or None)
        )
        conn.commit()

        # Update hostel student count
        if hostel_id:
            cursor.execute(
                "UPDATE Hostel SET no_of_students = (SELECT COUNT(*) FROM Student WHERE hostel_id = %s) WHERE hostel_id = %s",
                (hostel_id, hostel_id)
            )
            conn.commit()

        return jsonify({"message": "Student added successfully", "student_id": cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@students_bp.route('/<int:student_id>', methods=['PUT'])
@token_required
def update_student(student_id):
    """Update student details."""
    data = request.get_json()
    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute(
            """UPDATE Student SET fname=%s, lname=%s, mob_no=%s, dept=%s, year_of_study=%s, hostel_id=%s
               WHERE student_id=%s""",
            (data.get('fname'), data.get('lname'), data.get('mob_no'),
             data.get('dept'), data.get('year_of_study'), data.get('hostel_id'), student_id)
        )
        conn.commit()

        # Recalculate hostel counts
        hostel_id = data.get('hostel_id')
        if hostel_id:
            cursor.execute(
                "UPDATE Hostel SET no_of_students = (SELECT COUNT(*) FROM Student WHERE hostel_id = %s) WHERE hostel_id = %s",
                (hostel_id, hostel_id)
            )
            conn.commit()

        return jsonify({"message": "Student updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@students_bp.route('/<int:student_id>', methods=['DELETE'])
@token_required
def delete_student(student_id):
    """Delete a student by ID."""
    conn = get_connection()
    if not conn:
        return jsonify({"error": "DB connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Get hostel_id before deleting
        cursor.execute("SELECT hostel_id FROM Student WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()

        cursor.execute("DELETE FROM Student WHERE student_id = %s", (student_id,))
        conn.commit()

        # Update hostel count
        if student and student['hostel_id']:
            hid = student['hostel_id']
            cursor.execute(
                "UPDATE Hostel SET no_of_students = (SELECT COUNT(*) FROM Student WHERE hostel_id = %s) WHERE hostel_id = %s",
                (hid, hid)
            )
            conn.commit()

        return jsonify({"message": "Student deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
