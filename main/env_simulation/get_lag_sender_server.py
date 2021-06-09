import client

PACKAGES_NUM = 500

client_socket = client.connect_to_server('LagListener')
client.show_lag_sender_server(client_socket, PACKAGES_NUM)
