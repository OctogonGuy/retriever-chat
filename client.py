# Client program

import socket
import threading

HEADER = 256
CHUNK = 1024
HOST = socket.gethostbyname(socket.gethostname())
PORT = 8080
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = 'q'

client_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_soc.connect(ADDR)

def send(message):
    msg = message.encode(FORMAT)
    msg_len = len(msg)
    msg_padding = str(msg_len).encode(FORMAT)
    msg_padding += b' ' * (HEADER - len(msg_padding))
    client_soc.send(msg_padding)
    client_soc.send(msg)


def receive():
    msg_len = client_soc.recv(HEADER).decode(FORMAT)
    if msg_len:
        msg_len = int(msg_len)
        return client_soc.recv(msg_len).decode(FORMAT)
    return None


def listen():
    while True:
        try:
            msg = receive()
            if msg:
                print(f"\nNew Message Available: {msg}")
                print('Enter a message (or "q" to quit): ', end='', flush=True)
        except:
            break


connected = True
threading.Thread(target=listen, daemon=True).start()

while connected:
    send_msg = input('Enter a message (or "q" to quit): ')
    send(send_msg)
    if send_msg == DISCONNECT_MESSAGE:
        connected = False
        break

