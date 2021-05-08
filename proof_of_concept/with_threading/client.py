import socket
import argparse


parser = argparse.ArgumentParser(description='This is client for multi threaded socket server')
parser.add_argument('--host', metavar='host', type=str, nargs='?', default=socket.gethostname)
parser.add_argument('--port', metavar='port', type=str, nargs='?', default=1234)
args = parser.parse_args()

print(f'Connecting to server: {args.host} on port: {args.port}')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sck:
    try:
        sck.connect((args.host, args.post))
    except Exception as e:
        raise SystemExit(f'Failed to connect to host: {args.host} on port: {args.port}, because: {e}')

    while True:
        msg = input('What to send to the server: ')
        sck.sendall(msg.encode('utf-8'))
        if msg == 'exit':
            print('Client closing...')
            break
        data = sck.recv(1024)
        print(f"Server's respond: {data.decode()}")
