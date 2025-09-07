from flask import Flask, request, render_template_string, redirect, url_for, session, make_response
import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret')

USERS = {
    "user": {"password": "password123", "role": "user"},
    "admin": {"password": "admin789", "role": "admin"},
    "alice": {"password": "alice456", "role": "user"},
}

JWT_SECRET = os.getenv('JWT_SECRET', 'fallback-jwt-secret')

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Corporate Login</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; padding: 50px; }
        .container { background: white; max-width: 400px; margin: auto; padding: 30px; border-radius: 8px; }
        h2 { margin-bottom: 20px; color: #333; }
        input { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ddd; border-radius: 4px; }
        button { width: 100%; background: #007bff; color: white; padding: 12px; border: none; border-radius: 4px; cursor: pointer; }
        .error { color: red; margin-bottom: 10px; }
        .creds { background: #f8f9fa; padding: 10px; margin-top: 15px; font-size: 12px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Login</h2>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="hidden" name="admin" value="false">
            <button type="submit">Login</button>
        </form>
        
        <div class="creds">
            <strong>Test accounts:</strong><br>
            user / password123<br>
            alice / alice456<br>
            
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <script>
        window.onload = function() {
            var isAdmin = {{ 'true' if admin_access else 'false' }};
            if (isAdmin) {
                alert("CU{auth_bypass_admin_access_pwned}");
            } else {
                alert("Access denied - Admin required");
            }
        }
    </script>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; }
        .header { background: #333; color: white; padding: 20px; }
        .content { max-width: 800px; margin: 20px auto; padding: 20px; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 5px; border-left: 3px solid #007bff; }
        .admin-card { border-left-color: #dc3545; }
        .denied { text-align: center; color: #dc3545; }
        .logout { float: right; background: #6c757d; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Corporate Dashboard</h1>
        <span>Welcome {{ user_data.username }} ({{ user_data.role }})</span>
        <a href="/logout" class="logout">Logout</a>
        <div style="clear: both;"></div>
    </div>

    <div class="content">
        <div class="card">
            <h3>Profile</h3>
            <p>Username: {{ user_data.username }}</p>
            <p>Role: {{ user_data.role }}</p>
        </div>

        <div class="card admin-card">
            <h3>Admin Panel</h3>
            {% if admin_access %}
            <p>System configuration access granted</p>
            <p>User management enabled</p>
            {% else %}
            <div class="denied">
                <h4>Access Denied</h4>
                <p>Administrative privileges required</p>
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

def generate_jwt(username, role):
    payload = {
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_jwt(token):
    try:
        header = jwt.get_unverified_header(token)
        if header.get('alg') == 'none':
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except:
        return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and USERS[username]['password'] == password:
            user_role = USERS[username]['role']
            
            session['username'] = username
            session['role'] = user_role
            
            admin_param = request.form.get('admin', 'false')
            session['admin_param_bypass'] = (admin_param == 'true')
            
            token = generate_jwt(username, user_role)
            
            resp = make_response(redirect(url_for('dashboard')))
            resp.set_cookie('auth_token', token, max_age=86400)
            resp.set_cookie('user_role', user_role, max_age=86400)
            resp.set_cookie('admin', 'false', max_age=86400)
            
            return resp
        else:
            error = "Invalid username or password"
    
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    base_role = session.get('role', 'user')
    
    step1_passed = session.get('admin_param_bypass', False)
    step2_passed = (request.cookies.get('user_role') == 'admin' and request.cookies.get('admin') == 'true')
    
    jwt_token = request.cookies.get('auth_token')
    step3_passed = False
    
    if jwt_token:
        try:
            header = jwt.get_unverified_header(jwt_token)
            if header.get('alg') == 'none':
                payload = jwt.decode(jwt_token, options={"verify_signature": False})
                if payload.get('role') == 'admin':
                    step3_passed = True
        except:
            pass
    
    admin_access = step1_passed and step2_passed and step3_passed
    display_role = 'admin' if admin_access else base_role
    
    user_data = {
        'username': username,
        'role': display_role
    }
    
    return render_template_string(
        DASHBOARD_TEMPLATE,
        user_data=user_data,
        admin_access=admin_access
    )

@app.route('/logout')
def logout():
    session.clear()
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('auth_token')
    resp.delete_cookie('user_role')
    resp.delete_cookie('admin')
    return resp

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=12520)
