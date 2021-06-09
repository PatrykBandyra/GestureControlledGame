import socket
import sys
import errno
import pickle
import time
import matplotlib.pyplot as plt


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


def send_string_message(client_socket, message: str):
    message = message.encode('utf-8')
    message_header = f'{len(message):<{HEADER_LENGTH}}'.encode('utf-8')
    client_socket.send(message_header + message)


def send_object_message(client_socket, message: object):
    message = pickle.dumps(message)
    message_header = bytes(f'{len(message):<{HEADER_LENGTH}}', 'utf-8')
    client_socket.send(message_header + message)


def show_lag_sender_server(client_socket, packages_num):
    x_vals = []
    y_vals = []
    index = 0

    while True:
        try:
            while index != packages_num:
                # Receive things
                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()

                username_length = int(username_header.decode('utf-8').strip())
                username = client_socket.recv(username_length).decode('utf-8')

                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length)
                message = pickle.loads(message)

                lag_ms = (time.time_ns() - message["time"]) / 1_000_000
                y_vals.append(lag_ms)
                index += 1
                x_vals.append(index)
                print(f'Lag: {lag_ms} ms')


        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error', str(e))
                sys.exit()
            continue

        except Exception as e:
            print('General error', str(e))
            sys.exit()

        break
    plt.hist(y_vals)
    plt.title('Histogram of delays between data sender and receiver')
    plt.xlabel('Delay in ms')
    plt.ylabel('Number of packages')
    plt.show()


def receive_commands_from_server(client_socket, fifo_buffer, quit_event):

    # It will quit if server is down or PyGame window is closed and it receives one last message to end the loop

    while True:
        try:
            while True:
                # Receive things
                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()

                username_length = int(username_header.decode('utf-8').strip())
                username = client_socket.recv(username_length).decode('utf-8')

                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length)
                message = pickle.loads(message)

                fifo_buffer.put(message)

                if quit_event.isSet():
                    sys.exit()

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error', str(e))
                sys.exit()
            continue

        except Exception as e:
            print('General error', str(e))
            sys.exit()