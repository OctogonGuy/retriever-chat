import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend

HEADER = 256
FORMAT = 'utf-8'

# generated once at startup
DH_PARAMETERS = dh.generate_parameters(generator=2, key_size=2048, backend=default_backend())

def send_raw(soc, data):
    header = str(len(data)).encode(FORMAT)
    header += b' ' * (HEADER - len(header))
    soc.send(header)
    soc.send(data)

def recv_raw(soc):
    msg_len = soc.recv(HEADER).decode(FORMAT).strip()
    if msg_len:
        msg_len = int(msg_len)
        return soc.recv(msg_len)
    return None

def _derive_fernet(shared_secret):
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake',
        backend=default_backend()
    ).derive(shared_secret)
    return Fernet(base64.urlsafe_b64encode(derived_key))

def client_key_exchange(soc):
    params_bytes = recv_raw(soc)
    parameters = serialization.load_pem_parameters(params_bytes, backend=default_backend())

    client_private_key = parameters.generate_private_key()
    client_public_key = client_private_key.public_key()

    server_public_bytes = recv_raw(soc)
    server_public_key = serialization.load_pem_public_key(server_public_bytes, backend=default_backend())

    client_public_bytes = client_public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    )
    send_raw(soc, client_public_bytes)

    return _derive_fernet(client_private_key.exchange(server_public_key))

def server_key_exchange(soc):
    params_bytes = DH_PARAMETERS.parameter_bytes(
        serialization.Encoding.PEM,
        serialization.ParameterFormat.PKCS3
    )
    send_raw(soc, params_bytes)

    server_private_key = DH_PARAMETERS.generate_private_key()
    server_public_key = server_private_key.public_key()

    server_public_bytes = server_public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    )
    send_raw(soc, server_public_bytes)

    client_public_bytes = recv_raw(soc)
    client_public_key = serialization.load_pem_public_key(client_public_bytes, backend=default_backend())

    return _derive_fernet(server_private_key.exchange(client_public_key))