# Server program

from config import *

import socket
import threading
from fernets import server_key_exchange, send_raw, recv_raw


def get_local_ip():
    try:
        dummy_ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dummy_ip.connect(('8.8.8.8', 80))
        local_ip = dummy_ip.getsockname()[0]
        dummy_ip.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


HEADER = 256
HOST = '0.0.0.0'
SERVER_IP = get_local_ip()
PORT = 8080
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
clients = {}

server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_soc.bind(ADDR)


def connect_to_client(client_soc, addr):
    print(f'connected to {addr}')
    try:
        username_bytes = recv_raw(client_soc)
        username = username_bytes.decode(FORMAT)
        print(f"{addr} registered as {username}")
    except:
        print(f"Error registering user at {addr}")
        return

    fernet = server_key_exchange(client_soc)
    clients[client_soc] = (username, fernet)
    broadcast(f"--- {username} has joined the chat! ---", client_soc)

    connected = True
    while connected:
        msg_len = client_soc.recv(HEADER).decode(FORMAT).strip()
        if msg_len:
            msg_len = int(msg_len)
            encrypted = client_soc.recv(msg_len)
            print(f'Encrypted message from {username}: {encrypted}')
            msg = fernet.decrypt(encrypted).decode(FORMAT)

            if msg != DISCONNECT_MESSAGE:
                formatted_msg = f"{username}: {msg}"
                broadcast(formatted_msg, client_soc)
                print('server sent message to client')

            else:
                del clients[client_soc]
                print('server received disconnect message from client')
                client_soc.close()
                print(f'client connection with {addr} closed')
                connected = False


def broadcast(msg, sender):
    for client, (username, fernet) in list(clients.items()):
        if client != sender:
            try:
                encrypted = fernet.encrypt(msg.encode(FORMAT))
                send_raw(client, encrypted)
            except OSError:
                client.close()
                if client in clients:
                    del clients[client]


def start_server():
    try:
        server_soc.listen()
        while True:
            client_soc, addr = server_soc.accept()
            thread = threading.Thread(target=connect_to_client, args=(client_soc, addr))
            thread.start()
            print(f'{threading.active_count() - 1} threads started')
    except KeyboardInterrupt:
        print('\nShutting down server...')
        for client in clients:
            client.close()
            server_soc.close()
            print("Client closed.")


if __name__ == "__main__":
    print('starting server')
    print(f"[STARTING] Server is starting...")
    print(f"[INFO] Tell your friends to connect to this IP: {SERVER_IP}")
    start_server()