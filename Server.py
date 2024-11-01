import json
import socket
import threading
import logging

# Configure logging to log error messages
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

clients = []
game_state = {
    "boards": {},
    "turn": 1,  # Initialize the turn to player 1
    "players": {}
}

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

def broadcast_game_state():
    message = {"type": "game_update", "state": game_state}
    for client in clients:
        send_message(client, message)

def handle_chat(client_socket, message, client_id):
    message['client_id'] = client_id
    message['message'] = f"Player {client_id} says: {message['message']}"
    broadcast_message(client_socket, message)

def handle_turn(client_socket, message, client_id):
    if game_state["turn"] == client_id:
        # Process the player's move (e.g., update game_state["boards"] based on the move)
        
        # Switch to the other player's turn
        game_state["turn"] = 1 if game_state["turn"] == 2 else 2
        broadcast_game_state()  # Broadcast updated game state to all clients
    else:
        send_message(client_socket, {"type": "system", "message": "It's not your turn!"})

def handle_join(client_socket, client_id):
    game_state["players"][client_id] = {"connected": True}  # Track connected players
    if len(game_state["players"]) == 2:
        game_state["turn"] = 1  # Set player 1 to go first when both players are connected
        broadcast_game_state()  # Send initial game state to all clients

def handle_message(client_socket, message, client_id):
    if message['type'] == 'join':
        handle_join(client_socket, client_id)
    elif message['type'] == 'move':
        handle_turn(client_socket, message, client_id)
    elif message['type'] == 'chat':
        handle_chat(client_socket, message, client_id)

def broadcast_message(sender_socket, message):
    for client in clients:
        if client != sender_socket:
            send_message(client, message)

def handle_client(client_socket, client_id):
    with client_socket:
        print(f"Player {client_id} connected")
        join_message = {"type": "join", "client_id": client_id}
        send_message(client_socket, join_message)
        broadcast_message(client_socket, join_message)

        while True:
            message = receive_message(client_socket)
            if not message:
                break
            handle_message(client_socket, message, client_id)
        clients.remove(client_socket)
        broadcast_message(client_socket, {"type": "system", "message": f"Player {client_id} left"})

def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((host, port))
        server.listen(5)
        actual_host = socket.gethostbyname(socket.gethostname())
        print(f"Server listening on {actual_host}:{port}")
        client_id = 1
        while client_id <= 2:
            client_socket, addr = server.accept()
            clients.append(client_socket)
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_id))
            client_handler.start()
            client_id += 1
    except socket.error as e:
        logging.error(f"Server error: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    start_server("0.0.0.0", 5444)
