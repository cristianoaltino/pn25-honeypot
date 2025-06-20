#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import datetime
import json
from urllib.parse import urlparse, parse_qs

# config
HOST = "0.0.0.0"
PORT = 8080
LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)

# Class Handler
class HTTPHoneypotHandler(BaseHTTPRequestHandler):
    def _log_request(self, body=None):
        log_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "client_ip": self.client_address[0],
            "method": self.command,
            "path": self.path,
            "headers": {k: v.strip() for k, v in self.headers.items()},
            "body": body.decode(errors='ignore') if body else ""
        }

        log_filename = os.path.join(LOG_DIR, f"{self.client_address[0]}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(log_filename, "w") as f:
            json.dump(log_data, f, indent=4)

    def _send_response(self, code, body):
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/admin":
            body = "<h1>403 Forbidden</h1><p>You are not authorized to access /admin</p>"
        elif parsed.path == "/":
            body = "<h1>Fake HTTP Honeypot</h1><p>All your requests are being logged.</p>"
        else:
            body = f"<h1>404 Not Found</h1><p>No resource at {parsed.path}</p>"

        self._log_request()
        self._send_response(200, body)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        parsed = urlparse(self.path)

        if parsed.path == "/login":
            body = "<h1>Login Failed</h1><p>Invalid credentials</p>"
        else:
            body = f"<h1>POST received at {parsed.path}</h1>"

        self._log_request(body=post_data)
        self._send_response(200, body)

    def log_message(self, format, *args):
        return

# server
def run_server():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, HTTPHoneypotHandler)
    print(f"[+] Honeypot HTTP rodando em http://{HOST}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Honeypot HTTP encerrado pelo usuário.")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run_server()