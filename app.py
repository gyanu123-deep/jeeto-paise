from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Session ke liye secret key
app.secret_key = "change-this-secret-key"


# ================= DATABASE =================

def init_db():
    conn = sqlite3.connect("event.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ================= HOME =================

@app.route("/")
def home():
    return render_template("login.html")


# ================= STUDENT REGISTRATION =================

@app.route("/register", methods=["POST"])
def register():

    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    if not name or not email or not password:
        return "Please fill all fields."

    hashed_password = generate_password_hash(password)

    conn = sqlite3.connect("event.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (name, email, password)
        VALUES (?, ?, ?)
    """, (name, email, hashed_password))

    conn.commit()
    conn.close()

    return """
    <h2>Registration Successful!</h2>
    <p>Your registration has been saved.</p>
    <a href="/">Go Back</a>
    """


# ================= ADMIN LOGIN =================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Apna admin username/password yahan set karo
        ADMIN_USERNAME = "admin"
        ADMIN_PASSWORD = "ChangeMe123!"

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect("/admin")

        return render_template(
            "admin_login.html",
            error="Invalid username or password"
        )

    return render_template("admin_login.html")


# ================= ADMIN DASHBOARD =================

@app.route("/admin")
def admin():

    # Login check
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    conn = sqlite3.connect("event.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, registered_at
        FROM users
        ORDER BY id DESC
    """)

    users = cursor.fetchall()

    conn.close()

    return render_template("admin.html", users=users)


# ================= ADMIN LOGOUT =================

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin_logged_in", None)

    return redirect("/admin/login")


# ================= START SERVER =================

if __name__ == "__main__":
    init_db()
    app.run(debug=True)