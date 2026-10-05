import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()  # reads values from the .env file


def get_connection():
    """Create and return a new MySQL connection using environment variables."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "student_management"),
    )


def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """
    Run one SQL query safely and return the result.
    - params are always passed separately (parameterized) to prevent SQL injection.
    - Returns: a row, a list of rows, the new row id (for INSERT), or the affected row count.
    """
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if commit:
            connection.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        if fetch_one:
            return cursor.fetchone()
        if fetch_all:
            return cursor.fetchall()
        return None
    finally:
        # Always close, even if an error occurred
        cursor.close()
        connection.close()
