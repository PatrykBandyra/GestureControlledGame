from client import connect_to_server, receive_messages, receive_binary_messages
import threading
import time


def main():
    client_socket = connect_to_server('EnvSimulator')
    # t1 = threading.Thread(target=receive_messages, args=(client_socket, ))
    t1 = threading.Thread(target=receive_binary_messages, args=(client_socket,))
    t1.start()
    i = 0
    while True:
        print(i)
        time.sleep(1)
        i += 1


if __name__ == '__main__':
    main()