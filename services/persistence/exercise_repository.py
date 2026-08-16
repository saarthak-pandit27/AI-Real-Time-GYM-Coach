import sqlite3
import streamlit as st
from pathlib import Path
from services.auth.security import generate_salt, hash_password, verify_password

_DB_PATH = str(Path(__file__).parent.parent.parent / "data.db")



@st.cache_resource
def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _get_connection()

    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                salt          TEXT,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # Ensure password_hash and salt columns exist if DB was created previously
        cursor = conn.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        if "password_hash" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
        if "salt" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN salt TEXT")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS exercises (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL REFERENCES users(id),
                exercise_name TEXT    NOT NULL,
                reps          INTEGER NOT NULL DEFAULT 0,
                sets          INTEGER NOT NULL DEFAULT 0,
                time          INTEGER NOT NULL DEFAULT 0,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def get_user(username: str) -> sqlite3.Row:
    conn = _get_connection()

    return conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()


def register_user(username: str, password: str):
    """Register a new user with hashed password. Returns (user, None) or (None, error_str)."""
    username = username.strip().lower()
    if not username:
        return None, "Username cannot be empty."
    if len(password) < 6:
        return None, "Password must be at least 6 characters long."
    
    existing = get_user(username)
    if existing is not None:
        return None, "Username is already taken. Please choose another or sign in."
    
    salt = generate_salt()
    pw_hash = hash_password(password, salt)
    
    conn = _get_connection()
    with conn:
        conn.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, pw_hash, salt)
        )

    user = get_user(username)
    return user, None


def authenticate_user(username: str, password: str):
    """Authenticate a user. Returns (user, None) or (None, error_str)."""
    username = username.strip().lower()
    if not username or not password:
        return None, "Please enter both username and password."
    
    user = get_user(username)
    if user is None:
        return None, "Account not found. Please check your username or register a new account."
    
    # Handle legacy accounts created without a password
    if not user['password_hash'] or not user['salt']:
        salt = generate_salt()
        pw_hash = hash_password(password, salt)
        conn = _get_connection()
        with conn:
            conn.execute(
                "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
                (pw_hash, salt, user['id'])
            )
        return user, None

    if verify_password(password, user['salt'], user['password_hash']):
        return user, None
    else:
        return None, "Invalid password. Please try again."


def get_or_create_user(username: str) -> sqlite3.Row:
    user = get_user(username)

    if user is None:
        salt = generate_salt()
        conn = _get_connection()
        with conn:
            conn.execute(
                "INSERT INTO users (username, salt) VALUES (?, ?)", (username, salt)
            )
        user = get_user(username)
    
    return user


def add_exercise(user_id, exercise_name, reps, sets, time):
    conn = _get_connection()

    with conn:
        existing = conn.execute("""
            SELECT * FROM exercises 
            WHERE user_id = ? AND exercise_name = ? AND Date(created_at) = Date('now')
        """, (user_id, exercise_name)).fetchone()

        if existing:
            conn.execute("""
                UPDATE exercises 
                SET reps = reps + ?, sets = sets + ?, time = time + ?
                WHERE id = ?
            """, (reps, sets, time, existing['id']))
        else:
            conn.execute("""
                INSERT INTO exercises (user_id, exercise_name, sets, reps, time)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, exercise_name, sets, reps, time))


def get_users_exercises(user_id):
    conn = _get_connection()

    return conn.execute("""
        SELECT * FROM exercises 
        WHERE user_id = ?
    """, (user_id,)).fetchall()