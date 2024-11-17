import json
import socket
import threading
import logging

# Configure logging to log error messages
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

clients = []
game_state = {
    "boards": {
        1: {"ships": [(1, 1), (1, 2), (1, 3)], "hits": [], "misses": []},
        2: {"ships": [(3, 3), (4, 3), (5, 3)], "hits": [], "misses": []},
    },
    "turn": 1,
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
    if game_state["turn"] != client_id:
        send_message(client_socket, {"type": "system", "message": "It's not your turn!"})
        return

    # Extract move details
    position = message.get("position")
    if not position:
        send_message(client_socket, {"type": "error", "message": "Invalid move!"})
        return

    x, y = map(int, position.split())
    opponent_id = 1 if client_id == 2 else 2
    opponent_board = game_state["boards"][opponent_id]

    # Check if the move is a hit or miss
    if (x, y) in opponent_board["ships"]:
        opponent_board["hits"].append((x, y))
        result = "hit"
    else:
        opponent_board["misses"].append((x, y))
        result = "miss"

    # Notify the client of the result
    send_message(client_socket, {"type": "move_result", "result": result, "position": position})

    # Switch turn and broadcast updated game state
    game_state["turn"] = opponent_id
    broadcast_game_state()


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
