import socket
import argparse
from _thread import *
import threading


# Default configuration
HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234


print_lock = threading.Lock()


# thread function
def threaded(c):
    while True:

        # data received from client
        data = c.recv(1024)
        if not data:
            print('Bye')

            # lock released on exit
            print_lock.release()
            break

        # reverse the given string from client
        data = data[::-1]

        # send back reversed string to client
        c.send(data)

    # connection closed
    c.close()


def main():
    # Socket setup
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Solves the "Address already in use" problem

    try:
        server_socket.bind((IP, PORT))
        server_socket.listen()
    except Exception as e:
        raise SystemExit(f'Could not bind the server on: {IP}, port: {PORT}, because: {e}')

    print(f'Running the server on: {IP} and port: {PORT}')

    sockets_list = [server_socket]
    clients = {}

    server_socket.listen(5)
    print(f'Server is listening for connection...')

    # a forever loop until client wants to exit
    while True:
        # establish connection with client/
        client_socket, client_address = server_socket.accept()

        # lock acquired by client
        print_lock.acquire()
        print(f'Connected to: {client_address[0]}, port: {client_address[1]}')

        # Start a new thread and return its identifier
        start_new_thread(threaded, (c,))
    s.close()


if __name__ == '__main__':
    main()
