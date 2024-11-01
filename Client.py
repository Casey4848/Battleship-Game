import json
import socket
import threading
import logging
import argparse

# Configure logging to log only error messages
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

client_id = None
current_turn = None

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
    global client_id, current_turn
    while True:
        message = receive_message(client_socket)
        if not message:
            break
        if message['type'] == 'join':
            client_id = message['client_id']  # Set client_id from server message
            print(f"Your player ID is {client_id}")
        elif message['type'] == 'chat':
            print(f"\n{message['message']}")  # Display chat message
        elif message['type'] == 'system':
            print(f"\n{message['message']}")  # Display system messages
        elif message['type'] == 'game_update':
            handle_game_update(message['state'])  # Render game state update


def handle_game_update(state):
    global current_turn
    print("Updated game state received.")
    # Render the game state (e.g., print the boards for each player)
    # You could use `state["boards"]` to display the board positions
    print(f"Turn: Player {state['turn']}")
    current_turn = state['turn']

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
    global client_id
    # Start thread for receiving messages
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()
    
    # Input and send messages
    try:
        while True:
            if current_turn == client_id:
                move = input("Enter your move (row col): ")
                move_data = {"type": "move", "position": move}
                send_message(client, move_data)
            else:
                # Allow player to send chat messages while waiting for their turn
                message_text = input("Enter chat message or wait for your turn: ")
                chat_message = {"type": "chat", "message": message_text}
                send_message(client, chat_message)
    except socket.error as e:
        logging.error(f"Socket error: {e}")
    finally:
        client.close()
        print("Disconnected from server")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Connect to the Battleship server.")
    parser.add_argument('--host', type=str, required=True, help='Server IP address')
    parser.add_argument('--port', type=int, required=True, help='Server port')
    args = parser.parse_args()

    client = connect_to_server(args.host, args.port)
    if client:
        send_receive_messages(client)
