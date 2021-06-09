import socket
import pickle


# Default configuration
HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234


def connect_to_server(client_name: str):
    """
    Connects to the local server.

    :param client_name: string
    :return: client's socket
    """
    client_name = client_name.encode('utf-8')
    client_name_header = f'{len(client_name):<{HEADER_LENGTH}}'.encode('utf-8')

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)

    client_socket.send(client_name_header + client_name)    # Send id to the server

    return client_socket


def send_object_message(client_socket, message: object):
    message = pickle.dumps(message)
    message_header = bytes(f'{len(message):<{HEADER_LENGTH}}', 'utf-8')
    client_socket.send(message_header + message)
