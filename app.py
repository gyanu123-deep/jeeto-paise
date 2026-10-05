from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash


app = Flask(__name__)

# ================= SECRET KEY =================

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


# ================= ROBOTS.TXT =================

@app.route("/robots.txt")
def robots():
    return """User-agent: *
Allow: /

Disallow: /admin
Disallow: /register

Sitemap: https://jeeto-paise.onrender.com/sitemap.xml
""", 200, {"Content-Type": "text/plain"}


# ================= SITEMAP =================

@app.route("/sitemap.xml")
def sitemap():
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

    <url>
        <loc>https://jeeto-paise.onrender.com/</loc>
    </url>

</urlset>
""", 200, {"Content-Type": "application/xml"}


# ================= STUDENT REGISTRATION =================

@app.route("/register", methods=["POST"])
def register():

    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    if not name or not email or not password:
        return "Please fill all fields."

    # Password ko hash karke database me save karna
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

        # Admin username/password
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

# Database initialize hoga
# Local aur Render dono par useful hai
init_db()


if __name__ == "__main__":
    app.run(debug=True)
