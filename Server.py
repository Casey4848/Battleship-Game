import socket
import threading

def handle_client(client_socket, client_id):
    with client_socket:
        print(f"Client {client_id} connected from {client_socket.getpeername()}")
        while True:
            message = client_socket.recv(1024)
            if not message:
                break
            print(f"Client {client_id} says: {message.decode()}")
            client_socket.sendall(message)
        print(f"Client {client_id} disconnected")

def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server listening on {host}:{port}")

    client_id = 1
    try:
        while client_id <= 2:
            client_socket, addr = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_id))
            client_handler.start()
            client_id += 1
    except KeyboardInterrupt:
        print("Server is shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    start_server("0.0.0.0", 9999)