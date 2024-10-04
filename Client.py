import socket
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_server(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
        logging.info(f"Connected to server at {host}:{port}")
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
            logging.info(f"Sent: {response.decode()}")
    except socket.error as e:
        logging.error(f"Socket error: {e}")
    finally:
        client.close()
        logging.info("Disconnected from server")

if __name__ == "__main__":
    client = connect_to_server("127.0.0.1", 5444)
    if client:
        send_receive_messages(client)