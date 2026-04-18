# Server program

import socket
import threading
import time

HEADER = 256
HOST = socket.gethostbyname(socket.gethostname())
PORT = 8080
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = 'DISCONNECTED'

server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_soc.bind(ADDR)

def connect_to_client(client_soc, addr):
    print(f'connected to {addr}')

    connected = True
    while connected:
        msg_len = client_soc.recv(HEADER).decode(FORMAT)
        if msg_len:
            msg_len = int(msg_len)
            msg = client_soc.recv(msg_len).decode(FORMAT)
            print(f'message "{msg}" from {addr}')

            if msg != DISCONNECT_MESSAGE:
                client_soc.send(msg.encode(FORMAT))
                print('server sent message to client')
                print('sleeping')
                time.sleep(30)

            else:
                print('server received disconnect message from client')
                client_soc.close()
                print(f'client connection with {addr} closed')
                connected = False

def start_server():
    server_soc.listen()
    while True:
        client_soc, addr = server_soc.accept()
        thread = threading.Thread(target=connect_to_client, args=(client_soc, addr))
        thread.start()
        print(f'{threading.active_count() - 1} threads started')

print('starting server')
start_server()