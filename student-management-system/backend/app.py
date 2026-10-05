import re
from flask import Flask, jsonify, request
from flask_cors import CORS
from mysql.connector import Error as MySQLError, IntegrityError

from database import execute_query

app = Flask(__name__)
CORS(app)  # allows the frontend (different origin) to call this API

NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z .'-]*$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_PATTERN = re.compile(r"^[6-9]\d{9}$")  # Indian mobile: 10 digits starting with 6-9
VALID_GENDERS = {"Male", "Female", "Other"}

SELECT_COLUMNS = "id, name, email, phone, age, gender, course, address, created_at"


# ---------- Helpers ----------
def success(message=None, data=None, status=200):
    body = {"success": True}
    if message:
        body["message"] = message
    if data is not None:
        body["data"] = data
    return jsonify(body), status


def error(message, status=400, errors=None):
    body = {"success": False, "message": message}
    if errors:
        body["errors"] = errors  # field-wise errors, e.g. {"email": "Invalid"}
    return jsonify(body), status


def validate_student(data):
    """Validate input and return (cleaned_data, errors_dict)."""
    errors = {}
    cleaned = {}

    name = str(data.get("name", "")).strip()
    if not name:
        errors["name"] = "Name is required"
    elif len(name) < 3:
        errors["name"] = "Name must be at least 3 characters"
    elif len(name) > 100 or not NAME_PATTERN.match(name):
        errors["name"] = "Name can contain only letters and spaces"
    cleaned["name"] = name

    email = str(data.get("email", "")).strip().lower()
    if not email:
        errors["email"] = "Email is required"
    elif len(email) > 100 or not EMAIL_PATTERN.match(email):
        errors["email"] = "Please enter a valid email"
    cleaned["email"] = email

    phone = str(data.get("phone", "")).strip()
    if not phone:
        errors["phone"] = "Phone number is required"
    elif not PHONE_PATTERN.match(phone):
        errors["phone"] = "Phone number must contain 10 digits (starting with 6-9)"
    cleaned["phone"] = phone

    age_raw = data.get("age")
    try:
        if isinstance(age_raw, bool) or str(age_raw).strip() == "":
            raise ValueError
        age = int(str(age_raw).strip())
        if age < 16 or age > 100:
            errors["age"] = "Age must be between 16 and 100"
    except (ValueError, TypeError):
        age = None
        errors["age"] = "Age must be a whole number between 16 and 100"
    cleaned["age"] = age

    gender = str(data.get("gender", "")).strip()
    if not gender:
        errors["gender"] = "Gender is required"
    elif gender not in VALID_GENDERS:
        errors["gender"] = "Please select a valid gender"
    cleaned["gender"] = gender

    course = str(data.get("course", "")).strip()
    if not course:
        errors["course"] = "Course is required"
    elif len(course) > 100:
        errors["course"] = "Course must be 100 characters or fewer"
    cleaned["course"] = course

    address = str(data.get("address") or "").strip()
    if address and (len(address) < 5 or len(address) > 255):
        errors["address"] = "Address must be between 5 and 255 characters"
    cleaned["address"] = address or None

    return cleaned, errors


def email_exists(email, exclude_id=None):
    """Check whether an email is already used (optionally ignoring one student)."""
    if exclude_id:
        row = execute_query("SELECT id FROM students WHERE email = %s AND id != %s",
                            (email, exclude_id), fetch_one=True)
    else:
        row = execute_query("SELECT id FROM students WHERE email = %s", (email,), fetch_one=True)
    return row is not None


def get_student_or_none(student_id):
    return execute_query(f"SELECT {SELECT_COLUMNS} FROM students WHERE id = %s",
                         (student_id,), fetch_one=True)


def serialize(student):
    """Convert datetime to string so it can be turned into JSON."""
    if student and student.get("created_at"):
        student["created_at"] = student["created_at"].strftime("%Y-%m-%d %H:%M:%S")
    return student


def get_json_body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


# ---------- Routes ----------
@app.route("/api/students", methods=["POST"])
def create_student():
    data = get_json_body()
    if data is None:
        return error("Request body must be valid JSON")

    cleaned, errors = validate_student(data)
    if errors:
        return error("Validation failed", 400, errors)

    if email_exists(cleaned["email"]):
        return error("Email already exists", 409, {"email": "Email already exists"})

    try:
        new_id = execute_query(
            "INSERT INTO students (name, email, phone, age, gender, course, address) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (cleaned["name"], cleaned["email"], cleaned["phone"], cleaned["age"],
             cleaned["gender"], cleaned["course"], cleaned["address"]),
            commit=True,
        )
        return success("Student created successfully", serialize(get_student_or_none(new_id)), 201)
    except IntegrityError:  # race condition safety net for the UNIQUE email
        return error("Email already exists", 409, {"email": "Email already exists"})


@app.route("/api/students", methods=["GET"])
def get_students():
    students = execute_query(f"SELECT {SELECT_COLUMNS} FROM students ORDER BY id DESC", fetch_all=True)
    return success(data=[serialize(s) for s in students])


# NOTE: /search is a fixed path, so Flask matches it before /<int:student_id>
@app.route("/api/students/search", methods=["GET"])
def search_students():
    query_text = request.args.get("q", "").strip()
    if not query_text:
        return get_students()

    pattern = f"%{query_text}%"
    students = execute_query(
        f"SELECT {SELECT_COLUMNS} FROM students "
        "WHERE name LIKE %s OR email LIKE %s OR course LIKE %s OR phone LIKE %s "
        "ORDER BY id DESC",
        (pattern, pattern, pattern, pattern),
        fetch_all=True,
    )
    return success(data=[serialize(s) for s in students])


@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = get_student_or_none(student_id)
    if not student:
        return error("Student not found", 404)
    return success(data=serialize(student))


@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    if not get_student_or_none(student_id):
        return error("Student not found", 404)

    data = get_json_body()
    if data is None:
        return error("Request body must be valid JSON")

    cleaned, errors = validate_student(data)
    if errors:
        return error("Validation failed", 400, errors)

    if email_exists(cleaned["email"], exclude_id=student_id):
        return error("Email already exists", 409, {"email": "Email already exists"})

    try:
        execute_query(
            "UPDATE students SET name=%s, email=%s, phone=%s, age=%s, gender=%s, "
            "course=%s, address=%s WHERE id=%s",
            (cleaned["name"], cleaned["email"], cleaned["phone"], cleaned["age"],
             cleaned["gender"], cleaned["course"], cleaned["address"], student_id),
            commit=True,
        )
        return success("Student updated successfully", serialize(get_student_or_none(student_id)))
    except IntegrityError:
        return error("Email already exists", 409, {"email": "Email already exists"})


@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    if not get_student_or_none(student_id):
        return error("Student not found", 404)
    execute_query("DELETE FROM students WHERE id = %s", (student_id,), commit=True)
    return success("Student deleted successfully")


# ---------- Error handlers ----------
@app.errorhandler(MySQLError)
def handle_database_error(exc):
    app.logger.error("Database error: %s", exc)
    return error("Database error. Please check the database connection.", 500)


@app.errorhandler(404)
def handle_not_found(_):
    # Also covers invalid IDs like /api/students/abc (int converter fails)
    return error("Resource not found or invalid ID", 404)


@app.errorhandler(405)
def handle_method_not_allowed(_):
    return error("Method not allowed", 405)


@app.errorhandler(Exception)
def handle_unexpected_error(exc):
    app.logger.error("Unexpected error: %s", exc)
    return error("Internal server error", 500)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
