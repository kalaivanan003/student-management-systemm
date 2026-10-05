# Student Management System

A full-stack CRUD web application to manage student records, built with Flask, MySQL and vanilla JavaScript.

## Features
- Add, view, edit and delete students
- Frontend and backend validation with field-level error messages
- Live search by name, email, course or phone
- Dashboard cards (total, male, female, courses)
- Responsive UI with success/error notifications and loading state
- Consistent JSON API with proper HTTP status codes

## Technologies Used
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API)
- **Backend:** Python 3, Flask, Flask-CORS
- **Database:** MySQL, mysql-connector-python
- **Config:** python-dotenv

## Project Structure
```
student-management-system/
├── backend/
│   ├── app.py
│   ├── database.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── schema.sql
└── README.md
```

## Database Setup
1. Start MySQL.
2. Run the script: `mysql -u root -p < schema.sql`
   (creates the `student_management` database, the `students` table and 6 sample rows).

## Installation
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables
```bash
cp .env.example .env            # Windows: copy .env.example .env
```
Edit `.env` and set your real MySQL password in `DB_PASSWORD`.

## Run the Backend
```bash
cd backend
python app.py
```
The API runs at `http://127.0.0.1:5000`.

## Run the Frontend
```bash
cd frontend
python -m http.server 5500
```
Open `http://127.0.0.1:5500` in your browser.

## API Documentation
| Method | Endpoint | Description | Success code |
|--------|----------|-------------|--------------|
| POST | `/api/students` | Create student | 201 |
| GET | `/api/students` | List all students | 200 |
| GET | `/api/students/<id>` | Get one student | 200 |
| PUT | `/api/students/<id>` | Update student | 200 |
| DELETE | `/api/students/<id>` | Delete student | 200 |
| GET | `/api/students/search?q=value` | Search students | 200 |

**Error codes:** 400 (validation), 404 (not found), 409 (duplicate email), 500 (server/database error).

Success: `{"success": true, "message": "...", "data": {...}}`
Error: `{"success": false, "message": "...", "errors": {"field": "..."}}`

## Validation Details
| Field | Rules |
|-------|-------|
| Name | Required, min 3 chars, letters/spaces only |
| Email | Required, valid format, unique |
| Phone | Required, 10-digit Indian mobile (starts with 6-9) |
| Age | Required, integer, 16-100 |
| Gender | Required (Male/Female/Other) |
| Course | Required, max 100 chars |
| Address | Optional, 5-255 chars if provided |

## CRUD Explanation
- **Create:** form → `POST /api/students` → `INSERT`
- **Read:** page load → `GET /api/students` → `SELECT`
- **Update:** Edit button → `PUT /api/students/<id>` → `UPDATE`
- **Delete:** confirm → `DELETE /api/students/<id>` → `DELETE`

## Screenshots
_Add screenshots here (dashboard, add form, table, edit mode)._

## Future Improvements
- Pagination and sorting
- User authentication (admin login)
- Export to CSV/Excel
- Unit tests (pytest)
- Docker setup
