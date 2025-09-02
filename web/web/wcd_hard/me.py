import time
from flask import Flask, render_template_string, request, session, redirect, url_for, make_response
import urllib.parse
import re

app = Flask(__name__)
app.secret_key = "supersecretctfkey"

CACHE = {}
CACHE_MAX_AGE = 3600

USERS = {
    "alice": {
        "email": "alice@example.com",
        "password": "alice123",
        "role": "Team Lead",
        "team": "Development",
        "tasks": ["Oversee project timeline", "Code review", "Team coordination"],
        "flag": "FLAG{advanced_wcd_url_encoding_pwned}"
    },
    "bob": {
        "email": "bob@example.com",
        "password": "bob456",
        "role": "Frontend Developer",
        "team": "Development",
        "tasks": ["UI/UX implementation", "React components", "CSS styling"],
        "flag": None
    },
    "carol": {
        "email": "carol@example.com",
        "password": "carol789",
        "role": "Backend Developer",
        "team": "Development",
        "tasks": ["API development", "Database design", "Server maintenance"],
        "flag": None
    },
    "david": {
        "email": "david@example.com",
        "password": "david321",
        "role": "DevOps Engineer",
        "team": "Infrastructure",
        "tasks": ["CI/CD pipeline", "Docker containers", "AWS deployment"],
        "flag": None
    },
    "emma": {
        "email": "emma@example.com",
        "password": "emma654",
        "role": "QA Tester",
        "team": "Quality Assurance",
        "tasks": ["Test case creation", "Bug reporting", "Automated testing"],
        "flag": None
    }
}

def normalize_username_origin_server(username):
    """Origin server normalization - handles URL-encoded separators"""
    try:
        decoded = urllib.parse.unquote(username)
    except:
        decoded = username

    separators = [';', '#', '?', '|', ',', ' ', '\t', '\n', '\r']
    username_cleaned = decoded
    for sep in separators:
        if sep in username_cleaned:
            username_cleaned = username_cleaned.split(sep)[0]
            break

    if '.' in username_cleaned:
        extensions = ['.css', '.js', '.html', '.json', '.xml', '.txt']
        for ext in extensions:
            if username_cleaned.endswith(ext):
                username_cleaned = username_cleaned[:-len(ext)]
                break

    username_cleaned = re.sub(r'[^\w-]', '', username_cleaned.lower())
    return username_cleaned

def cache_server_decision(requested_path):
    """Cache server logic - URL-encoded separators + extensions required"""
    cacheable_extensions = ['.css', '.js', '.html', '.json', '.xml', '.txt']
    
    url_encoded_separators = [
        '%3B', '%3b',  # semicolon (;)
        '%23',         # hash (#)  
        '%3F', '%3f',  # query (?)
        '%7C', '%7c',  # pipe (|)
        '%2C', '%2c',  # comma (,)
        '%20',         # space
        '%09',         # tab
        '%0A', '%0a',  # newline
        '%0D', '%0d'   # carriage return
    ]

    has_separator = any(sep in requested_path for sep in url_encoded_separators)
    
    if has_separator:
        for ext in cacheable_extensions:
            if requested_path.endswith(ext):
                if ext == '.css':
                    return True, "text/css"
                elif ext == '.js':
                    return True, "application/javascript"
                elif ext == '.json':
                    return True, "application/json"
                elif ext == '.xml':
                    return True, "application/xml"
                elif ext == '.txt':
                    return True, "text/plain"
                else:
                    return True, "text/html; charset=utf-8"

    return False, "text/html; charset=utf-8"

@app.route("/")
def home():
    return render_template_string(home_template)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            error = "Please enter both username and password."
        elif username in USERS and USERS[username]["password"] == password:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password."
    return render_template_string(login_template, error=error)

@app.route("/resources/<filename>")
def resources(filename):
    requested_path = request.path
    now = time.time()
    
    cached = CACHE.get(requested_path)
    if cached:
        content, timestamp = cached
        if now - timestamp < CACHE_MAX_AGE:
            resp = make_response(content)
            resp.headers["Cache-Control"] = f"max-age={CACHE_MAX_AGE}"
            resp.headers["X-Cache"] = "hit"
            resp.headers["Age"] = int(now - timestamp)
            resp.headers["Content-Type"] = "text/html; charset=utf-8"
            return resp
        else:
            del CACHE[requested_path]

    if filename == "onboarding.html":
        content = render_template_string(onboarding_template)
    elif filename == "team-info.html":
        content = render_template_string(team_info_template, users=USERS)
    else:
        return "Resource not found", 404

    CACHE[requested_path] = (content, now)
    resp = make_response(content)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    resp.headers["Cache-Control"] = f"max-age={CACHE_MAX_AGE}"
    resp.headers["X-Cache"] = "miss"
    resp.headers["Age"] = 0
    return resp

@app.route("/user/<path:username>")
def user_page(username):
    """Advanced Web Cache Deception - URL-encoded separators required"""
    if "username" not in session:
        return redirect(url_for("login"))

    current_user = session["username"]
    requested_path = request.path
    now = time.time()

    # Check cache first
    cached = CACHE.get(requested_path)
    if cached:
        content, timestamp = cached
        if now - timestamp < CACHE_MAX_AGE:
            resp = make_response(content)
            resp.headers["Cache-Control"] = f"max-age={CACHE_MAX_AGE}"
            resp.headers["X-Cache"] = "HIT"
            resp.headers["Age"] = int(now - timestamp)
            resp.headers["Content-Type"] = "text/html; charset=utf-8"
            resp.headers["X-Cache-Server"] = "CloudFront"
            return resp
        else:
            del CACHE[requested_path]

    # Get raw path for cache decision
    raw_path = request.environ.get('REQUEST_URI') or request.environ.get('RAW_URI') or request.full_path.rstrip('?')
    should_cache, content_type = cache_server_decision(raw_path)

    if should_cache:
        # Advanced WCD: normalize username from URL-encoded separators
        username_to_serve = normalize_username_origin_server(username)
    else:
        # Normal request: only serve current user's profile
        username_to_serve = current_user
        if username.lower() != current_user.lower():
            return "Access denied: You can only view your own profile", 403

    user = USERS.get(username_to_serve)
    if not user:
        return "User not found", 404

    content = render_template_string(user_profile_template,
                                     username=username_to_serve,
                                     email=user["email"],
                                     role=user["role"],
                                     team=user["team"],
                                     tasks=user["tasks"],
                                     flag=user["flag"])

    # Cache if should_cache is True (the vulnerability)
    if should_cache:
        CACHE[requested_path] = (content, now)

    resp = make_response(content)
    resp.headers["Content-Type"] = content_type

    if should_cache:
        resp.headers["Cache-Control"] = f"max-age={CACHE_MAX_AGE}"
        resp.headers["X-Cache"] = "MISS"
        resp.headers["Age"] = 0
        resp.headers["X-Cache-Server"] = "CloudFront"
    else:
        resp.headers["X-Cache"] = "NONE"

    return resp

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    user_data = USERS[username]
    return render_template_string(dashboard_template, user=user_data, username=username)

home_template = """
<!DOCTYPE html>
<html>
<head>
    <title>CollabFlow</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border: 1px solid #ddd; }
        h1 { color: #333; }
        p { color: #666; margin: 20px 0; }
        a { background: #0066cc; color: white; padding: 10px 20px; text-decoration: none; }
        a:hover { background: #004499; }
    </style>
</head>
<body>
    <div class="container">
        <h1>CollabFlow</h1>
        <p>Employee Portal - Advanced Security</p>
        <a href="/login">Login</a>
    </div>
</body>
</html>
"""

login_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - CollabFlow</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .login-box { max-width: 400px; margin: 50px auto; background: white; padding: 30px; border: 1px solid #ddd; }
        h2 { color: #333; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #555; }
        input { width: 100%; padding: 8px; border: 1px solid #ddd; box-sizing: border-box; }
        button { width: 100%; background: #0066cc; color: white; padding: 10px; border: none; cursor: pointer; }
        button:hover { background: #004499; }
        .error { color: #cc0000; margin-bottom: 15px; padding: 10px; background: #ffe6e6; }
        .demo { background: #f0f0f0; padding: 15px; margin-top: 20px; font-size: 14px; }
        .back a { color: #0066cc; }
        .security-notice { background: #e8f5e8; padding: 10px; margin-top: 10px; font-size: 12px; color: #2d5a2d; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Login</h2>

        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}

        <form method="POST">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>

        <div class="demo">
            <strong>Test Accounts:</strong><br>
            alice / alice123<br>
            bob / bob456<br>
            carol / carol789<br>
            david / david321<br>
            emma / emma654
        </div>

        <div class="security-notice">
            <strong>Security:</strong> This system uses advanced cache protection against simple extension-based attacks.
        </div>

        <div class="back">
            <a href="/">Back to Home</a>
        </div>
    </div>
</body>
</html>
"""

dashboard_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - CollabFlow</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border: 1px solid #ddd; }
        h1 { color: #333; margin-bottom: 10px; }
        .user-info { background: #f9f9f9; padding: 15px; margin: 20px 0; }
        .nav-links { margin: 30px 0; }
        .nav-links a {
            display: inline-block;
            background: #0066cc;
            color: white;
            padding: 10px 15px;
            margin: 5px;
            text-decoration: none;
        }
        .nav-links a:hover { background: #004499; }
        .logout { margin-top: 30px; }
        .logout a { color: #cc0000; }
        .security-info { background: #fff3cd; border: 1px solid #ffc107; padding: 10px; margin: 20px 0; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>CollabFlow Dashboard</h1>
        <p>Welcome, {{ username }}</p>

        <div class="user-info">
            <h3>Profile Information</h3>
            <p><strong>Role:</strong> {{ user.role }}</p>
            <p><strong>Team:</strong> {{ user.team }}</p>
            <p><strong>Email:</strong> {{ user.email }}</p>
        </div>

        <div class="nav-links">
            <a href="/resources/onboarding.html">Employee Onboarding</a>
            <a href="/user/{{ username }}">My Profile</a>
            <a href="/resources/team-info.html">Team Directory</a>
        </div>

        <div class="security-info">
            <strong>Security Notice:</strong> Profile pages are protected with advanced caching controls to prevent unauthorized access.
        </div>

        <div class="logout">
            <a href="/logout">Logout</a>
        </div>
    </div>
</body>
</html>
"""

user_profile_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ username }} Profile</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 700px; margin: 0 auto; background: white; padding: 20px; border: 1px solid #ddd; }
        h1, h2 { color: #333; }
        .section { margin: 20px 0; padding: 15px; background: #f9f9f9; }
        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
        .info-item { background: white; padding: 10px; }
        .info-label { font-size: 12px; color: #666; margin-bottom: 5px; }
        .info-value { font-weight: bold; }
        .task-list { list-style: none; padding: 0; }
        .task-item { background: white; padding: 10px; margin: 5px 0; border-left: 3px solid #0066cc; }
        .flag-section {
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
        }
        .flag-value {
            background: #f8f9fa;
            padding: 10px;
            font-family: monospace;
            border: 1px solid #dee2e6;
            word-break: break-all;
        }
        .back a { color: #0066cc; }
        .cache-warning {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 10px;
            margin: 20px 0;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>User Profile</h1>

        <div class="section">
            <h2>{{ username }}</h2>
            <p>{{ role }}</p>

            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Email</div>
                    <div class="info-value">{{ email }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Team</div>
                    <div class="info-value">{{ team }}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Role</div>
                    <div class="info-value">{{ role }}</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h3>Assigned Tasks</h3>
            <ul class="task-list">
                {% for task in tasks %}
                <li class="task-item">{{ task }}</li>
                {% endfor %}
            </ul>
        </div>

        {% if flag %}
        <div class="flag-section">
            <h3>Achievement Flag</h3>
            <div class="flag-value">{{ flag }}</div>
        </div>
        {% else %}
        <div class="flag-section">
            <h3>Achievement Flag</h3>
            <p>No flag assigned to this user</p>
        </div>
        {% endif %}

        <div class="cache-warning">
            <strong>Warning:</strong> This page should never be cached due to sensitive personal information.
        </div>

        <div class="back">
            <a href="/dashboard">Back to Dashboard</a>
        </div>
    </div>
</body>
</html>
"""

onboarding_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Employee Onboarding</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 700px; margin: 0 auto; background: white; padding: 20px; border: 1px solid #ddd; }
        h1, h2, h3 { color: #333; }
        .section { margin: 20px 0; padding: 15px; background: #f9f9f9; }
        .checklist-item { padding: 5px 0; border-bottom: 1px solid #eee; }
        .contact-info { background: #e8f5e8; padding: 15px; margin: 20px 0; }
        .back a { color: #0066cc; }
    </style>
</head>
<body>
    <div class="container">
        <h1>New Employee Onboarding</h1>
        <p>Welcome to CollabFlow Advanced Security Portal.</p>

        <div class="section">
            <h2>Week 1: Setup</h2>
            <h3>Account Setup</h3>
            <div class="checklist-item">- Get login credentials from team lead</div>
            <div class="checklist-item">- Complete first login</div>
            <div class="checklist-item">- Update profile information</div>
            <div class="checklist-item">- Join team workspace</div>

            <h3>Security Orientation</h3>
            <div class="checklist-item">- Review security policies</div>
            <div class="checklist-item">- Complete security training</div>
            <div class="checklist-item">- Learn about cache protection</div>
            <div class="checklist-item">- Test system features</div>
        </div>

        <div class="section">
            <h2>Week 2: Integration</h2>
            <div class="checklist-item">- Schedule manager meeting</div>
            <div class="checklist-item">- Join team meetings</div>
            <div class="checklist-item">- Complete training modules</div>
            <div class="checklist-item">- Review company policies</div>
        </div>

        <div class="contact-info">
            <h3>Important Contacts</h3>
            <p><strong>Team Lead:</strong> alice@collabflow.com</p>
            <p><strong>IT Support:</strong> support@collabflow.com</p>
            <p><strong>Security Team:</strong> security@collabflow.com</p>
        </div>

        <div class="back">
            <a href="/dashboard">Back to Dashboard</a>
        </div>
    </div>
</body>
</html>
"""

team_info_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Team Directory</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 20px; border: 1px solid #ddd; }
        h1 { color: #333; }
        .team-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .person-card {
            background: #f9f9f9;
            padding: 15px;
            border: 1px solid #ddd;
        }
        .person-name { font-weight: bold; color: #0066cc; margin-bottom: 5px; }
        .person-role { color: #333; margin-bottom: 3px; }
        .person-team { color: #666; margin-bottom: 3px; }
        .person-email { color: #666; font-size: 14px; }
        .back a { color: #0066cc; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Team Directory</h1>
        <p>Secure employee directory with advanced access controls</p>

        <div class="team-grid">
            {% for username, user_data in users.items() %}
            <div class="person-card">
                <div class="person-name">{{ username.title() }}</div>
                <div class="person-role">{{ user_data.role }}</div>
                <div class="person-team">{{ user_data.team }} Team</div>
                <div class="person-email">{{ user_data.email }}</div>
            </div>
            {% endfor %}
        </div>

        <div class="back">
            <a href="/dashboard">Back to Dashboard</a>
        </div>
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3200)
