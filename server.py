# Server program

from config import *

import socket
import threading
import time

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
UDP_PORT = 8081
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
clients = {}

ROOM_PASSWORD = input("Create a secret password for this chat room: ")

server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_soc.bind(ADDR)

# --- NEW: Auto-Discovery Broadcaster ---
def broadcast_presence():
    """Constantly shouts to the network so clients can find the server."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    broadcast_msg = b"CHAT_SERVER_HERE"
    start_time = time.time()
    
    while time.time() - start_time < 30:  # Broadcast for 30 seconds
        try:
            udp_socket.sendto(broadcast_msg, ('<broadcast>', UDP_PORT))
            time.sleep(1)
        except Exception as e:
            print(f"Broadcast error: {e}")
            break
    print("\n[INFO] Broadcast ended. The room is now hidden from the network.")
    udp_socket.close()

def connect_to_client(client_soc, addr):
    print(f'connected to {addr}')
    try:
        # --- NEW: 3 Tries Password Logic ---
        authenticated = False
        for attempt in range(3):
            msg_len = client_soc.recv(HEADER).decode(FORMAT)
            if msg_len:
                client_pass = client_soc.recv(int(msg_len)).decode(FORMAT)
                
                if client_pass == ROOM_PASSWORD:
                    send(client_soc, "PASS_OK")
                    authenticated = True
                    break # Break out of the loop, password is correct
                else:
                    if attempt < 2: # If it's try 1 or 2
                        send(client_soc, "WRONG_PASS")
                    else:           # If it's the 3rd try
                        send(client_soc, "LOCKED_OUT")
        
        # If they failed 3 times, close the connection and stop the thread
        if not authenticated:
            print(f"[{addr}] Kicked: Failed password 3 times.")
            client_soc.close()
            return

        # --- EXISTING: Register the username ---
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


def send(client_soc, message):
    msg = message.encode(FORMAT)
    msg_len = len(msg)
    header = str(msg_len).encode(FORMAT)
    header += b' ' * (HEADER - len(header))
    client_soc.send(header)
    client_soc.send(msg)


def broadcast(msg, sender):
    for client in list(clients.keys()):
        if client != sender:
            try:
                send(client, msg)
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
    print(f"[INFO] Server is broadcasting its presence on the network.")
    
    # --- NEW: Start the broadcaster thread ---
    announce_thread = threading.Thread(target=broadcast_presence, daemon=True)
    announce_thread.start()
    start_server()