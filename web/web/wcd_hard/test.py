# NOTE: I know this code has intentional security vulnerabilities - it's designed for a CTF challenge
# In production, you'd want proper password hashing, secure session management, etc.

import time
from flask import make_response
import time
from flask import Flask, render_template, render_template_string, request, session, redirect, url_for, make_response
import urllib.parse
import re

# Initialize Flask app first
app = Flask(__name__)
app.secret_key = "supersecretctfkey"
# Cache configuration for Web Cache Deception vulnerability
CACHE = {}
CACHE_MAX_AGE = 3600  # 1 hour

USERS = {
    "alice": {
        "email": "alice@example.com", 
        "password": "alice123", 
        "role": "Team Lead",
        "team": "Development",
        "tasks": ["Oversee project timeline", "Code review", "Team coordination"],
        "flag": "FLAG{wcd_basic_success}"
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

def login():
    """
    Standard login function with username and password authentication
    """
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
    """
    Company resources that get cached for performance
    This naturally demonstrates caching without being obvious about vulnerabilities
    """
    requested_path = request.path
    now = time.time()

    # Check cache first
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
            del CACHE[requested_path]  # expired

    # Serve actual company resources
    if filename == "onboarding-checklist.html":
        content = render_template_string(onboarding_template)
    elif filename == "coding-standards.html":
        content = render_template_string(coding_standards_template)
    elif filename == "team-directory.html":
        content = render_template_string(team_directory_template, users=USERS)
    else:
        return "Resource not found", 404

    # Cache all resource files
    CACHE[requested_path] = (content, now)

    resp = make_response(content)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    resp.headers["Cache-Control"] = f"max-age={CACHE_MAX_AGE}"
    resp.headers["X-Cache"] = "miss"
    resp.headers["Age"] = 0
    
    return resp

@app.route("/static/<path:filename>")
def static_files(filename):
    """
    Static file handler that also demonstrates caching behavior
    This gives players another hint about what gets cached vs what doesn't
    
    Examples:
    - /static/style.css → Gets cached
    - /static/app.js → Gets cached  
    - /static/config.json → Gets cached
    - /static/../../user/alice → Path traversal attempt (should fail)
    """
    requested_path = request.path
    now = time.time()

    # Check cache first
    cached = CACHE.get(requested_path)
    if cached:
        content, timestamp = cached
        if now - timestamp < CACHE_MAX_AGE:
            resp = make_response(content)
            resp.headers["Cache-Control"] = f"max-age={CACHE_MAX_AGE}"
            resp.headers["X-Cache"] = "hit"
            resp.headers["Age"] = int(now - timestamp)
            
            # Set appropriate content type based on extension
            if filename.endswith('.css'):
                resp.headers["Content-Type"] = "text/css"
            elif filename.endswith('.js'):
                resp.headers["Content-Type"] = "application/javascript"
            elif filename.endswith('.json'):
                resp.headers["Content-Type"] = "application/json"
            else:
                resp.headers["Content-Type"] = "text/plain"
                
            return resp
        else:
            del CACHE[requested_path]  # expired

    # Simulate serving static files (but we don't actually have any)
    # This is just to demonstrate caching behavior
    if filename == "style.css":
        content = """
/* CollabFlow Static CSS */
body { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    font-family: 'SF Pro Display', sans-serif;
}
.cached-file { 
    color: #4ecdc4; 
    text-align: center;
    padding: 2rem;
}
"""
    elif filename == "app.js":
        content = """
// CollabFlow Static JavaScript
console.log('CollabFlow app loaded');
document.addEventListener('DOMContentLoaded', function() {
    console.log('This is a cached static file');
    // Static files like this get cached automatically
});
"""
    elif filename == "config.json":
        content = """{
    "app_name": "CollabFlow",
    "version": "1.0.0",
    "cache_enabled": true,
    "note": "This JSON file gets cached as a static resource"
}"""
    else:
        # For any other filename, show a helpful message
        content = f"""
<!DOCTYPE html>
<html>
<head><title>Static File Demo</title></head>
<body style="font-family: sans-serif; padding: 2rem; background: #f0f0f0;">
    <h1>Static File: {filename}</h1>
    <p><strong>Cache Status:</strong> This file gets cached because it's in /static/</p>
    <p><strong>Path:</strong> {requested_path}</p>
    <p><strong>Tip:</strong> Files in /static/ are automatically cached for performance.</p>
    <p>Try: <a href="/static/style.css">/static/style.css</a> | 
           <a href="/static/app.js">/static/app.js</a> | 
           <a href="/static/config.json">/static/config.json</a></p>
    <hr>
    <small>This demonstrates which paths get cached by the server.</small>
</body>
</html>"""

    # Cache ALL static files regardless of extension
    CACHE[requested_path] = (content, now)

    resp = make_response(content)
    
    # Set content type based on file extension
    if filename.endswith('.css'):
        resp.headers["Content-Type"] = "text/css"
    elif filename.endswith('.js'):
        resp.headers["Content-Type"] = "application/javascript"
    elif filename.endswith('.json'):
        resp.headers["Content-Type"] = "application/json"
    else:
        resp.headers["Content-Type"] = "text/html; charset=utf-8"
    
    # All static files get cache headers
    resp.headers["Cache-Control"] = f"max-age={CACHE_MAX_AGE}"
    resp.headers["X-Cache"] = "miss"
    resp.headers["Age"] = 0
    
    return resp

@app.route("/cache-info")
def cache_info():
    """
    Debug endpoint to show what's currently cached
    Helps players understand the caching mechanism
    """
    if "username" not in session:
        return redirect(url_for("login"))
    
    cache_data = []
    now = time.time()
    
    for path, (content, timestamp) in CACHE.items():
        age = int(now - timestamp)
        expired = age > CACHE_MAX_AGE
        cache_data.append({
            'path': path,
            'age': age,
            'expired': expired,
            'content_length': len(content)
        })
    
    return render_template_string(cache_info_template, cache_data=cache_data)

@app.route("/user/<username>")
def user_page(username):
    """
    Web Cache Deception Vulnerability - This is the main vulnerability for this CTF
    
    The vulnerability works as follows:
    1. Normal request: /user/alice returns Alice's page
    2. Malicious request: /user/alice.css or /user/alice.js 
    3. The server strips the extension and serves Alice's page
    4. BUT the response gets cached as if it were a static file (.css/.js)
    5. Attackers can then access /user/alice.css to see Alice's cached private data
    
    This simulates real-world WCD where CDNs cache files with static extensions
    but the origin server treats them as dynamic content.
    """
    requested_path = request.path
    now = time.time()

    # Check cache first - this is where the vulnerability lies
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
            del CACHE[requested_path]  # expired

    # Determine username to serve
    if requested_path.endswith((".js", ".css", ".html")):
        # Simulate WCD: strip extension and serve dynamic page
        username_to_serve = username.rsplit(".", 1)[0]
    else:
        username_to_serve = username

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
    
    # Store in cache if .js, .css, or .html - THIS IS THE VULNERABILITY
    # Private user data gets cached as if it were a static file
    if requested_path.endswith((".js", ".css", ".html")):
        CACHE[requested_path] = (content, now)

    resp = make_response(content)
    if requested_path.endswith(".js"):
        resp.headers["Content-Type"] = "application/javascript"
    elif requested_path.endswith(".css"):
        resp.headers["Content-Type"] = "text/css"
    elif requested_path.endswith(".html"):
        resp.headers["Content-Type"] = "text/html; charset=utf-8"
    if requested_path.endswith((".js", ".css", ".html")):
        resp.headers["Cache-Control"] = f"max-age={CACHE_MAX_AGE}"
        resp.headers["X-Cache"] = "miss"
        resp.headers["Age"] = 0
    else:
        resp.headers["X-Cache"] = "none"

    return resp

@app.route("/dashboard")
def dashboard():
    """User dashboard with navigation options"""
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session["username"]
    user_data = USERS[username]
    
    return render_template_string(dashboard_template, user=user_data, username=username)

@app.route("/user/viewteam")
def viewteam():
    """View team members - shows all users"""
    if "username" not in session:
        return redirect(url_for("login"))
    
    current_user = session["username"]
    current_user_data = USERS[current_user]
    
    return render_template_string(team_template, 
                                current_user=current_user,
                                current_user_data=current_user_data,
                                users=USERS)

@app.route("/user/tasks")
def my_tasks():
    """View current user's assigned tasks"""
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session["username"]
    user_data = USERS[username]
    
    return render_template_string(tasks_template, user=user_data, username=username)

@app.route("/viewteam/<username>/tasks")
def view_user_tasks(username):
    """Attempt to view another user's tasks - should show permission denied"""
    if "username" not in session:
        return redirect(url_for("login"))
    
    current_user = session["username"]
    
    # Permission check - only allow users to view their own tasks
    if current_user != username:
        return render_template_string(permission_denied_template, 
                                    current_user=current_user,
                                    requested_user=username)
    
    # If somehow they access their own tasks through this route
    user_data = USERS[username]
    return render_template_string(tasks_template, user=user_data, username=username)

# Resource page templates
onboarding_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CollabFlow - New Employee Onboarding</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 2rem;
        }

        .header {
            text-align: center;
            margin-bottom: 2rem;
            color: white;
        }

        .logo {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }

        .content {
            color: white;
            line-height: 1.6;
        }

        h1, h2, h3 {
            color: #4ecdc4;
            margin-bottom: 1rem;
        }

        .checklist {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1.5rem 0;
        }

        .checklist-item {
            display: flex;
            align-items: center;
            margin-bottom: 0.8rem;
            padding: 0.5rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
        }

        .checkbox {
            width: 20px;
            height: 20px;
            border: 2px solid #4ecdc4;
            border-radius: 4px;
            margin-right: 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #4ecdc4;
            font-weight: bold;
        }

        .contact-info {
            background: rgba(78, 205, 196, 0.1);
            border: 1px solid rgba(78, 205, 196, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 2rem;
        }

        .links {
            margin-top: 2rem;
            text-align: center;
        }

        .links a {
            color: #4ecdc4;
            text-decoration: none;
            margin: 0 1rem;
            padding: 0.5rem 1rem;
            border: 1px solid rgba(78, 205, 196, 0.3);
            border-radius: 8px;
            transition: all 0.3s ease;
        }

        .links a:hover {
            background: rgba(78, 205, 196, 0.1);
        }

        .back-link {
            text-align: center;
            margin-top: 2rem;
        }

        .back-link a {
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .back-link a:hover {
            color: #4ecdc4;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">CollabFlow</div>
            <h1>New Employee Onboarding</h1>
        </div>

        <div class="content">
            <p>Welcome to CollabFlow! This guide will help you get started with our team collaboration platform.</p>

            <div class="checklist">
                <h2>Week 1: Getting Started</h2>
                
                <h3>Account Setup</h3>
                <div class="checklist-item">
                    <div class="checkbox">✓</div>
                    Receive login credentials from your team lead
                </div>
                <div class="checklist-item">
                    <div class="checkbox">✓</div>
                    Complete first login and password change
                </div>
                <div class="checklist-item">
                    <div class="checkbox">✓</div>
                    Update your profile information
                </div>
                <div class="checklist-item">
                    <div class="checkbox">✓</div>
                    Join your assigned team workspace
                </div>

                <h3>Platform Orientation</h3>
                <div class="checklist-item">
                    <div class="checkbox">✓</div>
                    Review team member directory
                </div>
                <div class="checklist-item">
                    <div class="checkbox">✓</div>
                    Explore your assigned tasks
                </div>
                <div class="checklist-item">
                    <div class="checkbox">✓</div>
                    Familiarize yourself with the dashboard
                </div>
                <div class="checklist-item">
                    <div class="checkbox">✓</div>
                    Test communication features
                </div>
            </div>

            <div class="checklist">
                <h2>Week 2: Team Integration</h2>
                <div class="checklist-item">
                    <div class="checkbox">✓</div>
                    Schedule 1:1 with your direct manager
                </div>
                <div class="checklist-item">
                    <div class="checkbox">✓</div>
                    Attend team standup meeting
                </div>
                <div class="checklist-item">
                    <div class="checkbox">✓</div>
                    Complete security training
                </div>
                <div class="checklist-item">
                    <div class="checkbox">✓</div>
                    Review coding standards document
                </div>
            </div>

            <div class="contact-info">
                <h3>Important Contacts</h3>
                <p><strong>Team Lead:</strong> alice@collabflow.com</p>
                <p><strong>IT Support:</strong> support@collabflow.com</p>
                <p><strong>HR Questions:</strong> hr@collabflow.com</p>
            </div>

            <div class="links">
                <a href="/resources/coding-standards.html">Coding Standards</a>
                <a href="/resources/team-directory.html">Team Directory</a>
            </div>
        </div>

        <div class="back-link">
            <a href="/dashboard">&larr; Back to Dashboard</a>
        </div>
    </div>
</body>
</html>
"""

coding_standards_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CollabFlow - Coding Standards</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 2rem;
        }

        .header {
            text-align: center;
            margin-bottom: 2rem;
            color: white;
        }

        .logo {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }

        .content {
            color: white;
            line-height: 1.6;
        }

        h1, h2, h3 {
            color: #4ecdc4;
            margin-bottom: 1rem;
        }

        .section {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1.5rem 0;
        }

        .code-example {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.9rem;
            color: #4ecdc4;
            overflow-x: auto;
        }

        .guideline {
            background: rgba(255, 255, 255, 0.05);
            border-left: 4px solid #4ecdc4;
            padding: 1rem;
            margin: 1rem 0;
        }

        ul {
            padding-left: 1.5rem;
        }

        li {
            margin-bottom: 0.5rem;
        }

        .back-link {
            text-align: center;
            margin-top: 2rem;
        }

        .back-link a {
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .back-link a:hover {
            color: #4ecdc4;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">CollabFlow</div>
            <h1>Development Team Coding Standards</h1>
        </div>

        <div class="content">
            <div class="section">
                <h2>General Principles</h2>
                <ul>
                    <li>Write clean, readable, and maintainable code</li>
                    <li>Use meaningful variable and function names</li>
                    <li>Comment complex logic and business rules</li>
                    <li>Follow DRY (Don't Repeat Yourself) principles</li>
                </ul>
            </div>

            <div class="section">
                <h2>Python Standards</h2>
                <div class="code-example">
# Use snake_case for variables and functions
user_name = "alice"
def get_user_profile(user_id):
    return user_data

# Use PascalCase for classes  
class UserManager:
    def __init__(self):
        pass

# Use UPPER_CASE for constants
MAX_LOGIN_ATTEMPTS = 3
                </div>
            </div>

            <div class="section">
                <h2>JavaScript Standards</h2>
                <div class="code-example">
// Use camelCase for variables and functions
const userName = 'alice';
function getUserProfile(userId) {
    return userData;
}

// Use PascalCase for classes
class UserManager {
    constructor() {}
}

// Use UPPER_CASE for constants
const MAX_LOGIN_ATTEMPTS = 3;
                </div>
            </div>

            <div class="section">
                <h2>Security Guidelines</h2>
                <div class="guideline">
                    <h3>Critical Security Practices</h3>
                    <ul>
                        <li>Validate all user inputs on both client and server side</li>
                        <li>Use parameterized queries to prevent SQL injection</li>
                        <li>Sanitize data before displaying to prevent XSS</li>
                        <li>Never store passwords in plain text</li>
                        <li>Implement proper session management</li>
                    </ul>
                </div>
            </div>

            <div class="section">
                <h2>Code Review Process</h2>
                <p>All code changes must go through our peer review process:</p>
                <ul>
                    <li>Create feature branch from main</li>
                    <li>Run tests locally before submitting</li>
                    <li>Request review from at least one team member</li>
                    <li>Address all feedback before merging</li>
                </ul>
            </div>

            <div class="section">
                <h2>Testing Requirements</h2>
                <ul>
                    <li>Minimum 80% code coverage for new features</li>
                    <li>Unit tests for all business logic</li>
                    <li>Integration tests for API endpoints</li>
                    <li>End-to-end tests for critical user workflows</li>
                </ul>
            </div>
        </div>

        <div class="back-link">
            <a href="/dashboard">&larr; Back to Dashboard</a>
        </div>
    </div>
</body>
</html>
"""

team_directory_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CollabFlow - Team Directory</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 2rem;
        }

        .header {
            text-align: center;
            margin-bottom: 2rem;
            color: white;
        }

        .logo {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }

        .directory-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }

        .person-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 1.5rem;
            color: white;
            transition: all 0.3s ease;
        }

        .person-card:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-3px);
        }

        .person-name {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #4ecdc4;
        }

        .person-role {
            font-weight: 500;
            margin-bottom: 0.3rem;
        }

        .person-team {
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 0.5rem;
        }

        .person-email {
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.8);
        }

        .back-link {
            text-align: center;
            margin-top: 2rem;
        }

        .back-link a {
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .back-link a:hover {
            color: #4ecdc4;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">CollabFlow</div>
            <h1>Team Directory</h1>
            <p>Connect with your colleagues across all teams</p>
        </div>

        <div class="directory-grid">
            {% for username, user_data in users.items() %}
            <div class="person-card">
                <div class="person-name">{{ username.title() }}</div>
                <div class="person-role">{{ user_data.role }}</div>
                <div class="person-team">{{ user_data.team }} Team</div>
                <div class="person-email">{{ user_data.email }}</div>
            </div>
            {% endfor %}
        </div>

        <div class="back-link">
            <a href="/dashboard">&larr; Back to Dashboard</a>
        </div>
    </div>
</body>
</html>
"""

# User profile template for the vulnerable /user/<username> route
user_profile_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CollabFlow - {{ username }} Profile</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 2rem;
        }

        .header {
            text-align: center;
            margin-bottom: 2rem;
            color: white;
        }

        .logo {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }

        .profile-section {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            color: white;
        }

        .profile-header {
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .profile-avatar {
            width: 80px;
            height: 80px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            margin-right: 1.5rem;
        }

        .profile-info h2 {
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
            color: #4ecdc4;
        }

        .profile-info .role {
            font-size: 1.1rem;
            color: rgba(255, 255, 255, 0.8);
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .info-item {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 1rem;
        }

        .info-label {
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.6);
            margin-bottom: 0.3rem;
        }

        .info-value {
            font-size: 1rem;
            color: white;
            font-weight: 500;
        }

        .tasks-section {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            color: white;
        }

        .section-title {
            font-size: 1.3rem;
            margin-bottom: 1rem;
            color: #4ecdc4;
        }

        .tasks-list {
            list-style: none;
        }

        .task-item {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.8rem;
            transition: all 0.3s ease;
        }

        .task-item:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateX(5px);
        }

        .task-item::before {
            content: "✓";
            color: #4ecdc4;
            font-weight: bold;
            margin-right: 0.5rem;
        }

        .flag-section {
            background: rgba(255, 107, 107, 0.1);
            border: 2px solid rgba(255, 107, 107, 0.3);
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
        }

        .flag-title {
            color: #ff6b6b;
            font-size: 1.2rem;
            margin-bottom: 1rem;
            font-weight: 600;
        }

        .flag-value {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 1rem;
            font-family: 'Monaco', monospace;
            font-size: 1.1rem;
            color: #4ecdc4;
            word-break: break-all;
        }

        .no-flag {
            color: rgba(255, 255, 255, 0.6);
            font-style: italic;
        }

        .back-link {
            text-align: center;
            margin-top: 2rem;
        }

        .back-link a {
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .back-link a:hover {
            color: #4ecdc4;
        }

        .cache-info {
            background: rgba(78, 205, 196, 0.1);
            border: 1px solid rgba(78, 205, 196, 0.3);
            border-radius: 10px;
            padding: 1rem;
            margin-top: 1rem;
            font-size: 0.85rem;
            color: rgba(255, 255, 255, 0.7);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">CollabFlow</div>
            <h1>User Profile</h1>
        </div>

        <div class="profile-section">
            <div class="profile-header">
                <div class="profile-avatar">👤</div>
                <div class="profile-info">
                    <h2>{{ username }}</h2>
                    <div class="role">{{ role }}</div>
                </div>
            </div>

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

        <div class="tasks-section">
            <h3 class="section-title">Assigned Tasks</h3>
            <ul class="tasks-list">
                {% for task in tasks %}
                <li class="task-item">{{ task }}</li>
                {% endfor %}
            </ul>
        </div>

        {% if flag %}
        <div class="flag-section">
            <div class="flag-title">🏁 Achievement Flag</div>
            <div class="flag-value">{{ flag }}</div>
        </div>
        {% else %}
        <div class="flag-section">
            <div class="flag-title">🏁 Achievement Flag</div>
            <div class="no-flag">No flag assigned to this user</div>
        </div>
        {% endif %}

        <div class="cache-info">
            💡 <strong>Tip:</strong> This page contains sensitive user information and should be properly protected from caching vulnerabilities.
        </div>

        <div class="back-link">
            <a href="/dashboard">&larr; Back to Dashboard</a>
        </div>
    </div>
</body>
</html>
"""

# Templates
dashboard_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CollabFlow - Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }

        .dashboard-container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 2rem;
            animation: fadeInUp 0.6s ease;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .header {
            text-align: center;
            margin-bottom: 2rem;
            color: white;
        }

        .logo {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .welcome {
            margin-top: 1rem;
            font-size: 1.2rem;
            color: rgba(255, 255, 255, 0.9);
        }

        .user-info {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            color: white;
        }

        .navigation {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }

        .nav-card {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 2rem;
            text-align: center;
            transition: all 0.3s ease;
            text-decoration: none;
            color: white;
            display: block;
        }

        .nav-card:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        }

        .nav-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }

        .nav-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .nav-description {
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.9rem;
        }

        .logout {
            text-align: center;
            margin-top: 2rem;
        }

        .logout a {
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .logout a:hover {
            color: #ff6b6b;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <div class="logo">CollabFlow</div>
            <div class="welcome">Welcome back, {{ username }}!</div>
        </div>

        <div class="user-info">
            <h3>User Profile</h3>
            <p><strong>Role:</strong> {{ user.role }}</p>
            <p><strong>Team:</strong> {{ user.team }}</p>
            <p><strong>Email:</strong> {{ user.email }}</p>
        </div>

        <div class="navigation">
            <a href="/resources/onboarding-checklist.html" class="nav-card">
                <div class="nav-icon">📋</div>
                <div class="nav-title">Onboarding Guide</div>
                <div class="nav-description">New employee setup and checklist</div>
            </a>

            <a href="/user/{{ username }}" class="nav-card">
                <div class="nav-icon">👤</div>
                <div class="nav-title">My Profile</div>
                <div class="nav-description">View your detailed profile information</div>
            </a>

            <a href="/user/viewteam" class="nav-card">
                <div class="nav-icon">👥</div>
                <div class="nav-title">View Team</div>
                <div class="nav-description">See all team members and their roles</div>
            </a>

            <a href="/user/tasks" class="nav-card">
                <div class="nav-icon">📋</div>
                <div class="nav-title">My Tasks</div>
                <div class="nav-description">View your assigned tasks and responsibilities</div>
            </a>
        </div>

        <div class="logout">
            <a href="/logout">Logout</a>
        </div>
    </div>
</body>
</html>
"""

team_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CollabFlow - Team Members</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 2rem;
        }

        .header {
            text-align: center;
            margin-bottom: 2rem;
            color: white;
        }

        .logo {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }

        .team-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .team-member {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 1.5rem;
            color: white;
            transition: all 0.3s ease;
        }

        .team-member:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-3px);
        }

        .member-name {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #4ecdc4;
        }

        .member-role {
            font-weight: 500;
            margin-bottom: 0.3rem;
        }

        .member-team {
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 1rem;
        }

        .tasks-link {
            display: inline-block;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            text-decoration: none;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }

        .tasks-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
        }

        .back-link {
            text-align: center;
            margin-top: 2rem;
        }

        .back-link a {
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .back-link a:hover {
            color: #4ecdc4;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">CollabFlow Team</div>
            <h1>Team Members</h1>
        </div>

        <div class="team-grid">
            {% for username, user_data in users.items() %}
            <div class="team-member">
                <div class="member-name">{{ username }}</div>
                <div class="member-role">{{ user_data.role }}</div>
                <div class="member-team">Team: {{ user_data.team }}</div>
                <a href="/viewteam/{{ username }}/tasks" class="tasks-link">View Tasks</a>
            </div>
            {% endfor %}
        </div>

        <div class="back-link">
            <a href="/dashboard">&larr; Back to Dashboard</a>
        </div>
    </div>
</body>
</html>
"""

tasks_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CollabFlow - My Tasks</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 2rem;
        }

        .header {
            text-align: center;
            margin-bottom: 2rem;
            color: white;
        }

        .logo {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }

        .user-info {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            color: white;
        }

        .tasks-list {
            list-style: none;
        }

        .task-item {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            color: white;
            transition: all 0.3s ease;
        }

        .task-item:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateX(5px);
        }

        .task-item::before {
            content: "✓";
            color: #4ecdc4;
            font-weight: bold;
            margin-right: 0.5rem;
        }

        .back-link {
            text-align: center;
            margin-top: 2rem;
        }

        .back-link a {
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .back-link a:hover {
            color: #4ecdc4;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">CollabFlow</div>
            <h1>My Assigned Tasks</h1>
        </div>

        <div class="user-info">
            <h3>{{ username }} - {{ user.role }}</h3>
            <p>Team: {{ user.team }}</p>
        </div>

        <ul class="tasks-list">
            {% for task in user.tasks %}
            <li class="task-item">{{ task }}</li>
            {% endfor %}
        </ul>

        <div class="back-link">
            <a href="/dashboard">&larr; Back to Dashboard</a>
        </div>
    </div>
</body>
</html>
"""

permission_denied_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CollabFlow - Access Denied</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }

        .error-container {
            max-width: 500px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 107, 107, 0.3);
            border-radius: 20px;
            padding: 3rem;
            text-align: center;
            animation: shake 0.5s ease;
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }

        .error-icon {
            font-size: 4rem;
            color: #ff6b6b;
            margin-bottom: 1rem;
        }

        .error-title {
            font-size: 2rem;
            font-weight: 700;
            color: #ff6b6b;
            margin-bottom: 1rem;
        }

        .error-message {
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.1rem;
            margin-bottom: 2rem;
            line-height: 1.6;
        }

        .back-links {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }

        .back-link {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            padding: 0.8rem 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            text-decoration: none;
            transition: all 0.3s ease;
        }

        .back-link:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">🚫</div>
        <h1 class="error-title">Permission Denied</h1>
        <p class="error-message">
            You don't have permission to view {{ requested_user }}'s tasks. 
            You can only access your own assigned tasks and team overview.
        </p>
        <div class="back-links">
            <a href="/user/tasks" class="back-link">My Tasks</a>
            <a href="/user/viewteam" class="back-link">Team View</a>
            <a href="/dashboard" class="back-link">Dashboard</a>
        </div>
    </div>
</body>
</html>
"""

# Update login template to include demo credentials for all 5 users
login_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CollabFlow - Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .login-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 3rem;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
            animation: fadeInUp 0.6s ease;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .logo {
            text-align: center;
            margin-bottom: 2rem;
        }

        .logo h1 {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }

        .logo p {
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            color: rgba(255, 255, 255, 0.9);
            font-weight: 500;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }

        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            color: white;
            font-size: 1rem;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }

        input[type="text"]:focus,
        input[type="password"]:focus {
            outline: none;
            border-color: rgba(255, 107, 107, 0.6);
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.1);
        }

        input::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }

        .login-button {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 1rem;
        }

        .login-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 35px rgba(255, 107, 107, 0.4);
        }

        .login-button:active {
            transform: translateY(0);
        }

        .error-message {
            background: rgba(255, 107, 107, 0.2);
            border: 1px solid rgba(255, 107, 107, 0.4);
            color: #ff6b6b;
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            text-align: center;
            font-size: 0.9rem;
            animation: shake 0.5s ease;
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }

        .demo-credentials {
            background: rgba(78, 205, 196, 0.1);
            border: 1px solid rgba(78, 205, 196, 0.3);
            border-radius: 12px;
            padding: 1rem;
            margin-top: 1.5rem;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.85rem;
        }

        .demo-credentials h4 {
            color: #4ecdc4;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }

        .demo-credentials code {
            background: rgba(255, 255, 255, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', monospace;
        }

        .back-link {
            text-align: center;
            margin-top: 2rem;
        }

        .back-link a {
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            font-size: 0.9rem;
            transition: color 0.3s ease;
        }

        .back-link a:hover {
            color: #4ecdc4;
        }

        @media (max-width: 480px) {
            .login-container {
                padding: 2rem;
                margin: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>CollabFlow</h1>
            <p>Secure Team Collaboration Platform</p>
        </div>

        {% if error %}
        <div class="error-message">
            {{ error }}
        </div>
        {% endif %}

        <form method="POST">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" placeholder="Enter your username" required>
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="Enter your password" required>
            </div>

            <button type="submit" class="login-button">Access Platform</button>
        </form>

        <div class="demo-credentials">
            <h4>Demo Accounts:</h4>
            <p><code>alice</code> / <code>alice123</code> - Team Lead</p>
            <p><code>bob</code> / <code>bob456</code> - Frontend Dev</p>
            <p><code>carol</code> / <code>carol789</code> - Backend Dev</p>
            <p><code>david</code> / <code>david321</code> - DevOps</p>
            <p><code>emma</code> / <code>emma654</code> - QA Tester</p>
        </div>

        <div class="back-link">
            <a href="/">&larr; Back to Home</a>
        </div>
    </div>
</body>
</html>
"""
if __name__ == "__main__":
    app.run(debug=True)
