# Client program

from config import *

import socket
import threading

HEADER = 256
CHUNK = 1024
PORT = 8080
FORMAT = 'utf-8'

SERVER = input("Enter the server IP address to connect to: ")
ADDR = (SERVER, PORT)

USER_INPUT_PROMPT = f'Enter a message (or "{DISCONNECT_MESSAGE}" to quit): '

client_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_soc.connect(ADDR)
except Exception as e:
    print(f"Unable to connect to server at {ADDR}: {e}")
    exit(1)

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
                print(f"\n{msg}")
                print(USER_INPUT_PROMPT, end='', flush=True)
        except OSError:
            break

username = input("Enter your username: ")
send(username)

connected = True
threading.Thread(target=listen, daemon=True).start()

while connected:
    send_msg = input(USER_INPUT_PROMPT)
    send(send_msg)
    if send_msg == DISCONNECT_MESSAGE:
        connected = False
        break

