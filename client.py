# Client program

from config import *

import socket
import threading

HEADER = 256
CHUNK = 1024
PORT = 8080
UDP_PORT = 8081
FORMAT = 'utf-8'

USER_INPUT_PROMPT = f'Enter a message (or "{DISCONNECT_MESSAGE}" to quit): '


def find_server():
    print("Looking for the chat server on the network...")
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind(('', UDP_PORT))
    udp_socket.settimeout(5.0)

    while True:
        try:
            data, addr = udp_socket.recvfrom(1024)
            if data == b"CHAT_SERVER_HERE":
                server_ip = addr[0]
                print(f"Found server at {server_ip}!")
                udp_socket.close()
                return server_ip
        except socket.timeout:
            print("No server found. Please ensure the server is running and try again.")
            udp_socket.close()
            return None


def setup_connection():
    """Finds the server and establishes the TCP connection."""
    server_ip = find_server()
    if not server_ip:
        return None

    addr = (server_ip, PORT)
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        soc.connect(addr)
        return soc
    except Exception as e:
        print(f"Unable to connect to server at {addr}: {e}")
        return None


def connect(ip_address):
    addr = (ip_address, PORT)
    client_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_soc.connect(addr)
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


def authenticate(soc):
    """Handles the 3-try password loop. Returns True if successful, False if failed."""
    for attempt in range(3):
        room_pass = input(f"Enter the secret room password (Attempt {attempt + 1}/3): ")
        send(room_pass, soc)
        response = receive(soc)

        if response == "PASS_OK":
            print("Access granted!\n")
            return True
        elif response == "WRONG_PASS":
            print("Incorrect password. Try again.\n")
        elif response == "LOCKED_OUT":
            print("Incorrect password. You have been locked out.")
            return False

    return False


if __name__ == "__main__":
    client_soc = setup_connection()
    if not client_soc:
        print("Failed to connect to the server.")
        exit(1)

    if not authenticate(client_soc):
        client_soc.close()
        exit(1)

    username = input("Enter your username: ")
    send(username, client_soc)

    connected = True
    threading.Thread(target=listen, daemon=True, args=(client_soc,)).start()

    while connected:
        send_msg = input(USER_INPUT_PROMPT)
        send(send_msg, client_soc)
        if send_msg == DISCONNECT_MESSAGE:
            connected = False
            break