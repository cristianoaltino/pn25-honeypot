#!/usr/bin/env python3

import socket
import threading
import os
import datetime

# ----------------------------
# CONFIGURAÇÃO
# ----------------------------
HOST = "0.0.0.0"
PORT = 2222  # Porta fake SSH
LOG_DIR = "logs"

# Garante que a pasta de logs exista
os.makedirs(LOG_DIR, exist_ok=True)

# ----------------------------
# Classe para lidar com o cliente
# ----------------------------
class SSHHoneypotHandler(threading.Thread):
    def __init__(self, client_socket, client_address):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_ip = client_address[0]
        self.log_filename = os.path.join(LOG_DIR, f"{self.client_ip}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    def run(self):
        with open(self.log_filename, "a") as f:
            f.write(f"=== Nova conexão de {self.client_ip} ===\n")
            try:
                # Envia banner SSH fake (mais realista)
                banner = b"SSH-2.0-OpenSSH_7.9p1 Ubuntu-10.04 LTS\n"
                self.client_socket.sendall(banner)

                # Envia prompt de login
                self.client_socket.sendall(b"login: ")
                username = self._recv_line()
                f.write(f"Usuario: {username}\n")

                # Envia prompt de senha
                self.client_socket.sendall(b"Password: ")
                password = self._recv_line()
                f.write(f"Senha: {password}\n")

                # Mensagem de erro plausível
                self.client_socket.sendall(b"Permission denied, please try again.\n")
                self.client_socket.sendall(b"login: ")

                # Segunda tentativa (opcional)
                username2 = self._recv_line()
                f.write(f"Segunda tentativa - Usuario: {username2}\n")

                self.client_socket.sendall(b"Password: ")
                password2 = self._recv_line()
                f.write(f"Segunda tentativa - Senha: {password2}\n")

                # Encerrar sessão
                self.client_socket.sendall(b"Access denied. Connection closed by remote host.\n")

            except Exception as e:
                f.write(f"[Erro]: {str(e)}\n")
            finally:
                self.client_socket.close()
                f.write(f"=== Conexão encerrada ===\n\n")

    def _recv_line(self):
        """
        Recebe uma linha até o \n ou buffer cheio.
        """
        buffer = b""
        while True:
            data = self.client_socket.recv(1)
            if not data or data == b"\n":
                break
            buffer += data
        return buffer.decode(errors="ignore").strip()

# ----------------------------
# Servidor principal
# ----------------------------
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