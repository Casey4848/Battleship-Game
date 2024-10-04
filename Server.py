import socket
import threading
import logging

# Configure logging to log error messages
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def handle_client(client_socket, client_id):
    with client_socket:
        try:
            print(f"Client {client_id} connected from {client_socket.getpeername()}")
            while True:
                message = client_socket.recv(1024)
                if not message:
                    break
                print(f"Client {client_id} says: {message.decode()}")
                client_socket.sendall(message)
            print(f"Client {client_id} disconnected")
        except socket.error as e:
            logging.error(f"Socket error with client {client_id}: {e}")

def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((host, port))
        server.listen(5)
        print(f"Server listening on {host}:{port}")

        client_id = 1
        while client_id <= 2:
            try:
                client_socket, addr = server.accept()
                client_handler = threading.Thread(target=handle_client, args=(client_socket, client_id))
                client_handler.start()
                client_id += 1
            except socket.error as e:
                logging.error(f"Error accepting connection: {e}")
    except socket.error as e:
        logging.error(f"Server error: {e}")
    except KeyboardInterrupt:
        print("Server is shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    start_server("0.0.0.0", 5444)