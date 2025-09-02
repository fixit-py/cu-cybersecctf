from flask import Flask, request, render_template_string
import subprocess
import random

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ShipFast Order Tracker</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 500px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #2c3e50;
            margin: 0 0 10px 0;
        }
        .header p {
            color: #7f8c8d;
            margin: 0;
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
            font-size: 16px;
            box-sizing: border-box;
        }
        input:focus {
            outline: none;
            border-color: #3498db;
        }
        .btn {
            width: 100%;
            background: #3498db;
            color: white;
            padding: 15px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            font-weight: bold;
        }
        .btn:hover {
            background: #2980b9;
        }
        .result {
            margin-top: 30px;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        .result h3 {
            margin: 0 0 15px 0;
            color: #2c3e50;
        }
        .order-info {
            background: white;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
        }
        .label {
            font-weight: bold;
            color: #2c3e50;
        }
        .value {
            color: #7f8c8d;
            font-family: monospace;
        }
        .command-output {
            background: #2c3e50;
            color: #2ecc71;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 14px;
            max-height: 200px;
            overflow-y: auto;
            margin: 15px 0;
            white-space: pre-wrap;
        }
        .hint {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            text-align: center;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ShipFast Tracker</h1>
            <p>Track your orders</p>
        </div>

        <form method="POST">
            <div class="form-group">
                <label>Order ID (max 6 chars):</label>
                <input type="text" name="order_id" maxlength="6" required>
            </div>

            <div class="form-group">
                <label>Email:</label>
                <input type="email" name="email" required>
            </div>

            <div class="form-group">
                <label>Postal Code:</label>
                <input type="text" name="postal_code" required>
            </div>

            <div class="form-group">
                <label>Phone:</label>
                <input type="tel" name="phone" required>
            </div>

            <button type="submit" class="btn">Track Order</button>
        </form>

        {% if result %}
        <div class="result">
            <h3>Order Status</h3>
            <p>{{ result }}</p>
            
            <div class="order-info">
                <div class="info-row">
                    <span class="label">Order ID:</span>
                    <span class="value">{{ order_data.order_id }}</span>
                </div>
                <div class="info-row">
                    <span class="label">Email:</span>
                    <span class="value">{{ order_data.email }}</span>
                </div>
                <div class="info-row">
                    <span class="label">Postal:</span>
                    <span class="value">{{ order_data.postal }}</span>
                </div>
                <div class="info-row">
                    <span class="label">Phone:</span>
                    <span class="value">{{ order_data.phone }}</span>
                </div>
            </div>

            {% if expected_days %}
            <p><strong>Delivery:</strong> {{ expected_days }} business days</p>
            {% endif %}

            {% if command_output %}
            <div class="command-output">{{ command_output }}</div>
            {% endif %}
        </div>
        {% endif %}

    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    command_output = ""
    expected_days = None
    order_data = {}

    if request.method == "POST":
        order_id = request.form.get("order_id", "").strip()
        email = request.form.get("email", "").strip()
        postal = request.form.get("postal_code", "").strip()
        phone = request.form.get("phone", "").strip()

        # Enforce 6 character limit
        if len(order_id) > 6:
            order_id = order_id[:6]

        order_data = {
            "order_id": order_id,
            "email": email,
            "postal": postal,
            "phone": phone
        }

        # Command injection vulnerability
        allowed_commands = ["ls", "pwd", "whoami", "ps", "cat"]
        command_executed = False

        if order_id in allowed_commands:
            try:
                if order_id == "ps":
                    cmd = "ps aux"
                elif order_id == "cat":
                    if postal:
                        cmd = f"cat {postal}"
                    else:
                        command_output = "Error: cat requires postal code as filename"
                        command_executed = True
                        cmd = None
                else:
                    cmd = order_id

                if cmd:
                    output = subprocess.check_output(
                        cmd, shell=True, stderr=subprocess.STDOUT, text=True, timeout=10
                    )
                    command_output = output
                    command_executed = True

            except subprocess.CalledProcessError as e:
                command_output = f"Command failed: {e.output}"
                command_executed = True
            except Exception as e:
                command_output = f"Error: {str(e)}"
                command_executed = True

        # Show order status
        if command_executed:
            result = f"Processing order {order_id}..."
        else:
            statuses = ["Processing", "Shipped", "In Transit", "Delivered"]
            result = f"Order {order_id} status: {random.choice(statuses)}"

        expected_days = random.randint(1, 5)

    return render_template_string(
        TEMPLATE,
        result=result,
        command_output=command_output,
        expected_days=expected_days,
        order_data=order_data
    )

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=12700)
