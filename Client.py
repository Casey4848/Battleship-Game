import socket
import threading
import logging

# Configure logging to log only error messages
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            print(f"\n{message.decode()}")
        except socket.error as e:
            logging.error(f"Socket error: {e}")
            break

def connect_to_server(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
        print(f"Connected to server at {host}:{port}")
        return client
    except socket.error as e:
        logging.error(f"Connection error: {e}")
        return None

def send_receive_messages(client):
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()
    try:
        while True:
            message = input("Enter message: ")
            client.sendall(message.encode())
    except socket.error as e:
        logging.error(f"Socket error: {e}")
    finally:
        client.close()
        print("Disconnected from server")

if __name__ == "__main__":
    client = connect_to_server("127.0.0.1", 5444)
    if client:
        send_receive_messages(client)