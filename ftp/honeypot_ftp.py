#!/usr/bin/env python3

import socketserver
import threading
import datetime
import os
import json
from dotenv import load_dotenv

# ----------------------------
# Carregar variáveis do .env
# ----------------------------
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# ----------------------------
# CONFIGURAÇÃO
# ----------------------------
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT_FTP", 2121))  # Porta específica para FTP
LOG_DIR = os.path.join(os.getenv("LOG_DIR", "logs"), "ftp")

# Garante que a pasta de logs FTP exista
os.makedirs(LOG_DIR, exist_ok=True)

# ----------------------------
# Handler de comandos
# ----------------------------
class FTPHoneypotHandler(socketserver.BaseRequestHandler):
    def handle(self):
        ip = self.client_address[0]
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(LOG_DIR, f"{ip}_{timestamp}.json")
        log_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "client_ip": ip,
            "commands": []
        }

        try:
            self.request.sendall(b"220 Fake FTP Honeypot Ready.\r\n")

            authenticated = False

            while True:
                data = self.request.recv(1024)
                if not data:
                    break

                command = data.decode(errors='ignore').strip()
                log_data["commands"].append(command)

                cmd_upper = command.upper()

                if cmd_upper.startswith("USER"):
                    self.request.sendall(b"331 Username OK, need password.\r\n")
                elif cmd_upper.startswith("PASS"):
                    authenticated = True
                    self.request.sendall(b"230 Login successful.\r\n")
                elif cmd_upper.startswith("QUIT"):
                    self.request.sendall(b"221 Goodbye.\r\n")
                    break
                elif not authenticated:
                    self.request.sendall(b"530 Please login with USER and PASS.\r\n")
                elif cmd_upper.startswith("LIST"):
                    self.request.sendall(b"150 Here comes the directory listing.\r\n")
                    self.request.sendall(b"-rw-r--r-- 1 user group 123 Jan 01 00:00 fakefile.txt\r\n")
                    self.request.sendall(b"226 Directory send OK.\r\n")
                elif cmd_upper.startswith("RETR"):
                    self.request.sendall(b"550 Requested action not taken. File unavailable.\r\n")
                elif cmd_upper.startswith("STOR"):
                    self.request.sendall(b"550 Permission denied.\r\n")
                else:
                    self.request.sendall(b"502 Command not implemented.\r\n")

        except Exception as e:
            log_data["error"] = str(e)

        finally:
            with open(log_file, "w") as f:
                json.dump(log_data, f, indent=4)
            self.request.close()

# ----------------------------
# Servidor Thread-safe
# ----------------------------
class ThreadedFTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def main():
    server = ThreadedFTPServer((HOST, PORT), FTPHoneypotHandler)
    server.allow_reuse_address = True
    print(f"[+] Honeypot FTP Fake rodando em {HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Servidor honeypot FTP encerrado pelo usuário.")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()

