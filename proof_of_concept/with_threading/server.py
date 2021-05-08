import socket
import argparse
import threading


parser = argparse.ArgumentParser(description='This is multi threaded socket server')
parser.add_argument('--host', metavar='host', type=str, nargs='?', default=socket.gethostname)
parser.add_argument('--port', metavar='port', type=str, nargs='?', default=1234)
args = parser.parse_args()

print(f'Running the server on: {args.host} and port: {args.port}')

sck = socket.socket()
sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    sck.bind((args.host, args.port))
    sck.listen(5)
except Exception as e:
    raise SystemExit(f'Could not bind the server on host: {args.host} to port: {args.port}, because: {e}')


def on_new_client(client, connection):
    ip = connection[0]
    port = connection[1]
    print(f'The new connection was made from IP: {ip}, port: {port}')
    while True:
        msg = client.recv(1024)
        if msg.decode() == 'exit':
            break
        print(f'The client said: {msg.decode()}')
        reply = f'You told me: {msg.decode()}'
        client.sendall(reply.encode('utf-8'))
    print(f'The client from IP: {ip}, port: {port} has disconnected')
    client.close()


while True:
    try:
        client, ip = sck.accept()
        threading.Thread(target=on_new_client, args=(client, ip)).start()
    except KeyboardInterrupt:
        print(f'Shutting down the server...')
        break
    except Exception as e:
        print(e)
        break
sck.close()