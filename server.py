# Server program

import socket
import threading
import time

HEADER = 256
HOST = socket.gethostbyname(socket.gethostname())
PORT = 8080
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = 'q'
clients = {}

server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_soc.bind(ADDR)

def connect_to_client(client_soc, addr):
    print(f'connected to {addr}')
    try:
        msg_len = client_soc.recv(HEADER).decode(FORMAT)
        if msg_len:
            msg_len = int(msg_len)
            username = client_soc.recv(msg_len).decode(FORMAT)
            clients[client_soc] = username
            print(f"[{addr}] registered as {username}")
            broadcast(f"--- {username} has joined the chat! ---", client_soc)
    except:
        print(f"Error registering user at {addr}")
        return

    connected = True
    while connected:
        msg_len = client_soc.recv(HEADER).decode(FORMAT)
        if msg_len:
            msg_len = int(msg_len)
            msg = client_soc.recv(msg_len).decode(FORMAT)
            print(f'message "{msg}" from {username}')

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


def send(client, message):
    msg = message.encode(FORMAT)
    msg_len = len(msg)
    header = str(msg_len).encode(FORMAT)
    header += b' ' * (HEADER - len(header))
    client.send(header)
    client.send(msg)


def broadcast(msg, sender):
    for client in list(clients.keys()):
        if client != sender:
            try:
                send(client, msg)
            except:
                client.close()
                if client in clients:
                    del clients[client]

def start_server():
    server_soc.listen()
    while True:
        client_soc, addr = server_soc.accept()
        thread = threading.Thread(target=connect_to_client, args=(client_soc, addr))
        thread.start()
        print(f'{threading.active_count() - 1} threads started')

print('starting server')
start_server()