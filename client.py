# Client program

from config import *

import socket
import threading

HEADER = 256
CHUNK = 1024
PORT = 8080
FORMAT = 'utf-8'
USER_INPUT_PROMPT = f'Enter a message (or "{DISCONNECT_MESSAGE}" to quit): '

def connect(ip_address):
    addr = (ip_address, PORT)
    client_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_soc.connect(addr)
    except Exception as e:
        print(f"Unable to connect to server at {ADDR}: {e}")
        exit(1)
    return client_soc

def send(soc, message):
    msg = message.encode(FORMAT)
    msg_len = len(msg)
    msg_padding = str(msg_len).encode(FORMAT)
    msg_padding += b' ' * (HEADER - len(msg_padding))
    soc.send(msg_padding)
    soc.send(msg)


def receive(soc):
    msg_len = soc.recv(HEADER).decode(FORMAT)
    if msg_len:
        msg_len = int(msg_len)
        return soc.recv(msg_len).decode(FORMAT)
    return None


def listen(soc):
    while True:
        try:
            msg = receive(soc)
            if msg:
                print(f"\n{msg}")
                print(USER_INPUT_PROMPT, end='', flush=True)
        except OSError:
            break


if __name__ == "__main__":
    # Get IP address
    server = input("Enter the server IP address to connect to: ")

    # Create client socket
    client_soc = connect(server)

    # Get and send username
    username = input("Enter your username: ")
    send(client_soc, username)

    # Keep listening for requests
    connected = True
    threading.Thread(target=listen, daemon=True, args=(client_soc,)).start()
    while connected:
        send_msg = input(USER_INPUT_PROMPT)
        send(client_soc, send_msg)
        if send_msg == DISCONNECT_MESSAGE:
            connected = False
            break