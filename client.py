# Client program

import socket

HEADER = 256
CHUNK = 1024
HOST = socket.gethostbyname(socket.gethostname())
PORT = 8080
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = 'DISCONNECTED'

client_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_soc.connect(ADDR)

def send(msg):
    msg = msg.encode(FORMAT)
    msg_len = len(msg)
    msg_padding = str(msg_len).encode(FORMAT)
    msg_padding += b' ' * (HEADER - len(msg_padding))
    client_soc.send(msg_padding)
    client_soc.send(msg)

print('client sent message to server')
send('testing testing 123')
received_msg = client_soc.recv(CHUNK).decode(FORMAT)
print(received_msg)
print('client received message from server')

send(DISCONNECT_MESSAGE)