import json
import socket
import threading
import logging
import argparse

logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

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
            print(f"Your player ID is {client_id}")  # Display the correct player ID
        elif message['type'] == 'chat':
            print(f"\n{message['message']}")  # Display chat message
        elif message['type'] == 'system':
            print(f"\n{message['message']}")  # Display system messages
        elif message['type'] == 'game_update':
            handle_game_update(message['state'])  # Render game state update


def handle_game_update(state):
    global current_turn
    print("\n--- Updated Game State ---")
    for player_id, board in state["boards"].items():
        if player_id == client_id:
            print("\nYour Board:")
            render_board(board, is_own_board=True)
        else:
            print("\nOpponent's Board:")
            render_board(board, is_own_board=False)

    current_turn = state["turn"]
    print(f"\nIt's Player {state['turn']}'s turn.")


def render_board(board, is_own_board):
    """Render the game board for display."""
    grid = [["." for _ in range(10)] for _ in range(10)]  # 10x10 grid

    # Place ships (only on the player's own board)
    if is_own_board:
        for x, y in board["ships"]:
            grid[x][y] = "S"  # S represents a ship

    # Place hits
    for x, y in board["hits"]:
        grid[x][y] = "X"  # X represents a hit

    # Place misses
    for x, y in board["misses"]:
        grid[x][y] = "O"  # O represents a miss

    # Print the grid
    print("  " + " ".join(map(str, range(10))))  # Column numbers (0-9)
    for i, row in enumerate(grid):
        print(f"{i} " + " ".join(row))  # Row numbers (0-9)


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
    global client_id, current_turn
    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

    try:
        while True:
            if current_turn == client_id:
                move = input("Enter your move (row col): ")
                # Validate move input format
                if not is_valid_move(move):
                    print("Invalid move format. Please use 'row col' (e.g., 3 4).")
                    continue
                move_data = {"type": "move", "position": move}
                send_message(client, move_data)
            else:
                print("\nIt's not your turn! Please wait...")
                message_text = input("Enter chat message or wait for your turn: ")
                chat_message = {"type": "chat", "message": message_text}
                send_message(client, chat_message)
    except socket.error as e:
        logging.error(f"Socket error: {e}")
    finally:
        client.close()
        print("Disconnected from server")


def is_valid_move(move):
    """Check if the move input is in the correct format (e.g., 'row col')."""
    try:
        x, y = map(int, move.split())
        return 0 <= x < 10 and 0 <= y < 10
    except ValueError:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Connect to the Battleship server.")
    parser.add_argument("--host", type=str, required=True, help="Server IP address")
    parser.add_argument("--port", type=int, required=True, help="Server port")
    args = parser.parse_args()

    client = connect_to_server(args.host, args.port)
    if client:
        send_receive_messages(client)
