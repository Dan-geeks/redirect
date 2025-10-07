# /api/redirect.py - SIMPLE DEBUG VERSION

from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
import re

BOT_USERNAME = "PremiumtelenovelasBot"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse URL
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        # Convert to simple dict
        simple_params = {}
        for key, value in params.items():
            simple_params[key] = value[0] if len(value) == 1 else value
        
        # Get tx_ref from Flutterwave
        tx_ref = simple_params.get('tx_ref')
        
        # Sanitize tx_ref: remove or replace special characters that break Telegram deep links
        if tx_ref:
            # Remove parentheses, spaces, and other special characters
            tx_ref = re.sub(r'[^\w\-]', '_', tx_ref)
            payload = f"verify_{tx_ref}"
            # URL encode the payload for safety
            encoded_payload = quote(payload, safe='')
        else:
            payload = None
            encoded_payload = None
        
        # Create HTML response showing everything
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Debug - Payment Redirect</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    padding: 20px; 
                    background: #f5f5f5;
                }}
                .container {{ 
                    background: white; 
                    padding: 20px; 
                    border-radius: 8px; 
                    max-width: 800px; 
                    margin: 0 auto;
                }}
                .param {{ 
                    background: #e3f2fd; 
                    padding: 10px; 
                    margin: 5px 0; 
                    border-left: 3px solid #2196f3;
                }}
                .success {{ color: green; }}
                .error {{ color: red; }}
                pre {{ 
                    background: #f4f4f4; 
                    padding: 10px; 
                    overflow-x: auto;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔍 Payment Redirect Debug</h1>
                
                <h2>Full URL Received:</h2>
                <pre>{self.path}</pre>
                
                <h2>Parameters Received:</h2>
                <div>
        """
        
        if simple_params:
            for key, value in simple_params.items():
                html += f'<div class="param"><strong>{key}:</strong> {value}</div>'
        else:
            html += '<p class="error">❌ No parameters received!</p>'
        
        html += """
                </div>
                
                <h2>Looking for these parameters:</h2>
                <ul>
                    <li><strong>tx_ref</strong> - Transaction reference from Flutterwave</li>
                    <li><strong>status</strong> - Payment status</li>
                    <li><strong>transaction_id</strong> - Flutterwave transaction ID</li>
                </ul>
        """
        
        # Try to redirect if we have tx_ref
        tx_ref = simple_params.get('tx_ref')
        if tx_ref:
            payload = f"verify_{tx_ref}"
            telegram_url = f"https://t.me/{BOT_USERNAME}?start={payload}"
            html += f"""
                <hr>
                <h2 class="success">✅ Found tx_ref! Creating redirect...</h2>
                <p><strong>Transaction Reference:</strong> {tx_ref}</p>
                <p><strong>Payload Created:</strong> {payload}</p>
                <p><strong>Telegram URL:</strong> <a href="{telegram_url}">{telegram_url}</a></p>
                
                <script>
                    // Auto-redirect after 3 seconds
                    setTimeout(function() {{
                        window.location.href = '{telegram_url}';
                    }}, 3000);
                </script>
                
                <p>Redirecting in 3 seconds... <a href="{telegram_url}">Click here to redirect now</a></p>
            """
        else:
            html += """
                <hr>
                <h2 class="error">❌ No tx_ref found!</h2>
                <p>This means Flutterwave is not sending the transaction reference.</p>
                <p><strong>Possible issues:</strong></p>
                <ul>
                    <li>The redirect_url in Flutterwave payment might be incorrect</li>
                    <li>This is a direct visit to the page (not from Flutterwave)</li>
                    <li>Flutterwave changed their redirect format</li>
                </ul>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())