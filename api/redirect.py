# /api/redirect.py - Direct redirect without HTML

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

            if not tx_ref:
                # Send error as plain 302 redirect
                self.send_response(302)
                self.send_header('Location', f"https://t.me/{BOT_USERNAME}")
                self.end_headers()
                return

            # Sanitize tx_ref for Telegram deep link
            sanitized_tx_ref = sanitize_for_telegram(tx_ref)
            payload = f"verify_{sanitized_tx_ref}"

            # Create Telegram deep link
            telegram_url = f"https://t.me/{BOT_USERNAME}?start={payload}"

            # Direct 302 redirect
            self.send_response(302)
            self.send_header('Location', telegram_url)
            self.end_headers()

        except Exception as e:
            # On error, redirect to bot without payload
            self.send_response(302)
            self.send_header('Location', f"https://t.me/{BOT_USERNAME}")
            self.end_headers()