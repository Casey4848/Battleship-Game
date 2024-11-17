import json
import socket
import threading
import logging

# Configure logging to log error messages
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

clients = []  # List to hold client connections
game_state = {
    "boards": {
        1: {"ships": [(1, 1), (1, 2), (1, 3)], "hits": [], "misses": []},
        2: {"ships": [(3, 3), (4, 3), (5, 3)], "hits": [], "misses": []},
    },
    "turn": 1,
    "players": {}  # Store player info
}
state_lock = threading.Lock()  # Lock for synchronizing game state updates

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
    chat_message = {
        "type": "chat",
        "message": f"Player {client_id} says: {message['message']}",
    }
    for client in clients:
        send_message(client, chat_message)

def handle_turn(client_socket, message, client_id):
    global game_state
    with state_lock:  # Lock the game state during updates
        if game_state["turn"] != client_id:
            send_message(client_socket, {"type": "system", "message": "It's not your turn!"})
            return

        position = message.get("position")
        if not position:
            send_message(client_socket, {"type": "error", "message": "Invalid move!"})
            return

        try:
            x, y = map(int, position.split())
        except ValueError:
            send_message(client_socket, {"type": "error", "message": "Invalid move format!"})
            return

        opponent_id = 1 if client_id == 2 else 2
        opponent_board = game_state["boards"][opponent_id]

        if (x, y) in opponent_board["ships"]:
            opponent_board["hits"].append((x, y))
            result = "hit"
        else:
            opponent_board["misses"].append((x, y))
            result = "miss"

        send_message(client_socket, {"type": "move_result", "result": result, "position": position})
        game_state["turn"] = opponent_id
        broadcast_game_state()

def handle_join(client_socket, client_id):
    game_state["players"][client_id] = {"connected": True}  # Track connected players
    join_message = {"type": "join", "client_id": client_id}

    # Send the join message to the new player with their correct ID
    send_message(client_socket, join_message)

    # If both players are connected, start the game
    if len(game_state["players"]) == 2:
        game_state["turn"] = 1  # Player 1 goes first
        # Broadcast the initial game state to both players
        broadcast_game_state()

def handle_message(client_socket, message, client_id):
    if message["type"] == "join":
        handle_join(client_socket, client_id)
    elif message["type"] == "move":
        handle_turn(client_socket, message, client_id)
    elif message["type"] == "chat":
        handle_chat(client_socket, message, client_id)

def broadcast_message(sender_socket, message):
    for client in clients:
        if client != sender_socket:
            send_message(client, message)

def handle_client(client_socket):
    # Dynamically assign client_id based on the current number of players
    client_id = len(game_state["players"]) + 1

    with client_socket:
        print(f"Player {client_id} connected")
        game_state["players"][client_id] = {"connected": True}
        join_message = {"type": "join", "client_id": client_id}
        send_message(client_socket, join_message)

        # If both players are connected, start the game
        if len(game_state["players"]) == 2:
            game_state["turn"] = 1  # Player 1 goes first
            broadcast_game_state()

        # Handle incoming messages
        while True:
            message = receive_message(client_socket)
            if not message:
                break  # Client disconnected
            handle_message(client_socket, message, client_id)

        # Handle player disconnection
        with state_lock:
            game_state["players"].pop(client_id, None)  # Remove player from game state
        broadcast_message(client_socket, {"type": "system", "message": f"Player {client_id} left"})
        clients.remove(client_socket)  # Remove from active clients list

def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((host, port))
        server.listen(5)
        actual_host = socket.gethostbyname(socket.gethostname())
        print(f"Server listening on {actual_host}:{port}")
        
        while len(game_state["players"]) < 2:  # Only allow 2 players to join
            client_socket, addr = server.accept()
            clients.append(client_socket)
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()

    except socket.error as e:
        logging.error(f"Server error: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    start_server("0.0.0.0", 5444)
