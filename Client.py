import socket
import logging

# Configure logging to log only error messages
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_server(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
        return client
    except socket.error as e:
        logging.error(f"Connection error: {e}")
        return None

def send_receive_messages(client):
    try:
        while True:
            message = input("Enter message: ")
            client.sendall(message.encode())
            response = client.recv(1024)
    except socket.error as e:
        logging.error(f"Socket error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    client = connect_to_server("127.0.0.1", 9999)
    if client:
        send_receive_messages(client)