from flask import Flask, request, redirect, url_for, render_template_string
import random

app = Flask(__name__)

# Mock current user
current_user = "fixit"

# Mock database
receipts = []

# Generate random starting receipt IDs
used_ids = set()
def generate_receipt_id(fixed_id=None):
    if fixed_id:
        used_ids.add(fixed_id)
        return fixed_id
    while True:
        rid = str(random.randint(1, 1999)).zfill(4)
        if rid not in used_ids:
            used_ids.add(rid)
            return rid

# Pre-populate with mock receipts
mock_data = [
    ("SuperMart", "Downtown", "Ottawa", [("Milk", 5), ("Bread", 3), ("Eggs", 4)], "Great quality!", True),
    ("TechWorld", "Mall", "Toronto", [("Headphones", 30)], "Too pricey", True),
    ("GreenGrocers", "Main Street", "Ottawa", [("Bananas", 5), ("Apples", 7), ("Grapes", 3)], "Very fresh!", True),
    ("ElectroHub", "West End", "Montreal", [("Laptop Stand", 45)], "Sturdy stand", False),
    ("PizzaPlace", "Rideau", "Ottawa", [("Pizza", 18)], "Delicious", True),
]

# Hidden flag receipt with fixed ID
flag_receipt = {
    "id": "99",
    "store": "CU",
    "branch": "Hidden",
    "location": "Nowhere",
    "items": [("FLAG{idor_pwned}", 0)],
    "feedback": "You found it!",
    "public": False,
    "owner": None
}
receipts.append(flag_receipt)

for store, branch, location, items, feedback, is_public in mock_data:
    receipts.append({
        "id": generate_receipt_id(),
        "store": store,
        "branch": branch,
        "location": location,
        "items": items,
        "feedback": feedback,
        "public": is_public,
        "owner": None
    })

# Enhanced dashboard template
DASHBOARD_TEMPLATE = """
<style>
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; min-height: 100vh; }
.container { max-width: 1200px; margin: auto; }
.header { background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); border-radius: 20px; padding: 30px; margin-bottom: 30px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
h1 { margin: 0; color: #2c3e50; font-size: 2.5em; font-weight: 300; }
h2 { color: #34495e; margin: 30px 0 20px 0; font-weight: 400; }
.section { background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); border-radius: 15px; padding: 25px; margin-bottom: 25px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
.receipt-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.receipt-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); transition: all 0.3s ease; border: 1px solid rgba(0,0,0,0.05); }
.receipt-card:hover { transform: translateY(-5px); box-shadow: 0 8px 30px rgba(0,0,0,0.15); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.receipt-id { font-weight: 600; color: #2c3e50; font-size: 1.1em; }
.badge { padding: 6px 12px; border-radius: 20px; font-size: 11px; color: white; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.public { background: linear-gradient(135deg, #27ae60, #2ecc71); }
.private { background: linear-gradient(135deg, #e74c3c, #c0392b); }
.store-info { color: #7f8c8d; margin-bottom: 15px; line-height: 1.4; }
.store-name { font-weight: 500; color: #34495e; }
.view-btn { display: inline-block; background: linear-gradient(135deg, #3498db, #2980b9); color: white; padding: 10px 20px; border-radius: 25px; text-decoration: none; font-weight: 500; transition: all 0.3s ease; font-size: 14px; }
.view-btn:hover { transform: scale(1.05); box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4); text-decoration: none; }
.add-receipt-btn { display: inline-block; background: linear-gradient(135deg, #e67e22, #d35400); color: white; padding: 15px 30px; border-radius: 30px; text-decoration: none; font-weight: 600; margin-top: 20px; transition: all 0.3s ease; }
.add-receipt-btn:hover { transform: scale(1.05); box-shadow: 0 5px 20px rgba(230, 126, 34, 0.4); text-decoration: none; }
.empty-state { text-align: center; color: #7f8c8d; padding: 40px 20px; font-style: italic; }
</style>

<div class="container">
  <div class="header">
    <h1>🧾 Receipt Dashboard</h1>
  </div>

  <div class="section">
    <h2>Your Receipts</h2>
    {% if user_receipts %}
    <div class="receipt-grid">
      {% for r in user_receipts %}
      <div class="receipt-card">
        <div class="card-header">
          <span class="receipt-id">Receipt #{{ r['id'] }}</span>
          <span class="badge {% if r['public'] %}public{% else %}private{% endif %}">
            {% if r['public'] %}Public{% else %}Private{% endif %}
          </span>
        </div>
        <div class="store-info">
          <div class="store-name">{{r['store']}}</div>
          <div>{{r['branch']}} • {{r['location']}}</div>
        </div>
        <a href="{{ url_for('view_receipt', receipt_id=r['id']) }}" class="view-btn">View Receipt</a>
      </div>
      {% endfor %}
    </div>
    {% else %}
    <div class="empty-state">No receipts yet. Submit your first receipt below!</div>
    {% endif %}
  </div>

  <div class="section">
    <h2>Public Receipts</h2>
    <div class="receipt-grid">
      {% for r in sample %}
      <div class="receipt-card">
        <div class="card-header">
          <span class="receipt-id">Receipt #{{ r['id'] }}</span>
          <span class="badge public">Public</span>
        </div>
        <div class="store-info">
          <div class="store-name">{{r['store']}}</div>
          <div>{{r['branch']}} • {{r['location']}}</div>
        </div>
        <a href="{{ url_for('view_receipt', receipt_id=r['id']) }}" class="view-btn">View Receipt</a>
      </div>
      {% endfor %}
    </div>
  </div>

  <div style="text-align: center;">
    <a href="{{url_for('add_receipt')}}" class="add-receipt-btn">📝 Submit New Receipt</a>
  </div>
</div>
"""

# Enhanced receipt view template
RECEIPT_TEMPLATE = """
<style>
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; min-height: 100vh; }
.container { max-width: 700px; margin: auto; }
.receipt-detail { background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); border-radius: 20px; padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
.receipt-header { text-align: center; margin-bottom: 30px; }
.receipt-id { font-size: 2em; color: #2c3e50; margin: 0 0 15px 0; font-weight: 300; }
.badge { padding: 8px 16px; border-radius: 25px; font-size: 12px; color: white; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.public { background: linear-gradient(135deg, #27ae60, #2ecc71); }
.private { background: linear-gradient(135deg, #e74c3c, #c0392b); }
.store-section { background: #f8f9fa; padding: 20px; border-radius: 15px; margin: 25px 0; }
.store-title { font-size: 1.3em; font-weight: 600; color: #2c3e50; margin-bottom: 8px; }
.store-details { color: #6c757d; }
.items-section { margin: 25px 0; }
.items-title { font-weight: 600; color: #2c3e50; margin-bottom: 15px; font-size: 1.1em; }
.items-list { background: #f8f9fa; border-radius: 12px; padding: 20px; }
.item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e9ecef; }
.item:last-child { border-bottom: none; }
.item-name { font-weight: 500; }
.item-price { color: #28a745; font-weight: 600; }
.total { display: flex; justify-content: space-between; align-items: center; margin-top: 15px; padding-top: 15px; border-top: 2px solid #dee2e6; font-size: 1.2em; font-weight: 600; color: #2c3e50; }
.feedback-section { background: #e3f2fd; padding: 20px; border-radius: 15px; margin: 25px 0; border-left: 4px solid #2196f3; }
.feedback-title { font-weight: 600; color: #1976d2; margin-bottom: 8px; }
.feedback-text { color: #424242; font-style: italic; }
.back-btn { display: inline-block; background: linear-gradient(135deg, #6c757d, #495057); color: white; padding: 12px 25px; border-radius: 25px; text-decoration: none; font-weight: 500; margin-top: 25px; transition: all 0.3s ease; }
.back-btn:hover { transform: scale(1.05); text-decoration: none; box-shadow: 0 5px 15px rgba(108, 117, 125, 0.4); }
</style>

<div class="container">
  <div class="receipt-detail">
    <div class="receipt-header">
      <h1 class="receipt-id">Receipt #{{receipt['id']}}</h1>
      <span class="badge {% if receipt['public'] %}public{% else %}private{% endif %}">
        {% if receipt['public'] %}Public{% else %}Private{% endif %}
      </span>
    </div>

    <div class="store-section">
      <div class="store-title">{{receipt['store']}}</div>
      <div class="store-details">{{receipt['branch']}} • {{receipt['location']}}</div>
    </div>

    <div class="items-section">
      <div class="items-title">Items Purchased</div>
      <div class="items-list">
        {% for item, price in receipt['items'] %}
        <div class="item">
          <span class="item-name">{{item}}</span>
          <span class="item-price">${{price}}</span>
        </div>
        {% endfor %}
        <div class="total">
          <span>Total</span>
          <span>${{receipt['items']|map(attribute=1)|sum}}</span>
        </div>
      </div>
    </div>

    <div class="feedback-section">
      <div class="feedback-title">Customer Feedback</div>
      <div class="feedback-text">"{{receipt['feedback']}}"</div>
    </div>

    <div style="text-align: center;">
      <a href="{{url_for('index')}}" class="back-btn">← Back to Dashboard</a>
    </div>
  </div>
</div>
"""

# Enhanced form template
FORM_TEMPLATE = """
<style>
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; min-height: 100vh; }
.container { max-width: 600px; margin: auto; }
.form-card { background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); border-radius: 20px; padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
h2 { text-align: center; color: #2c3e50; margin-bottom: 30px; font-weight: 300; font-size: 2em; }
.form-group { margin-bottom: 20px; }
label { display: block; margin-bottom: 8px; color: #2c3e50; font-weight: 500; }
input[type="text"], textarea { width: 100%; padding: 12px 16px; border: 2px solid #e9ecef; border-radius: 10px; font-size: 16px; transition: all 0.3s ease; background: white; }
input[type="text"]:focus, textarea:focus { outline: none; border-color: #3498db; box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1); }
.radio-group { display: flex; gap: 20px; margin-top: 8px; }
.radio-option { display: flex; align-items: center; gap: 8px; }
input[type="radio"] { margin: 0; }
.submit-btn { background: linear-gradient(135deg, #27ae60, #2ecc71); color: white; padding: 15px 30px; border: none; border-radius: 25px; font-size: 16px; font-weight: 600; cursor: pointer; width: 100%; margin-top: 10px; transition: all 0.3s ease; }
.submit-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(39, 174, 96, 0.3); }
.back-link { display: inline-block; color: #6c757d; text-decoration: none; margin-top: 20px; font-weight: 500; }
.back-link:hover { color: #495057; text-decoration: underline; }
.help-text { font-size: 14px; color: #6c757d; margin-top: 5px; font-style: italic; }
</style>

<div class="container">
  <div class="form-card">
    <h2>📝 Submit a Receipt</h2>
    <form method="POST">
      <div class="form-group">
        <label for="store">Store Name</label>
        <input type="text" id="store" name="store" required placeholder="e.g. SuperMart">
      </div>

      <div class="form-group">
        <label for="branch">Store Branch</label>
        <input type="text" id="branch" name="branch" required placeholder="e.g. Downtown">
      </div>

      <div class="form-group">
        <label for="location">Store Location</label>
        <input type="text" id="location" name="location" required placeholder="e.g. Ottawa">
      </div>

      <div class="form-group">
        <label for="items">Receipt Items</label>
        <input type="text" id="items" name="items" required placeholder="Milk $5, Bread $3, Eggs $4" style="font-family: monospace;">
        <div class="help-text">Format: Item $Price, Item $Price (separated by commas)</div>
      </div>

      <div class="form-group">
        <label for="feedback">Your Feedback</label>
        <input type="text" id="feedback" name="feedback" required placeholder="Great quality products!">
      </div>

      <div class="form-group">
        <label>Make Receipt Public?</label>
        <div class="radio-group">
          <div class="radio-option">
            <input type="radio" id="public-yes" name="public" value="yes" checked>
            <label for="public-yes">Yes, make it public</label>
          </div>
          <div class="radio-option">
            <input type="radio" id="public-no" name="public" value="no">
            <label for="public-no">Keep it private</label>
          </div>
        </div>
      </div>

      <button type="submit" class="submit-btn">Submit Receipt</button>
    </form>

    <div style="text-align: center;">
      <a href="{{url_for('index')}}" class="back-link">← Back to Dashboard</a>
    </div>
  </div>
</div>
"""

@app.route("/")
def index():
    user_receipts = [r for r in receipts if r.get("owner") == current_user]
    public_receipts = [r for r in receipts if r["public"]]
    sample = random.sample(public_receipts, min(10, len(public_receipts)))
    return render_template_string(DASHBOARD_TEMPLATE, user_receipts=user_receipts, sample=sample)

@app.route("/receipt/<receipt_id>")
def view_receipt(receipt_id):
    for r in receipts:
        if r["id"] == receipt_id:
            return render_template_string(RECEIPT_TEMPLATE, receipt=r)
    return "Receipt not found", 404

@app.route("/add", methods=["GET", "POST"])
def add_receipt():
    if request.method == "POST":
        store = request.form["store"]
        branch = request.form["branch"]
        location = request.form["location"]
        feedback = request.form["feedback"]
        items_raw = request.form["items"]
        is_public = request.form.get("public") == "yes"

        items = []
        for entry in items_raw.split(","):
            try:
                name, price = entry.strip().rsplit(" ", 1)
                items.append((name, int(price.replace("$",""))))
            except:
                continue

        new_receipt = {
            "id": generate_receipt_id(),
            "store": store,
            "branch": branch,
            "location": location,
            "items": items,
            "feedback": feedback,
            "public": is_public,
            "owner": current_user
        }
        receipts.append(new_receipt)
        return redirect(url_for("index"))

    return render_template_string(FORM_TEMPLATE)

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=13400)
