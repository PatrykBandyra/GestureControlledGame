import socket
import sys
import errno


# default configuration
HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234


def connect_to_server(client_name: str):
    client_name = client_name.encode('utf-8')
    client_name_header = f'{len(client_name):<{HEADER_LENGTH}}'.encode('utf-8')

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)

    client_socket.send(client_name_header + client_name)    # send id to the server

    return client_socket


def send_string_message(client_socket, message: str):
    message = message.encode('utf-8')
    message_header = f'{len(message):<{HEADER_LENGTH}}'.encode('utf-8')
    client_socket.send(message_header + message)


def receive_messages(client_socket):
    while True:
        try:
            while True:
                # receive things
                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()

                username_length = int(username_header.decode('utf-8').strip())
                username = client_socket.recv(username_length).decode('utf-8')

                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')

                print(f"{username} > {message}")

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error', str(e))
                sys.exit()
            continue

        except Exception as e:
            print('General error', str(e))
            sys.exit()


def receive_binary_data():
    pass
