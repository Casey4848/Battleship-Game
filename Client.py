import json
import socket
import threading
import logging

# Configure logging to log only error messages
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def send_message(client_socket, message):
    try:
        client_socket.sendall(json.dumps(message).encode())
    except socket.error as e:
        logging.error(f"Error sending message: {e}")

def receive_message(client_socket):
    try:
        return json.loads(client_socket.recv(1024).decode())
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
    except socket.error as e:
        logging.error(f"Socket error: {e}")
    return None

def receive_messages(client_socket):
    while True:
        try:
            message = receive_message(client_socket)
            if not message:
                break
            if message['type'] == 'chat' or message['type'] == 'system':
                print(f"\n{message['message']}")
            elif message['type'] == 'move':
                print(f"\nPlayer {message['client_id']} attacked {message['move']} and it was a {message['result']}.")
            elif message['type'] == 'turn':
                print(f"\n{message['message']}")
                # Prompt player to make a move
                move = input("Enter your move (e.g., A1): ")
                send_message(client_socket, {'type': 'move', 'move': move})
            elif message['type'] == 'game_state':
                print("\nGame State Updated:", message['state'])
            elif message['type'] == 'welcome':
                print(f"Welcome, Player {message['client_id']}!")
            elif message['type'] == 'win':
                print(f"Player {message['client_id']} has won the game!")
            # Handle other message types
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
            message_text = input("Enter message: ")
            message = {"type": "chat", "message": message_text}
            send_message(client, message)
    except socket.error as e:
        logging.error(f"Socket error: {e}")
    finally:
        client.close()
        print("Disconnected from server")

if __name__ == "__main__":    
    client = connect_to_server("127.0.0.1", 5444)
    if client:
        send_receive_messages(client)
