from client import connect_to_server, receive_messages


def main():
    client_socket = connect_to_server('EnvSimulator')
    receive_messages(client_socket)


if __name__ == '__main__':
    main()