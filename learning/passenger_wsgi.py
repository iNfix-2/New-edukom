import os
import sys
import traceback

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from edukom import wsgi
    application = wsgi.application
except Exception:
    _startup_error = traceback.format_exc()

    def application(environ, start_response):
        status = '500 Internal Server Error'
        error_html = (
            "<!DOCTYPE html>"
            "<html><head><meta charset='utf-8'><title>Edukom Learning Error</title></head>"
            "<body style='font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,sans-serif;padding:30px;background:#f8f9fa;color:#333;'>"
            "<div style='max-width:850px;margin:0 auto;background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:25px;box-shadow:0 4px 6px rgba(0,0,0,0.06);'>"
            "<h2 style='color:#e53e3e;margin-top:0;'>Python Application Startup Error</h2>"
            "<p>An error occurred while initializing the Django application on this server:</p>"
            f"<pre style='background:#1e293b;color:#f8fafc;padding:16px;border-radius:6px;overflow-x:auto;font-size:13px;line-height:1.5;'>{_startup_error}</pre>"
            "<hr style='border:none;border-top:1px solid #e2e8f0;margin:20px 0;'>"
            "<p style='font-size:13px;color:#64748b;'>Edukom Learning Platform &bull; cPanel Phusion Passenger</p>"
            "</div></body></html>"
        )
        body = error_html.encode('utf-8')
        response_headers = [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', str(len(body)))
        ]
        start_response(status, response_headers)
        return [body]
