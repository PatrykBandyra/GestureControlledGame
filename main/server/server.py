import socket
import select


# default configuration
HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234

# socket setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)     # solves the "Address already in use" problem

server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list = [server_socket]
clients = {}


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not message_header:
            return False

        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)  # read list, write l, error l

    for notified_socket in read_sockets:

        # Server got a new connection
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)
            if user is False:
                continue

            sockets_list.append(client_socket)
            clients[client_socket] = user

            print(f"Accepted new connection from {client_address[0]}:{client_address[1]}, username:{user['data'].decode('utf-8')}")

        # Server got a new message
        else:
            message = receive_message(notified_socket)

            # Client disconnected
            if message is False:
                print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]

            # Broadcast message to all connected clients
            for client_socket in clients:
                if client_socket != notified_socket:    # Don't send back to the sender
                    client_socket.send(user['header']+user['data']+message['header']+message['data'])

    # Deal with potential socket exceptions
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
