# /api/redirect.py - FIXED VERSION with proper sanitization

from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import re

BOT_USERNAME = "PremiumtelenovelasBot"

def sanitize_for_telegram(text):
    """
    Sanitizes text to be safe for Telegram deep links.
    Only allows: letters, numbers, underscores, and hyphens.
    """
    # Replace any character that's not alphanumeric, underscore, or hyphen with underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', text)
    # Remove any consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    return sanitized

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse URL
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            
            # Convert to simple dict
            simple_params = {}
            for key, value in params.items():
                simple_params[key] = value[0] if len(value) == 1 else value
            
            # Get tx_ref from Flutterwave
            tx_ref = simple_params.get('tx_ref')
            status = simple_params.get('status', 'unknown')
            
            if not tx_ref:
                self.send_error_page("No transaction reference found")
                return
            
            # Sanitize tx_ref for Telegram deep link
            sanitized_tx_ref = sanitize_for_telegram(tx_ref)
            payload = f"verify_{sanitized_tx_ref}"
            
            # Create Telegram deep link
            telegram_url = f"https://t.me/{BOT_USERNAME}?start={payload}"
            
            # Send success page with auto-redirect
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Payment Processing</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ 
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                    }}
                    .container {{ 
                        background: rgba(255, 255, 255, 0.95);
                        padding: 40px;
                        border-radius: 16px;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                        max-width: 500px;
                        text-align: center;
                        color: #333;
                    }}
                    .success-icon {{
                        font-size: 64px;
                        margin-bottom: 20px;
                    }}
                    h1 {{
                        color: #2c3e50;
                        margin-bottom: 10px;
                    }}
                    .status {{
                        display: inline-block;
                        padding: 8px 16px;
                        background: #4caf50;
                        color: white;
                        border-radius: 20px;
                        margin: 15px 0;
                        font-weight: bold;
                    }}
                    .info {{
                        background: #f5f5f5;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 20px 0;
                        font-size: 14px;
                        color: #666;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 30px;
                        background: #667eea;
                        color: white;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: bold;
                        margin-top: 20px;
                        transition: background 0.3s;
                    }}
                    .button:hover {{
                        background: #5568d3;
                    }}
                    .spinner {{
                        border: 3px solid #f3f3f3;
                        border-top: 3px solid #667eea;
                        border-radius: 50%;
                        width: 40px;
                        height: 40px;
                        animation: spin 1s linear infinite;
                        margin: 20px auto;
                    }}
                    @keyframes spin {{
                        0% {{ transform: rotate(0deg); }}
                        100% {{ transform: rotate(360deg); }}
                    }}
                    .countdown {{
                        font-size: 18px;
                        color: #667eea;
                        margin: 15px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="success-icon">✅</div>
                    <h1>Payment {status.capitalize()}!</h1>
                    <div class="status">Transaction Verified</div>
                    
                    <div class="info">
                        <strong>Transaction ID:</strong><br>
                        {sanitized_tx_ref[:30]}...
                    </div>
                    
                    <div class="spinner"></div>
                    <div class="countdown">Redirecting in <span id="countdown">3</span> seconds...</div>
                    
                    <p style="color: #666; margin: 20px 0;">
                        You will be redirected to Telegram to complete your subscription activation.
                    </p>
                    
                    <a href="{telegram_url}" class="button">Continue to Telegram</a>
                    
                    <p style="color: #999; font-size: 12px; margin-top: 20px;">
                        If you're not redirected automatically, click the button above.
                    </p>
                </div>
                
                <script>
                    // Countdown timer
                    let seconds = 3;
                    const countdownEl = document.getElementById('countdown');
                    
                    const timer = setInterval(function() {{
                        seconds--;
                        countdownEl.textContent = seconds;
                        
                        if (seconds <= 0) {{
                            clearInterval(timer);
                            window.location.href = '{telegram_url}';
                        }}
                    }}, 1000);
                    
                    // Fallback redirect
                    setTimeout(function() {{
                        window.location.href = '{telegram_url}';
                    }}, 3000);
                </script>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
            
        except Exception as e:
            self.send_error_page(f"Error: {str(e)}")
    
    def send_error_page(self, message):
        """Send an error page"""
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payment Error</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                }}
                .container {{ 
                    background: white;
                    padding: 40px;
                    border-radius: 16px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    max-width: 500px;
                    text-align: center;
                }}
                .error-icon {{ font-size: 64px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">❌</div>
                <h1>Payment Error</h1>
                <p>{message}</p>
                <p>Please contact support if this issue persists.</p>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())