#!/usr/bin/env python3

import socket
import threading
import os
import datetime
import time
from dotenv import load_dotenv

# Carregar .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT_SSH", 2222))
LOG_DIR = os.getenv("LOG_DIR", "logs")

os.makedirs(LOG_DIR, exist_ok=True)

class SSHHoneypotHandler(threading.Thread):
    def __init__(self, client_socket, client_address):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_ip = client_address[0]
        self.log_filename = os.path.join(
            LOG_DIR, f"{self.client_ip}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

    def run(self):
        with open(self.log_filename, "a") as f:
            f.write(f"=== Nova conexão de {self.client_ip} ===\n")
            try:
                # Envia banner SSH fake
                banner = b"SSH-2.0-OpenSSH_7.9p1 Ubuntu-10.04 LTS\r\n"
                self.client_socket.sendall(banner)

                # Mantém a conexão aberta por 60s para não causar RESET imediato
                time.sleep(60)

            except Exception as e:
                f.write(f"[Erro]: {str(e)}\n")
            finally:
                self.client_socket.close()
                f.write(f"=== Conexão encerrada ===\n\n")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[+] Honeypot SSH Fake rodando em {HOST}:{PORT}")

    try:
        while True:
            client_socket, client_address = server.accept()
            handler = SSHHoneypotHandler(client_socket, client_address)
            handler.start()
    except KeyboardInterrupt:
        print("\n[!] Servidor honeypot encerrado pelo usuário.")
    finally:
        server.close()

if __name__ == "__main__":
    main()

