
from flask import Flask, request, redirect, url_for, session, flash, render_template_string
import mysql.connector
from functools import wraps
from datetime import date
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-key")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Navnath@4321")


# ---------------- DATABASE ----------------

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="employee"
    )


def fetch_all(sql, values=()):
    con = connect_db()
    cur = con.cursor()
    try:
        cur.execute(sql, values)
        return cur.fetchall()
    finally:
        cur.close()
        con.close()


def execute_query(sql, values=()):
    con = connect_db()
    cur = con.cursor()
    try:
        cur.execute(sql, values)
        con.commit()
        return cur.rowcount
    finally:
        cur.close()
        con.close()


# ---------------- ADMIN AUTH ----------------

def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return function(*args, **kwargs)
    return wrapper


# ---------------- HTML + CSS ----------------

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>{{ title }} | EmployeePro</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">

<style>

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    --bg: #080d1b;
    --panel: rgba(255,255,255,0.055);
    --border: rgba(255,255,255,0.10);
    --text: #f4f6ff;
    --muted: #929bb5;
    --purple: #8b5cf6;
    --blue: #3b82f6;
    --cyan: #22d3ee;
}

body {
    font-family: 'Inter', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    overflow-x: hidden;
}

body::before {
    content: "";
    position: fixed;
    width: 500px;
    height: 500px;
    background: #6936df;
    filter: blur(180px);
    opacity: .22;
    top: -200px;
    left: -150px;
    z-index: -1;
}

body::after {
    content: "";
    position: fixed;
    width: 450px;
    height: 450px;
    background: #087bbd;
    filter: blur(180px);
    opacity: .19;
    bottom: -200px;
    right: -100px;
    z-index: -1;
}

a {
    text-decoration: none;
    color: inherit;
}

button, input {
    font-family: inherit;
}

.layout {
    display: flex;
    min-height: 100vh;
}

.sidebar {
    width: 255px;
    padding: 30px 20px;
    background: rgba(14,20,39,.82);
    border-right: 1px solid var(--border);
    backdrop-filter: blur(25px);
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    z-index: 10;
}

.logo {
    font-size: 23px;
    font-weight: 800;
    margin-bottom: 45px;
    letter-spacing: -1px;
}

.logo span {
    color: #a78bfa;
}

.logo-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 39px;
    height: 39px;
    margin-right: 8px;
    border-radius: 12px;
    background: linear-gradient(135deg,#8b5cf6,#2563eb);
    box-shadow: 0 7px 25px #8b5cf655;
}

.nav-label {
    font-size: 10px;
    color: #707c9a;
    letter-spacing: 2px;
    margin: 25px 12px 12px;
}

.nav-link {
    display: flex;
    gap: 14px;
    align-items: center;
    padding: 14px;
    margin: 7px 0;
    border-radius: 12px;
    color: #9ba7c2;
    transition: .3s;
    font-size: 13px;
}

.nav-link:hover, .nav-link.active {
    color: white;
    background: linear-gradient(110deg,#7547e8,#3b65d5);
    box-shadow: 0 8px 25px #7547e844;
    transform: translateX(4px);
}

.nav-link i {
    width: 20px;
    font-size: 16px;
}

.sidebar-bottom {
    position: absolute;
    bottom: 25px;
    left: 20px;
    right: 20px;
}

.main {
    margin-left: 255px;
    width: calc(100% - 255px);
    padding: 30px 40px;
}

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 40px;
}

.topbar h2 {
    font-size: 24px;
}

.topbar p {
    color: var(--muted);
    font-size: 12px;
    margin-top: 7px;
}

.profile {
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 10px 15px;
}

.avatar {
    width: 38px;
    height: 38px;
    display: grid;
    place-items: center;
    background: linear-gradient(135deg,#8b5cf6,#2563eb);
    border-radius: 12px;
    font-weight: bold;
}

.profile small {
    color: var(--muted);
    font-size: 10px;
}

.card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 25px;
    backdrop-filter: blur(20px);
    box-shadow: 0 15px 45px #00000030;
    transition: transform .3s, box-shadow .3s;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 22px 50px #00000055;
}

.stats {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 20px;
    margin-bottom: 30px;
}

.stat-icon {
    width: 48px;
    height: 48px;
    display: grid;
    place-items: center;
    border-radius: 14px;
    font-size: 20px;
    margin-bottom: 20px;
}

.purple { background: #8b5cf633; color: #bba5ff; }
.blue { background: #3b82f633; color: #80b2ff; }
.cyan { background: #22d3ee22; color: #67e8f9; }

.stat-number {
    font-size: 30px;
    font-weight: 800;
    margin: 10px 0;
}

.muted {
    color: var(--muted);
    font-size: 12px;
}

.section-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 20px;
}

.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 9px;
    padding: 13px 19px;
    border: 0;
    border-radius: 11px;
    color: white;
    font-weight: 600;
    font-size: 12px;
    cursor: pointer;
    background: linear-gradient(120deg,#8b5cf6,#3b82f6);
    box-shadow: 0 8px 22px #684ce344;
    transition: .3s;
}

.btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 30px #684ce377;
}

.btn-secondary {
    background: var(--panel);
    border: 1px solid var(--border);
    box-shadow: none;
}

.btn-danger {
    background: linear-gradient(120deg,#ef4444,#be123c);
}

.actions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.form-card {
    max-width: 650px;
    margin: auto;
}

.form-group {
    margin: 20px 0;
}

label {
    display: block;
    color: #c1c9df;
    font-size: 12px;
    margin-bottom: 9px;
}

input {
    width: 100%;
    padding: 15px;
    border-radius: 11px;
    background: rgba(255,255,255,.045);
    border: 1px solid var(--border);
    color: white;
    outline: none;
    font-size: 13px;
    transition: .3s;
}

input:focus {
    border-color: var(--purple);
    box-shadow: 0 0 0 3px #8b5cf622;
}

input[type="date"] {
    color-scheme: dark;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 650px;
}

.table-wrap {
    overflow-x: auto;
}

th {
    text-align: left;
    padding: 16px;
    color: #929bb5;
    font-size: 11px;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border);
}

td {
    padding: 17px 16px;
    font-size: 12px;
    border-bottom: 1px solid #ffffff0d;
}

tr:hover td {
    background: #ffffff08;
}

.badge {
    padding: 6px 10px;
    border-radius: 20px;
    color: #67e8f9;
    background: #22d3ee17;
    font-size: 10px;
}

.flash {
    background: #8b5cf622;
    border: 1px solid #8b5cf655;
    color: #d5c6ff;
    padding: 14px;
    border-radius: 12px;
    margin-bottom: 20px;
    font-size: 13px;
}

.login-screen {
    min-height: 70vh;
    display: grid;
    place-items: center;
}

.login-card {
    width: 100%;
    max-width: 440px;
    padding: 40px;
    text-align: center;
}

.login-icon {
    width: 75px;
    height: 75px;
    border-radius: 23px;
    display: grid;
    place-items: center;
    margin: 0 auto 25px;
    background: linear-gradient(135deg,#8b5cf6,#2563eb);
    box-shadow: 0 15px 35px #8b5cf655;
    font-size: 27px;
}

.hero {
    min-height: 75vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.hero h1 {
    font-size: clamp(38px,6vw,68px);
    line-height: 1.12;
    letter-spacing: -3px;
    max-width: 800px;
}

.gradient-text {
    background: linear-gradient(100deg,#a78bfa,#60a5fa,#22d3ee);
    -webkit-background-clip: text;
    color: transparent;
}

.hero p {
    max-width: 550px;
    line-height: 1.8;
    color: var(--muted);
    margin: 25px 0;
    font-size: 14px;
}

.hero-buttons {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
    justify-content: center;
}

.employee-result {
    margin-top: 25px;
    line-height: 2.4;
}

.mobile-menu {
    display: none;
}

@media(max-width:850px) {
    .sidebar {
        width: 75px;
        padding: 20px 10px;
    }
    .logo {
        font-size: 0;
        text-align: center;
    }
    .logo-icon {
        margin: 0;
    }
    .nav-link {
        justify-content: center;
        font-size: 0;
        padding: 15px 5px;
    }
    .nav-link i {
        font-size: 18px;
    }
    .nav-label, .sidebar-bottom span {
        display: none;
    }
    .sidebar-bottom {
        left: 10px;
        right: 10px;
    }
    .main {
        margin-left: 75px;
        width: calc(100% - 75px);
        padding: 25px 18px;
    }
    .stats {
        grid-template-columns: 1fr;
    }
}

@media(max-width:500px) {
    .topbar {
        align-items: flex-start;
        gap: 12px;
    }
    .topbar h2 {
        font-size: 18px;
    }
    .profile {
        padding: 7px;
    }
    .profile small, .profile .username {
        display: none;
    }
    .hero h1 {
        letter-spacing: -1px;
    }
    .login-card {
        padding: 25px;
    }
}

</style>
</head>

<body>

{% if page == 'home' %}

<div class="main" style="width:100%;margin:0;">
    <div class="topbar">
        <div class="logo">
            <span class="logo-icon"><i class="fa-solid fa-cubes"></i></span>
            Employee<span>Pro</span>
        </div>
        <div class="actions">
            <a href="{{ url_for('admin_login') }}" class="btn btn-secondary">Admin Login</a>
            <a href="{{ url_for('employee_portal') }}" class="btn">Employee Portal</a>
        </div>
    </div>

    <div class="hero">
        <div class="badge">✦ SMART EMPLOYEE MANAGEMENT</div>
        <h1 style="margin-top:25px;">
            Manage your team<br>
            <span class="gradient-text">with intelligence.</span>
        </h1>
        <p>
            A modern employee management platform.
            Organize employee information, manage records,
            and access your workforce data in one place.
        </p>
        <div class="hero-buttons">
            <a href="{{ url_for('admin_login') }}" class="btn">
                <i class="fa-solid fa-rocket"></i> Get Started
            </a>
            <a href="{{ url_for('employee_portal') }}" class="btn btn-secondary">
                Employee Access
            </a>
        </div>
    </div>
</div>

{% elif page == 'login' %}

<div class="main" style="width:100%;margin:0;">
    <div class="login-screen">
        <div class="card login-card">
            <div class="login-icon"><i class="fa-solid fa-shield-halved"></i></div>
            <h2>Welcome Admin</h2>
            <p class="muted" style="margin:12px 0 25px;">
                Sign in to access your dashboard
            </p>

            {% for message in messages %}
            <div class="flash">{{ message }}</div>
            {% endfor %}

            <form method="POST">
                <div class="form-group">
                    <input type="password" name="password"
                           placeholder="Enter admin password" required>
                </div>
                <button class="btn" style="width:100%;">
                    Sign In <i class="fa-solid fa-arrow-right"></i>
                </button>
            </form>
            <p style="margin-top:25px;">
                <a class="muted" href="{{ url_for('home') }}">← Back to home</a>
            </p>
        </div>
    </div>
</div>

{% elif page == 'employee_portal' %}

<div class="main" style="width:100%;margin:0;">
    <div class="topbar">
        <div class="logo">
            <span class="logo-icon"><i class="fa-solid fa-cubes"></i></span>
            Employee<span>Pro</span>
        </div>
        <a href="{{ url_for('home') }}" class="btn btn-secondary">Home</a>
    </div>

    <div class="login-screen">
        <div class="card login-card">
            <div class="login-icon"><i class="fa-solid fa-user"></i></div>
            <h2>Employee Portal</h2>
            <p class="muted" style="margin:12px 0 25px;">
                Enter your employee ID to search your record
            </p>

            {% for message in messages %}
            <div class="flash">{{ message }}</div>
            {% endfor %}

            <form method="POST">
                <input type="number" name="emp_id"
                       placeholder="Employee ID" required>
                <button class="btn" style="width:100%;margin-top:15px;">
                    Search Employee
                </button>
            </form>

            {% if employee %}
            <div class="card employee-result">
                <h3>Employee Details</h3>
                <p><b>ID:</b> {{ employee[0] }}</p>
                <p><b>Name:</b> {{ employee[1] }}</p>
                <p><b>DOB:</b> {{ employee[2] }}</p>
                <p><b>Salary:</b> ₹{{ employee[3] }}</p>
            </div>
            {% endif %}
        </div>
    </div>
</div>

{% else %}

<div class="layout">

    <aside class="sidebar">
        <div class="logo">
            <span class="logo-icon"><i class="fa-solid fa-cubes"></i></span>
            Employee<span>Pro</span>
        </div>

        <div class="nav-label">MAIN MENU</div>

        <a href="{{ url_for('admin_dashboard') }}"
           class="nav-link {% if page == 'dashboard' %}active{% endif %}">
            <i class="fa-solid fa-chart-pie"></i> Dashboard
        </a>

        <a href="{{ url_for('add_employee') }}"
           class="nav-link {% if page == 'add' %}active{% endif %}">
            <i class="fa-solid fa-user-plus"></i> Add Employee
        </a>

        <a href="{{ url_for('view_employee') }}"
           class="nav-link {% if page == 'view' %}active{% endif %}">
            <i class="fa-solid fa-users"></i> Employees
        </a>

        <div class="nav-label">ACCOUNT</div>

        <a href="{{ url_for('logout') }}" class="nav-link">
            <i class="fa-solid fa-right-from-bracket"></i> Logout
        </a>

        <div class="sidebar-bottom">
            <div class="card" style="padding:15px;">
                <div class="muted">SYSTEM STATUS</div>
                <p style="color:#4ade80;font-size:12px;margin-top:10px;">
                    ● System Online
                </p>
            </div>
        </div>
    </aside>

    <main class="main">

        <div class="topbar">
            <div>
                <h2>{{ heading }}</h2>
                <p>Welcome back, Admin. Manage your workforce.</p>
            </div>
            <div class="profile">
                <div class="avatar">A</div>
                <div>
                    <div class="username">Administrator</div>
                    <small>Super Admin</small>
                </div>
            </div>
        </div>

        {% for message in messages %}
        <div class="flash">{{ message }}</div>
        {% endfor %}

        {% if page == 'dashboard' %}

        <div class="stats">
            <div class="card">
                <div class="stat-icon purple">
                    <i class="fa-solid fa-users"></i>
                </div>
                <div class="muted">TOTAL EMPLOYEES</div>
                <div class="stat-number">{{ total }}</div>
                <div class="muted">Registered employees</div>
            </div>

            <div class="card">
                <div class="stat-icon blue">
                    <i class="fa-solid fa-wallet"></i>
                </div>
                <div class="muted">TOTAL PAYROLL</div>
                <div class="stat-number">₹{{ payroll }}</div>
                <div class="muted">Combined employee salary</div>
            </div>

            <div class="card">
                <div class="stat-icon cyan">
                    <i class="fa-solid fa-user-shield"></i>
                </div>
                <div class="muted">ADMIN STATUS</div>
                <div class="stat-number" style="font-size:22px;">Active</div>
                <div class="muted">Administrator logged in</div>
            </div>
        </div>

        <div class="card">
            <div class="section-title">Quick Actions</div>
            <div class="actions">
                <a href="{{ url_for('add_employee') }}" class="btn">
                    <i class="fa-solid fa-plus"></i> Add Employee
                </a>
                <a href="{{ url_for('view_employee') }}" class="btn btn-secondary">
                    <i class="fa-solid fa-table"></i> View Employees
                </a>
            </div>
        </div>

        {% elif page == 'add' %}

        <div class="card form-card">
            <div class="section-title">Create New Employee</div>

            <form method="POST">
                <div class="form-group">
                    <label>Employee ID</label>
                    <input type="number" name="emp_id" required>
                </div>

                <div class="form-group">
                    <label>Employee Name</label>
                    <input type="text" name="name" required maxlength="100">
                </div>

                <div class="form-group">
                    <label>Date of Birth</label>
                    <input type="date" name="dob" required max="{{ today }}">
                </div>

                <div class="form-group">
                    <label>Monthly Salary (₹)</label>
                    <input type="number" name="salary" min="0" required>
                </div>

                <div class="actions">
                    <button class="btn">
                        <i class="fa-solid fa-plus"></i> Add Employee
                    </button>
                    <a href="{{ url_for('admin_dashboard') }}"
                       class="btn btn-secondary">Cancel</a>
                </div>
            </form>
        </div>

        {% elif page == 'view' %}

        <div class="card">
            <div class="topbar" style="margin-bottom:20px;">
                <div>
                    <div class="section-title">Employee Directory</div>
                    <p class="muted">{{ employees|length }} employee records</p>
                </div>
                <a href="{{ url_for('add_employee') }}" class="btn">
                    <i class="fa-solid fa-plus"></i> Add New
                </a>
            </div>

            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Employee Name</th>
                            <th>Date of Birth</th>
                            <th>Salary</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                    {% for emp in employees %}
                        <tr>
                            <td>#{{ emp[0] }}</td>
                            <td>{{ emp[1] }}</td>
                            <td>{{ emp[2] }}</td>
                            <td>₹{{ emp[3] }}</td>
                            <td>
                                <div class="actions">
                                    <a class="btn btn-secondary"
                                       href="{{ url_for('update_employee', emp_id=emp[0]) }}">
                                        <i class="fa-solid fa-pen"></i>
                                    </a>
                                    <form method="POST"
                                          action="{{ url_for('delete_employee', emp_id=emp[0]) }}"
                                          onsubmit="return confirm('Delete this employee?')">
                                        <button class="btn btn-danger" type="submit">
                                            <i class="fa-solid fa-trash"></i>
                                        </button>
                                    </form>
                                </div>
                            </td>
                        </tr>
                    {% else %}
                        <tr>
                            <td colspan="5">No employees found.</td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        {% elif page == 'update' %}

        <div class="card form-card">
            <div class="section-title">Update Employee #{{ employee[0] }}</div>

            <form method="POST">
                <div class="form-group">
                    <label>Employee ID</label>
                    <input type="text" value="{{ employee[0] }}" disabled>
                </div>

                <div class="form-group">
                    <label>Employee Name</label>
                    <input type="text" name="name"
                           value="{{ employee[1] }}" required maxlength="100">
                </div>

                <div class="form-group">
                    <label>Date of Birth</label>
                    <input type="date" name="dob"
                           value="{{ employee[2] }}" required max="{{ today }}">
                </div>

                <div class="form-group">
                    <label>Salary</label>
                    <input type="number" name="salary"
                           value="{{ employee[3] }}" min="0" required>
                </div>

                <div class="actions">
                    <button class="btn">
                        <i class="fa-solid fa-floppy-disk"></i> Save Changes
                    </button>
                    <a href="{{ url_for('view_employee') }}"
                       class="btn btn-secondary">Cancel</a>
                </div>
            </form>
        </div>

        {% endif %}

    </main>
</div>

{% endif %}

</body>
</html>
"""


# ---------------- PAGE RENDERER ----------------

def render_page(page, title, heading="", **kwargs):
    return render_template_string(
        TEMPLATE,
        page=page,
        title=title,
        heading=heading,
        messages=flash_messages(),
        today=date.today().isoformat(),
        **kwargs
    )


def flash_messages():
    from flask import get_flashed_messages
    return get_flashed_messages()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_page("home", "Home")


# ---------------- ADMIN LOGIN ----------------

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":
        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:
            session.clear()
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))

        flash("Incorrect password!")

    return render_page("login", "Admin Login")


# ---------------- DASHBOARD ----------------

@app.route("/admin_dashboard")
@admin_required
def admin_dashboard():

    stats = fetch_all("""
        SELECT COUNT(*), COALESCE(SUM(emp_salary), 0)
        FROM emp_details
    """)

    total, payroll = stats[0]

    return render_page(
        "dashboard",
        "Dashboard",
        "Dashboard",
        total=total,
        payroll=payroll
    )


# ---------------- ADD EMPLOYEE ----------------

@app.route("/add_employee", methods=["GET", "POST"])
@admin_required
def add_employee():

    if request.method == "POST":

        try:
            emp_id = int(request.form["emp_id"])
            name = request.form["name"].strip()
            dob = date.fromisoformat(request.form["dob"])
            salary = int(request.form["salary"])

            if not name or len(name) > 100:
                raise ValueError("Enter a valid employee name.")

            if dob > date.today():
                raise ValueError("DOB cannot be in the future.")

            if salary < 0:
                raise ValueError("Salary cannot be negative.")

            execute_query("""
                INSERT INTO emp_details
                (emp_id, emp_name, emp_DOB, emp_salary)
                VALUES (%s, %s, %s, %s)
            """, (emp_id, name, dob, salary))

            flash("Employee added successfully!")

            return redirect(url_for("view_employee"))

        except (ValueError, TypeError) as e:
            flash(str(e) or "Invalid employee details.")

        except mysql.connector.Error as e:
            flash("Database error: " + str(e))

    return render_page("add", "Add Employee", "Add Employee")


# ---------------- VIEW EMPLOYEES ----------------

@app.route("/view_employee")
@admin_required
def view_employee():

    try:
        employees = fetch_all("""
            SELECT emp_id, emp_name, emp_DOB, emp_salary
            FROM emp_details
            ORDER BY emp_id DESC
        """)

    except mysql.connector.Error as e:
        flash("Database error: " + str(e))
        employees = []

    return render_page(
        "view",
        "Employees",
        "Employee Management",
        employees=employees
    )


# ---------------- DELETE EMPLOYEE ----------------

@app.route("/delete_employee/<int:emp_id>", methods=["POST"])
@admin_required
def delete_employee(emp_id):

    try:
        result = execute_query(
            "DELETE FROM emp_details WHERE emp_id=%s",
            (emp_id,)
        )

        if result:
            flash("Employee deleted successfully!")
        else:
            flash("Employee not found!")

    except mysql.connector.Error as e:
        flash("Database error: " + str(e))

    return redirect(url_for("view_employee"))


# ---------------- UPDATE EMPLOYEE ----------------

@app.route("/update_employee/<int:emp_id>", methods=["GET", "POST"])
@admin_required
def update_employee(emp_id):

    try:
        if request.method == "POST":

            name = request.form["name"].strip()
            dob = date.fromisoformat(request.form["dob"])
            salary = int(request.form["salary"])

            if not name or len(name) > 100:
                raise ValueError("Enter a valid employee name.")

            if dob > date.today():
                raise ValueError("DOB cannot be in the future.")

            if salary < 0:
                raise ValueError("Salary cannot be negative.")

            execute_query("""
                UPDATE emp_details
                SET emp_name=%s, emp_DOB=%s, emp_salary=%s
                WHERE emp_id=%s
            """, (name, dob, salary, emp_id))

            flash("Employee updated successfully!")
            return redirect(url_for("view_employee"))

        result = fetch_all(
            "SELECT * FROM emp_details WHERE emp_id=%s",
            (emp_id,)
        )

        if not result:
            flash("Employee not found!")
            return redirect(url_for("view_employee"))

        return render_page(
            "update",
            "Update Employee",
            "Edit Employee",
            employee=result[0]
        )

    except (ValueError, TypeError) as e:
        flash(str(e) or "Invalid employee details.")

    except mysql.connector.Error as e:
        flash("Database error: " + str(e))

    return redirect(url_for("view_employee"))


# ---------------- EMPLOYEE PORTAL ----------------

@app.route("/employee_portal", methods=["GET", "POST"])
def employee_portal():

    employee = None

    if request.method == "POST":

        try:
            emp_id = int(request.form["emp_id"])

            result = fetch_all(
                "SELECT * FROM emp_details WHERE emp_id=%s",
                (emp_id,)
            )

            if result:
                employee = result[0]
            else:
                flash("Employee not found!")

        except ValueError:
            flash("Enter a valid employee ID.")

        except mysql.connector.Error as e:
            flash("Database error: " + str(e))

    return render_page(
        "employee_portal",
        "Employee Portal",
        employee=employee
    )


# ---------------- LOGOUT ----------------

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("home"))


# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    app.run(debug=True)
