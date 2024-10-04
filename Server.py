import socket
import threading

def handle_client(client_socket):
    with client_socket:
        print(f"Connection from {client_socket.getpeername()}")
        while True:
            message = client_socket.recv(1024)
            if not message:
                break
            print(f"Received: {message.decode()}")
            client_socket.sendall(message)
        print(f"Disconnection from {client_socket.getpeername()}")

def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server("0.0.0.0", 9999)