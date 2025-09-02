from flask import Flask, render_template_string, request, redirect, session, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"

# --- Credential setup ---
VALID_USER = "admin"
VALID_PASS = "SuperSecret123!"

# Enhanced username list of 20
FAKE_USERS = [
    "alice", "bob", "charlie", "diana", "edward", "fiona", "george", "helen",
    "ivan", "julia", "kevin", "laura", "michael", "nancy", "oscar", "petra",
    "quinn", "rachel", "steve", "tina"
]

# Enhanced password list of 100
FAKE_PASSWORDS = [
    "password123", "123456", "admin", "letmein", "welcome", "monkey", "dragon",
    "qwerty", "master", "sunshine", "iloveyou", "princess", "football", "charlie",
    "aa123456", "donald", "password1", "qwerty123", "solo", "1qaz2wsx",
    "shadow", "michael", "superman", "photoshop", "1234567890", "mustang",
    "jordan23", "robert", "matthew", "daniel", "hannah", "michelle", "thomas",
    "hunter", "taylor", "jessica", "nicholas", "anthony", "joshua", "freedom",
    "amanda", "orange", "kevin", "mickey", "liverpool", "banana", "tennis",
    "chelsea", "diamond", "nascar", "jackson", "cameron", "654321", "computer",
    "phoenix", "patrick", "mickey", "bailey", "knight", "iceman", "tigers",
    "purple", "andrea", "hornet", "dakota", "aaaaaa", "player", "sunshine",
    "morgan", "starwars", "boomer", "cowboys", "edward", "charles", "girls",
    "booboo", "coffee", "xxxxxx", "bulldog", "ncc1701", "rabbit", "peanut",
    "john", "johnny", "gandalf", "spanky", "winter", "brandy", "compaq", "carlos",
    "tennis", "james", "mike", "brandon", "fender", "anthony", "blowme", "ferrari",
    "cookie", "chicken", "maverick", "chicago", "joseph", "diablo", "sexsex",
    "hardcore", "willie", "welcome1", "chris", "panther"
]

ALL_USERS = [VALID_USER] + FAKE_USERS
ALL_PASSWORDS = [VALID_PASS] + FAKE_PASSWORDS

# --- Rate limiting setup ---
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri="redis://localhost:6379",
    default_limits=["20 per minute"]
)

# --- Enhanced Templates ---
login_template = """
<!DOCTYPE html>
<html>
<head>
    <title>SecureLogin Portal</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            display: flex; 
            align-items: center; 
            justify-content: center;
            padding: 20px;
        }
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            padding: 50px 40px;
            border-radius: 20px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            color: #2c3e50;
            font-size: 2.2em;
            font-weight: 300;
            margin-bottom: 10px;
        }
        .logo p {
            color: #7f8c8d;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 25px;
            position: relative;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 16px 20px;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.9);
        }
        input[type="text"]:focus, input[type="password"]:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 4px rgba(52, 152, 219, 0.1);
            background: white;
        }
        input::placeholder {
            color: #a0a6b0;
        }
        .login-btn {
            width: 100%;
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 16px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 10px;
        }
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(52, 152, 219, 0.3);
        }
        .login-btn:active {
            transform: translateY(0);
        }
        .error {
            background: #fee;
            border: 1px solid #fcc;
            color: #c33;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            text-align: center;
        }
        .hint {
            text-align: center;
            margin-top: 25px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            font-size: 13px;
            color: #6c757d;
        }
        .rate-limit-info {
            text-align: center;
            margin-top: 15px;
            font-size: 12px;
            color: #95a5a6;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>🔐 SecureLogin</h1>
            <p>Enterprise Security Portal</p>
        </div>
        
        {% if error %}
            <div class="error">
                ⚠️ {{ error }}
            </div>
        {% endif %}
        
        <form method="POST" action="/login">
            <div class="form-group">
                <input type="text" name="username" placeholder="Enter username" required>
            </div>
            <div class="form-group">
                <input type="password" name="password" placeholder="Enter password" required>
            </div>
            <button type="submit" class="login-btn">Sign In</button>
        </form>
        
        <div class="hint">
            💡 <strong>Demo Hint:</strong> Try different username/password combinations to see varying error messages
        </div>
        
        <div class="rate-limit-info">
            🛡️ Protected by rate limiting (5 attempts per minute)
        </div>
    </div>
</body>
</html>
"""

home_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Welcome - SecureLogin Portal</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            display: flex; 
            align-items: center; 
            justify-content: center;
            padding: 20px;
        }
        .home-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            padding: 50px 40px;
            border-radius: 20px;
            text-align: center;
            max-width: 500px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        h1 {
            color: #2c3e50;
            font-size: 2.2em;
            margin-bottom: 20px;
            font-weight: 300;
        }
        .user-badge {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 30px;
        }
        .welcome-msg {
            color: #2c3e50;
            font-size: 1.1em;
            margin-bottom: 30px;
            line-height: 1.6;
        }
        .logout-btn {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 25px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }
        .logout-btn:hover {
            transform: scale(1.05);
            text-decoration: none;
        }
    </style>
    <script>
        window.onload = function() {
            alert("🎉 FLAG{user_enum_success_2024} 🎉\\n\\nCongratulations! You successfully exploited the username enumeration vulnerability!");
        }
    </script>
</head>
<body>
    <div class="home-container">
        <h1>🔐 Welcome!</h1>
        <div class="user-badge">{{ user }}</div>
        <div class="welcome-msg">
            You have successfully logged into the SecureLogin Portal.<br>
            The system has authenticated your credentials and granted access.
        </div>
        <a href="/logout" class="logout-btn">🚪 Logout</a>
    </div>
</body>
</html>
"""

# --- Routes ---
@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
@limiter.limit("5 per minute", key_func=lambda: request.form.get("username", ""))
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Case 1: Correct user, wrong pass (gives "or" - username enumeration vulnerability)
        if username == VALID_USER and password != VALID_PASS:
            error = "Username or password not valid."
        # Case 2: Both wrong (gives "and")
        elif username not in ALL_USERS and password not in ALL_PASSWORDS:
            error = "Username and password not valid."
        # Case 3: Correct login - redirect to home
        elif username == VALID_USER and password == VALID_PASS:
            session["user"] = username
            return redirect(url_for("home"))
        # Case 4: Other combos (valid username but fake password, etc.)
        else:
            error = "Username and password not valid."
    
    return render_template_string(login_template, error=error)

@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    
    return render_template_string(home_template, user=session["user"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Debug endpoint to show all credentials (remove in production!)
@app.route("/debug")
def debug():
    if "user" not in session:
        return redirect(url_for("login"))
    
    debug_template = """
    <div style="font-family: monospace; padding: 20px; background: #f8f9fa;">
        <h2>Debug - All Credentials</h2>
        <h3>Valid Login:</h3>
        <p><strong>Username:</strong> {{ valid_user }}<br><strong>Password:</strong> {{ valid_pass }}</p>
        
        <h3>All Usernames ({{ user_count }}):</h3>
        <div style="columns: 4; column-gap: 20px;">
        {% for user in all_users %}
            <div>{{ user }}</div>
        {% endfor %}
        </div>
        
        <h3>All Passwords ({{ pass_count }}):</h3>
        <div style="columns: 4; column-gap: 20px; max-height: 400px; overflow-y: auto;">
        {% for password in all_passwords %}
            <div>{{ password }}</div>
        {% endfor %}
        </div>
        
        <a href="/home" style="margin-top: 20px; display: inline-block;">Back to Home</a>
    </div>
    """
    
    return render_template_string(
        debug_template,
        valid_user=VALID_USER,
        valid_pass=VALID_PASS,
        all_users=ALL_USERS,
        all_passwords=ALL_PASSWORDS,
        user_count=len(ALL_USERS),
        pass_count=len(ALL_PASSWORDS)
    )

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=17800)
