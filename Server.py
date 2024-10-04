import socket
import threading
import logging

# Configure logging to log only error messages
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

clients = []

def handle_client(client_socket, client_id):
    with client_socket:
        while True:
            try:
                message = client_socket.recv(1024)
                if not message:
                    break
                client_socket.sendall(message)
            except socket.error as e:
                logging.error(f"Socket error with client {client_id}: {e}")
                break

def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((host, port))
        server.listen(5)

        client_id = 1
        while client_id <= 2:
            try:
                client_socket, addr = server.accept()
                clients.append(client_socket)
                client_handler = threading.Thread(target=handle_client, args=(client_socket, client_id))
                client_handler.start()
                client_id += 1
            except socket.error as e:
                logging.error(f"Error accepting connection: {e}")
    except socket.error as e:
        logging.error(f"Server error: {e}")
    except KeyboardInterrupt:
        for client in clients:
            try:
                client.sendall("Server is shutting down...".encode())
                client.close()
            except socket.error as e:
                logging.error(f"Error closing client connection: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    start_server("0.0.0.0", 9999)