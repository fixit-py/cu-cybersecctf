from flask import Flask, request, render_template_string, redirect, url_for
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file (like real applications)
load_dotenv()

# Set Flask config from environment variables (minimal, realistic approach)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-dev-key')
app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'

# Email template - VULNERABLE to SSTI
EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>CAMPAIGN_NAME - Email Campaign</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background: #f4f4f4; }
        .email-container { max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
        .email-header { background: linear-gradient(135deg, #3498db, #2980b9); color: white; padding: 30px; text-align: center; }
        .email-body { padding: 30px; }
        .highlight { background: #f39c12; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
        .message-box { background: #ecf0f1; padding: 20px; border-left: 4px solid #3498db; margin: 20px 0; border-radius: 5px; }
        .email-footer { background: #2c3e50; color: white; padding: 20px; text-align: center; font-size: 14px; }
        .signature { margin-top: 20px; font-style: italic; color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="email-header">
            <h1>Hello RECIPIENT_NAME!</h1>
            <p>Special message from MarketingPro</p>
        </div>
        <div class="email-body">
            <p>We're excited to connect with you at <span class="highlight">COMPANY_NAME</span>!</p>
            
            <div class="message-box">
                CUSTOM_MESSAGE
            </div>
            
            <p>This email is part of our <strong>CAMPAIGN_NAME</strong> campaign.</p>
            
            <div class="signature">
                <p>Best regards,<br>
                The MarketingPro Team<br>
                <small>Automated Email System</small></p>
            </div>
        </div>
        <div class="email-footer">
            <p>&copy; 2024 MarketingPro Solutions | Professional Email Marketing</p>
        </div>
    </div>
</body>
</html>
"""

MAIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MarketingPro - Email Campaign Builder</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .main-container {
            max-width: 1400px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 400px 1fr;
            gap: 30px;
            align-items: start;
        }
        .control-panel {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
            overflow: hidden;
            position: sticky;
            top: 20px;
        }
        .preview-panel {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
            overflow: hidden;
        }
        .panel-header {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 25px;
            text-align: center;
        }
        .panel-header h1 {
            font-size: 1.8em;
            font-weight: 300;
            margin-bottom: 8px;
        }
        .panel-header p {
            opacity: 0.9;
            font-size: 14px;
        }
        .panel-body {
            padding: 25px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            color: #2c3e50;
            font-weight: 600;
            margin-bottom: 6px;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.9);
        }
        .form-group input:focus, .form-group textarea:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
            background: white;
        }
        .form-group textarea {
            min-height: 80px;
            resize: vertical;
            font-family: inherit;
        }
        .generate-btn {
            width: 100%;
            background: linear-gradient(135deg, #e67e22, #d35400);
            color: white;
            border: none;
            padding: 14px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
        }
        .generate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(230, 126, 34, 0.3);
        }
        .send-btn {
            width: 100%;
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
            border: none;
            padding: 14px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .send-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(39, 174, 96, 0.3);
        }
        .send-btn:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .preview-container {
            background: #f8f9fa;
            min-height: 500px;
            overflow: auto;
            padding: 0;
        }
        .hint-box {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 12px;
            text-align: center;
        }
        .hint-box strong {
            color: #d68910;
            display: block;
            margin-bottom: 8px;
            font-size: 13px;
        }
        .hint-box code {
            background: #f8d7da;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
        }
        .success-message {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 12px;
            border-radius: 6px;
            margin-top: 15px;
            text-align: center;
            font-size: 14px;
        }
        .empty-preview {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 500px;
            color: #7f8c8d;
            text-align: center;
        }
        .env-note {
            background: #e3f2fd;
            border: 1px solid #90caf9;
            color: #1565c0;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-size: 12px;
        }
        @media (max-width: 1024px) {
            .main-container {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            .control-panel {
                position: static;
            }
        }
    </style>
</head>
<body>
    <div class="main-container">
        <!-- Control Panel -->
        <div class="control-panel">
            <div class="panel-header">
                <h1>Email Builder</h1>
                <p>Create Professional Campaigns</p>
            </div>
            <div class="panel-body">
                <form method="POST" action="/">
                    <div class="form-group">
                        <label for="campaign_name">Campaign Name</label>
                        <input type="text" id="campaign_name" name="campaign_name"
                               placeholder="Summer Sale 2024"
                               value="{{ request.form.get('campaign_name', '') }}" required>
                    </div>

                    <div class="form-group">
                        <label for="recipient_name">Recipient Name</label>
                        <input type="text" id="recipient_name" name="recipient_name"
                               placeholder="John Doe"
                               value="{{ request.form.get('recipient_name', '') }}" required>
                    </div>

                    <div class="form-group">
                        <label for="company_name">Company Name</label>
                        <input type="text" id="company_name" name="company_name"
                               placeholder="Tech Solutions LLC"
                               value="{{ request.form.get('company_name', '') }}" required>
                    </div>

                    <div class="form-group">
                        <label for="custom_message">Custom Message</label>
                        <textarea id="custom_message" name="custom_message"
                                  placeholder="Your personalized message...">{{ request.form.get('custom_message', '') }}</textarea>
                    </div>

                    <button type="submit" name="action" value="generate" class="generate-btn">
                        Generate Preview
                    </button>
                </form>

            </div>
        </div>

        <!-- Preview Panel -->
        <div class="preview-panel">
            <div class="panel-header">
                <h1>Live Preview</h1>
                <p>Email campaign preview</p>
            </div>
            <div class="preview-container">
                {% if email_content %}
                    {{ email_content | safe }}
                {% else %}
                <div class="empty-preview">
                    <div>
                        <h3>Email Preview</h3>
                        <p>Generate preview to see your email campaign</p>
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    email_content = ""
    email_generated = False

    if request.method == "POST":
        campaign_name = request.form.get("campaign_name", "")
        recipient_name = request.form.get("recipient_name", "")
        company_name = request.form.get("company_name", "")
        custom_message = request.form.get("custom_message", "")
        action = request.form.get("action", "")

        if action == "generate":
            try:
                # Comprehensive filter to block most SSTI attacks
                # Only allow specific payloads: url_for.__globals__.os.environ and get_flashed_messages.__globals__.os.environ
                blocked_keywords = [
                    # Direct access attempts
                    'config', 'request', 'CONFIG', 'REQUEST',
                    
                    # Hex encoded versions (single backslash - what actually appears in input)
                    '\\x63\\x6f\\x6e\\x66\\x69\\x67',  # config
                    '\\x43\\x4f\\x4e\\x46\\x49\\x47',  # CONFIG
                    '\\x72\\x65\\x71\\x75\\x65\\x73\\x74',  # request
                    '\\x52\\x45\\x51\\x55\\x45\\x53\\x54',  # REQUEST
                    # Note: We DON'T block \x5f\x5f because we need it for our intended payload
                    
                    # Unicode escapes
                    '\\u0063', '\\u006f', '\\u006e', '\\u0066', '\\u0069', '\\u0067',  # config chars
                    '\\u0072', '\\u0065', '\\u0071', '\\u0075', '\\u0073', '\\u0074',  # request chars
                    '\\u005f',  # _ character
                    
                    # Octal escapes
                    '\\143', '\\157', '\\156', '\\146', '\\151', '\\147',  # config
                    '\\162', '\\145', '\\161', '\\165', '\\163', '\\164',  # request
                    '\\137',  # _
                    
                    # Character construction
                    'chr(', 'ord(',
                    
                    # String manipulation
                    '.join', '.format', '.decode', 'b64decode',
                    
                    # Dangerous modules and methods
                    'subprocess', 'popen', 'system', 'eval', 'exec', 'import',
                    'SUBPROCESS', 'POPEN', 'SYSTEM', 'EVAL', 'EXEC', 'IMPORT',
                    
                    # Other globals access methods
                    'lipsum', 'cycler', 'namespace', 'joiner', 'range',
                    
                    # OS module dangerous methods (allow only environ)
                    'os.system', 'os.popen', 'os.spawn', 'os.exec',
                    
                    # Class traversal alternatives
                    'subclasses', 'mro', 'bases',
                    '\\x73\\x75\\x62\\x63\\x6c\\x61\\x73\\x73\\x65\\x73',  # subclasses
                    '\\x6d\\x72\\x6f',  # mro
                    '\\x69\\x6e\\x69\\x74',  # init
                    
                    # Block literal __ but allow the hex version we need
                    '__',
                ]
                message_lower = custom_message.lower()
                
                for keyword in blocked_keywords:
                    if keyword in message_lower:
                        email_content = f"""
                        <div style="padding: 20px; background: #f8d7da; color: #721c24; border-radius: 10px; margin: 20px;">
                            <h3>Content Filter Alert</h3>
                            <p>Your message contains restricted content and cannot be processed.</p>
                            <p>Please revise your message and try again.</p>
                        </div>
                        """
                        email_generated = True
                        # Use redirect to prevent POST resubmission issues
                        return redirect(url_for('index') + '?error=filtered')

                # Safe replacement for non-vulnerable fields (no template rendering)
                template_with_data = EMAIL_TEMPLATE.replace("CAMPAIGN_NAME", campaign_name.replace('{', '').replace('}', ''))
                template_with_data = template_with_data.replace("RECIPIENT_NAME", recipient_name.replace('{', '').replace('}', ''))
                template_with_data = template_with_data.replace("COMPANY_NAME", company_name.replace('{', '').replace('}', ''))
                
                # VULNERABLE: Only custom message field has SSTI vulnerability
                template_with_data = template_with_data.replace("CUSTOM_MESSAGE", custom_message)

                # SSTI vulnerability - only affects custom message field
                email_content = render_template_string(template_with_data)
                email_generated = True

            except Exception as e:
                email_content = f"""
                <div style="padding: 20px; background: #f8d7da; color: #721c24; border-radius: 10px; margin: 20px;">
                    <h3>Template Processing Error</h3>
                    <p><strong>Error:</strong> {str(e)}</p>
                    <p>Please check your message content and try again.</p>
                </div>
                """
                email_generated = True

    # Handle GET requests with error parameter
    error_filtered = request.args.get('error') == 'filtered'
    if error_filtered:
        email_content = """
        <div style="padding: 20px; background: #f8d7da; color: #721c24; border-radius: 10px; margin: 20px;">
            <h3>Content Filter Alert</h3>
            <p>Your message contains restricted content and cannot be processed.</p>
            <p>Please revise your message and try again.</p>
        </div>
        """
        email_generated = True

    return render_template_string(
        MAIN_TEMPLATE,
        email_content=email_content,
        email_generated=email_generated
    )

@app.route("/setup")
def setup_guide():
    return """
    <div style="font-family: Arial, sans-serif; padding: 30px; background: #f8f9fa; max-width: 900px; margin: auto;">
        <h1>MarketingPro Setup Guide</h1>
        
        <h2>Required .env File</h2>
        <p>Create a <code>.env</code> file in your project root with:</p>
        
        <div style="background: #2c3e50; color: #2ecc71; padding: 20px; border-radius: 8px; margin: 20px 0; font-family: 'Courier New', monospace;">
# Flask Email Template App Configuration
SECRET_KEY=flask_app_secret_2024
FLAG=FLAG{ssti_template_injection_discovered}
DEBUG=True
        </div>
        
        <h2>Installation Steps</h2>
        <ol style="line-height: 2;">
            <li><code>pip install flask python-dotenv</code></li>
            <li>Create the <code>.env</code> file above</li>
            <li><code>python app.py</code></li>
            <li>Visit <code>http://localhost:5000</code></li>
        </ol>
        
        <h2>Challenge Goal</h2>
        <p>The FLAG is stored in the <code>.env</code> file as an environment variable.</p>
        <p>Use Server-Side Template Injection (SSTI) to extract it from the environment!</p>
        
        <h2>SSTI Testing</h2>
        <ul style="line-height: 1.8;">
            <li><code>{{7*7}}</code> - Test basic template injection</li>
            <li><code>{{request.environ}}</code> - Access environment variables</li>
            <li><code>{{request.environ.FLAG}}</code> - Get the flag directly</li>
        </ul>
        
        <div style="background: #fff3cd; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #f39c12;">
            <strong>Security Note:</strong> This demonstrates why user input should never be directly 
            inserted into template strings. Always sanitize and validate input before template rendering!
        </div>
        
        <a href="/" style="color: #3498db; text-decoration: none;">Back to Email Builder</a>
    </div>
    """

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=7000)
