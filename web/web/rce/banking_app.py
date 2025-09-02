from flask import Flask, request, render_template_string, session, redirect, url_for, jsonify
import os
import time
from dotenv import load_dotenv
import threading
import uuid
import sqlite3
import hashlib
from datetime import datetime

app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv('SECRET_KEY', 'secure-banking-secret-2024')

# Database initialization
def init_db():
    conn = sqlite3.connect('banking.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            balance REAL DEFAULT 1000.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            recipient TEXT,
            amount REAL,
            note TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

account_lock = threading.Lock()

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SecureBank - Login</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0; 
            padding: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container { 
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 400px;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }
        .logo p {
            color: #7f8c8d;
            margin: 5px 0 0 0;
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 5px; 
            font-weight: bold;
            color: #2c3e50;
        }
        input { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #ecf0f1; 
            border-radius: 5px; 
            box-sizing: border-box;
            font-size: 16px;
        }
        input:focus {
            outline: none;
            border-color: #3498db;
        }
        .btn { 
            width: 100%;
            background: #3498db; 
            color: white; 
            padding: 12px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px;
            margin-bottom: 15px;
        }
        .btn:hover { background: #2980b9; }
        .btn-register { background: #2ecc71; }
        .btn-register:hover { background: #27ae60; }
        .alert { 
            padding: 12px; 
            border-radius: 5px; 
            margin-bottom: 20px; 
            text-align: center;
        }
        .alert-error { background: #f8d7da; color: #721c24; }
        .alert-success { background: #d4edda; color: #155724; }
        .divider {
            text-align: center;
            margin: 20px 0;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>SecureBank</h1>
            <p>Online Banking Portal</p>
        </div>
        
        {% if message %}
        <div class="alert {{ 'alert-success' if success else 'alert-error' }}">
            {{ message }}
        </div>
        {% endif %}
        
        <form method="POST" action="{{ '/register' if register_mode else '/login' }}">
            {% if register_mode %}
            <div class="form-group">
                <label>Full Name:</label>
                <input type="text" name="name" required placeholder="Enter your full name">
            </div>
            {% endif %}
            
            <div class="form-group">
                <label>Username:</label>
                <input type="text" name="username" required placeholder="Enter username">
            </div>
            
            <div class="form-group">
                <label>Password:</label>
                <input type="password" name="password" required placeholder="Enter password">
            </div>
            
            {% if register_mode %}
            <button type="submit" class="btn btn-register">Create Account</button>
            <div class="divider">Already have an account?</div>
            <a href="/login" class="btn" style="text-decoration: none; display: block; text-align: center;">Login</a>
            {% else %}
            <button type="submit" class="btn">Login</button>
            <div class="divider">Don't have an account?</div>
            <a href="/register" class="btn btn-register" style="text-decoration: none; display: block; text-align: center;">Create Account</a>
            {% endif %}
        </form>
    </div>
</body>
</html>
"""

BANKING_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SecureBank - Dashboard</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: #f5f5f5; 
            margin: 0; 
            padding: 20px; 
        }
        .container { 
            max-width: 800px; 
            margin: auto; 
            background: white; 
            border-radius: 8px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        .header { 
            background: #2c3e50; 
            color: white; 
            padding: 20px 30px; 
            border-radius: 8px 8px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { margin: 0; }
        .logout { 
            background: #e74c3c; 
            color: white; 
            text-decoration: none; 
            padding: 8px 15px; 
            border-radius: 4px; 
            font-size: 14px;
        }
        .content { padding: 30px; }
        .balance { 
            background: #ecf0f1; 
            padding: 20px; 
            border-radius: 5px; 
            text-align: center; 
            margin-bottom: 30px; 
        }
        .balance-amount { 
            font-size: 2.5em; 
            color: #2c3e50; 
            margin: 10px 0; 
        }
        .transfer-section { 
            background: #f8f9fa; 
            padding: 25px; 
            border-radius: 5px; 
            margin-bottom: 30px; 
        }
        .form-group { margin-bottom: 15px; }
        label { 
            display: block; 
            margin-bottom: 5px; 
            font-weight: bold; 
        }
        input, select { 
            width: 100%; 
            padding: 10px; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            box-sizing: border-box; 
        }
        .btn { 
            background: #3498db; 
            color: white; 
            padding: 12px 25px; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer; 
            font-size: 16px; 
        }
        .btn:hover { background: #2980b9; }
        .btn-reset { background: #95a5a6; }
        .transactions { 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 5px; 
        }
        .transaction { 
            padding: 12px 0; 
            border-bottom: 1px solid #eee; 
            display: flex; 
            justify-content: space-between; 
        }
        .flag { 
            background: #f39c12; 
            color: white; 
            padding: 15px; 
            text-align: center; 
            border-radius: 5px; 
            margin: 20px 0; 
            font-family: monospace; 
            font-size: 18px;
        }
        .alert { 
            padding: 12px; 
            border-radius: 4px; 
            margin: 15px 0; 
        }
        .alert-success { background: #d4edda; color: #155724; }
        .alert-error { background: #f8d7da; color: #721c24; }
        .user-info {
            font-size: 14px;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>SecureBank</h1>
                <div class="user-info">Welcome, {{ user.name }}</div>
            </div>
            <a href="/logout" class="logout">Logout</a>
        </div>
        
        <div class="content">
            <div class="balance">
                <h3>Account Balance</h3>
                <div class="balance-amount">${{ user.balance|round(2) }}</div>
                <p>Account: {{ user.username }}</p>
            </div>
            
            <div class="transfer-section">
                <h3>Transfer Money</h3>
                <form method="POST" action="/transfer">
                    <div class="form-group">
                        <label>To Account:</label>
                        <select name="recipient" required>
                            <option value="">Select recipient...</option>
                            <option value="savings_account">Savings Account</option>
                            <option value="business_account">Business Account</option>
                            <option value="external_bank">External Bank</option>
                            <option value="investment_fund">Investment Fund</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Amount ($):</label>
                        <input type="number" name="amount" min="1" step="0.01" required>
                    </div>
                    <div class="form-group">
                        <label>Reference:</label>
                        <input type="text" name="note" placeholder="Payment reference">
                    </div>
                    <button type="submit" class="btn">Transfer</button>
                </form>
            </div>
            
            {% if user.balance <= -1000 %}
            <div class="flag">
                🎉 FLAG{race_condition_banking_master} 🎉
            </div>
            {% endif %}
            
            <div class="transactions">
                <h3>Recent Transactions</h3>
                {% for txn in transactions %}
                <div class="transaction">
                    <div>
                        <strong>${{ txn.amount|round(2) }}</strong> to {{ txn.recipient }}
                        <br><small>{{ txn.note }}</small>
                    </div>
                    <div>{{ txn.time }}</div>
                </div>
                {% else %}
                <p>No recent transactions</p>
                {% endfor %}
            </div>
            
            {% if message %}
            <div class="alert {{ 'alert-success' if success else 'alert-error' }}">
                {{ message }}
            </div>
            {% endif %}
            
            <div style="margin-top: 30px;">
                <form method="POST" action="/reset" style="display: inline;">
                    <button type="submit" class="btn btn-reset">Reset Balance</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
"""

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db():
    conn = sqlite3.connect('banking.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not user:
        session.clear()
        conn.close()
        return redirect(url_for('login'))
    
    # Convert user data to dict and ensure balance is float
    user_data = dict(user)
    user_data['balance'] = float(user_data['balance'])
    
    # Get recent transactions
    transactions = conn.execute(
        'SELECT recipient, amount, note, datetime(timestamp) as formatted_time FROM transactions WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10',
        (session['user_id'],)
    ).fetchall()
    
    # Convert transactions to list of dicts for easier template access
    transaction_list = []
    for txn in transactions:
        transaction_list.append({
            'recipient': txn[0],
            'amount': float(txn[1]),
            'note': txn[2] or 'No reference',
            'time': txn[3]
        })
    
    conn.close()
    
    message = request.args.get('message')
    success = request.args.get('success') == 'true'
    
    return render_template_string(BANKING_TEMPLATE,
                                user=user_data,
                                transactions=transaction_list,
                                message=message,
                                success=success)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template_string(LOGIN_TEMPLATE, 
                                        message='Please enter both username and password',
                                        success=False)
        
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, hash_password(password))
        ).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        else:
            return render_template_string(LOGIN_TEMPLATE,
                                        message='Invalid username or password',
                                        success=False)
    
    return render_template_string(LOGIN_TEMPLATE, register_mode=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not all([name, username, password]):
            return render_template_string(LOGIN_TEMPLATE,
                                        register_mode=True,
                                        message='Please fill in all fields',
                                        success=False)
        
        if len(password) < 4:
            return render_template_string(LOGIN_TEMPLATE,
                                        register_mode=True,
                                        message='Password must be at least 4 characters',
                                        success=False)
        
        conn = get_db()
        
        # Check if username exists
        existing_user = conn.execute(
            'SELECT id FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        if existing_user:
            conn.close()
            return render_template_string(LOGIN_TEMPLATE,
                                        register_mode=True,
                                        message='Username already exists',
                                        success=False)
        
        # Create new user
        try:
            conn.execute(
                'INSERT INTO users (username, password, name) VALUES (?, ?, ?)',
                (username, hash_password(password), name)
            )
            conn.commit()
            conn.close()
            
            return render_template_string(LOGIN_TEMPLATE,
                                        message='Account created successfully! Please login.',
                                        success=True)
        except Exception as e:
            conn.close()
            return render_template_string(LOGIN_TEMPLATE,
                                        register_mode=True,
                                        message='Error creating account. Please try again.',
                                        success=False)
    
    return render_template_string(LOGIN_TEMPLATE, register_mode=True)

@app.route('/transfer', methods=['POST'])
def transfer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    recipient = request.form.get('recipient')
    note = request.form.get('note', 'Transfer')
    
    # Safely convert amount to float with error handling
    try:
        amount_str = request.form.get('amount', '0')
        amount = float(amount_str)
    except (ValueError, TypeError):
        return redirect(url_for('index', message='Invalid amount format', success='false'))
    
    if amount <= 0:
        return redirect(url_for('index', message='Amount must be greater than 0', success='false'))
    
    if not recipient:
        return redirect(url_for('index', message='Please select a recipient', success='false'))
    
    conn = get_db()
    
    try:
        # VULNERABLE: Race condition between check and deduct
        user = conn.execute('SELECT balance FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        
        if not user:
            conn.close()
            return redirect(url_for('login'))
        
        current_balance = float(user['balance'])
        
        if current_balance < amount:
            conn.close()
            return redirect(url_for('index', message='Insufficient funds', success='false'))
        
        # Processing delay (makes race condition exploitable)
        time.sleep(0.05)
        
        # Deduct amount (vulnerable - not atomic with balance check)
        conn.execute(
            'UPDATE users SET balance = balance - ? WHERE id = ?',
            (amount, session['user_id'])
        )
        
        # Record transaction
        conn.execute(
            'INSERT INTO transactions (user_id, recipient, amount, note) VALUES (?, ?, ?, ?)',
            (session['user_id'], recipient, amount, note)
        )
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('index', message=f'Transferred ${amount:.2f}', success='true'))
        
    except Exception as e:
        conn.close()
        return redirect(url_for('index', message='Transfer failed. Please try again.', success='false'))

@app.route('/reset', methods=['POST'])
def reset():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    conn.execute('UPDATE users SET balance = 1000 WHERE id = ?', (session['user_id'],))
    conn.execute('DELETE FROM transactions WHERE user_id = ?', (session['user_id'],))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index', message='Balance reset to $1000.00', success='true'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/balance')
def api_balance():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    user = conn.execute('SELECT balance FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    if user:
        balance = float(user['balance'])
        return jsonify({'balance': balance})
    else:
        return jsonify({'balance': 0})

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0', port=20000)
