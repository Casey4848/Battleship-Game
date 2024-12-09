import json
import socket
import threading
import logging
import argparse
import time
import ssl

logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

client_id = None
current_turn = None
game_reset_confirmations = 0  # New variable to track client confirmations for resetting the game


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
    global client_id, current_turn, game_reset_confirmations
    while True:
        message = receive_message(client_socket)
        if not message:
            break  # Client disconnected
        
        # Handle different types of messages from the server
        if message['type'] == 'join':
            client_id = message['client_id']
            print(f"Your player ID is {client_id}")
        
        elif message['type'] == 'system':
            # Display system messages (like game over or player leaving)
            print(f"\n{message['message']}")
            
            if "wins" in message['message']:
                # When a player wins or the game ends, prompt for a new game or quit
                new_game_prompt()
            elif "left the game" in message['message']:
                # If a player disconnects, game over
                game_over()

        elif message['type'] == 'game_update':
            # Handle the updated game state from the server
            handle_game_update(message['state'])
        
        elif message['type'] == 'reset_game':
            # Handle reset confirmation requests
            handle_reset_game_request()

def game_over():
    """End the game and ask if the player wants to restart."""
    print("The game is over! Thanks for playing.")
    print("Goodbye!")
    client.close()  # Close the connection
    exit()  # Exit the program


def new_game_prompt():
    """Prompt the player for a new game or quit."""
    global game_reset_confirmations
    while True:
        choice = input("Game Over! Do you want to start a new game? (yes/no): ").strip().lower()
        if choice in ["yes", "y"]:
            send_message(client, {"type": "reset_game", "confirmation": "yes"})
            game_reset_confirmations += 1  # Increment confirmation count
            if game_reset_confirmations == 2:
                print("Both players agreed. Starting a new game...")
                send_message(client, {"type": "new_game", "new_game": True})
                game_reset_confirmations = 0  # Reset confirmation count for next game
            break
        elif choice in ["no", "n"]:
            print("Thanks for playing! Exiting...")
            send_message(client, {"type": "reset_game", "confirmation": "no"})
            client.close()
            exit()
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")


def handle_reset_game_request():
    """Handle reset game confirmation from both clients."""
    global game_reset_confirmations
    print("Waiting for the other player to confirm the reset...")
    # This method ensures that both clients must say "yes" before proceeding
    while game_reset_confirmations < 2:
        pass  # Wait until both players confirm


def handle_game_update(state):
    global client_id, current_turn
    print("\n--- Updated Game State ---")

    for player_id, board in state["boards"].items():
        if int(player_id) == int(client_id):
            print("Rendering Your Board:")
            render_board(board, is_own_board=True)
        else:
            print("Rendering Opponent's Board:")
            render_board(board, is_own_board=False)

    current_turn = state["turn"]
    print(f"Current Turn: Player {state['turn']}")
    show_turn_message(current_turn)


def render_board(board, is_own_board):
    """Render the game board for display with instructions and legend."""
    print("\n--- Instructions ---")
    print("S = Ship | X = Hit | O = Miss")
    print("Enter your move as 'row col' (e.g., '3 4').")
    
    print("\n--- Your Board ---" if is_own_board else "\n--- Opponent's Board ---")
    print("  " + " ".join(map(str, range(10))))  # Column numbers (0-9)
    
    grid = [["." for _ in range(10)] for _ in range(10)]  # 10x10 grid

    if is_own_board:
        for x, y in board["ships"]:
            grid[x][y] = "S"  # S represents a ship

    for x, y in board["hits"]:
        grid[x][y] = "X"  # X represents a hit

    for x, y in board["misses"]:
        grid[x][y] = "O"  # O represents a miss

    for i, row in enumerate(grid):
        print(f"{i} " + " ".join(row))  # Row numbers (0-9)


def show_turn_message(turn):
    print(f"\n--- It's Player {turn}'s Turn ---")


def display_game_instructions():
    print("Welcome to Battleship!")
    print("Instructions:")
    print("1. The game is played on a 10x10 grid.")
    print("2. Players take turns to guess the opponent's ship locations.")
    print("3. The goal is to sink all of the opponent's ships.")
    print("4. 'S' marks your ships, 'X' marks hits, and 'O' marks misses.")
    print("5. Enter your move as 'row col' (e.g., '3 4').")
    print("\nLet's start the game!")


def connect_to_server(host, port, certfile="cert.pem", keyfile="key.pem"):
    # Create an SSL context
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    # Load the certificate and key files
    try:
        context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    except Exception as e:
        logging.error(f"Failed to load certificate or key: {e}")
        return None
    
    # Create a socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Wrap the socket with SSL
    client = context.wrap_socket(client, server_hostname=host)
    
    try:
        client.connect((host, port))
        print(f"Connected to server at {host}:{port} with SSL encryption")
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
                # It's the player's turn, so prompt them for a move
                move = input("Enter your move (row col): ")
                if not is_valid_move(move):
                    print("Invalid move format. Please use 'row col' (e.g., 3 4).")
                    continue
                move_data = {"type": "move", "position": move}
                send_message(client, move_data)
            else:
                # It's not the player's turn, so just wait
                print("\nIt's not your turn! Please wait...")
                while current_turn != client_id:  # Wait until it is the player's turn
                    time.sleep(1)  # Sleep briefly to prevent busy-waiting (adjust the time as needed)

    except socket.error as e:
        logging.error(f"Socket error: {e}")
    finally:
        print("Disconnected from server")
        client.close()


def is_valid_move(move):
    try:
        x, y = map(int, move.split())
        return 0 <= x < 10 and 0 <= y < 10
    except ValueError:
        return False


if __name__ == "__main__":
    display_game_instructions()

    parser = argparse.ArgumentParser(description="Connect to the Battleship server.")
    parser.add_argument("-i", type=str, required=True, help="Server IP address")
    parser.add_argument("-p", type=int, required=True, help="Server port")
    args = parser.parse_args()

    client = connect_to_server(args.i, args.p)
    if client:
        send_receive_messages(client)
