import json
import socket
import threading
import logging

# Configure logging to log error messages
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

clients = []
game_state = {
    'turn': 1,
    'players': {
        1: {'board': [], 'hits': [], 'misses': []},
        2: {'board': [], 'hits': [], 'misses': []}
    }
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
    for client in clients:
        send_message(client, {'type': 'game_state', 'state': game_state})

def handle_join(client_socket, message, client_id):
    clients.append(client_socket)
    broadcast_message(client_socket, {'type': 'system', 'message': f"Player {client_id} joined"})
    send_message(client_socket, {'type': 'welcome', 'client_id': client_id})
    broadcast_game_state()

def handle_chat(client_socket, message, client_id):
    message['client_id'] = client_id
    message['message'] = f"Player {client_id} says: {message['message']}"
    broadcast_message(client_socket, message)

def handle_move(client_socket, message, client_id):
    opponent_id = 2 if client_id == 1 else 1
    move = message['move']
    result = 'miss'

    if move in game_state['players'][opponent_id]['board']:
        result = 'hit'
        game_state['players'][client_id]['hits'].append(move)
    else:
        game_state['players'][client_id]['misses'].append(move)

    broadcast_message(client_socket, {
        'type': 'move',
        'client_id': client_id,
        'move': move,
        'result': result
    })

    if len(game_state['players'][client_id]['hits']) == len(game_state['players'][opponent_id]['board']):
        broadcast_message(client_socket, {'type': 'win', 'client_id': client_id})

    game_state['turn'] = opponent_id
    broadcast_game_state()

def handle_message(client_socket, message, client_id):
    if message['type'] == 'join':
        handle_join(client_socket, message, client_id)
    elif message['type'] == 'chat':
        handle_chat(client_socket, message, client_id)
    elif message['type'] == 'move':
        handle_move(client_socket, message, client_id)
    # Add more handlers as needed

def broadcast_message(sender_socket, message):
    for client in clients:
        if client != sender_socket:
            send_message(client, message)

def handle_client(client_socket, client_id):
    with client_socket:
        try:
            print(f"Player {client_id} connected from {client_socket.getpeername()}")
            join_message = {'type': 'join', 'client_id': client_id}
            handle_join(client_socket, join_message, client_id)
            while True:
                message = receive_message(client_socket)
                if not message:
                    break
                handle_message(client_socket, message, client_id)
            print(f"Player {client_id} disconnected")
        except socket.error as e:
            logging.error(f"Socket error with client {client_id}: {e}")
        finally:
            clients.remove(client_socket)
            broadcast_message(client_socket, {'type': 'system', 'message': f"Player {client_id} left"})

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
