import tkinter as tk
from tkinter import messagebox
import json
import socket
import threading
import logging
import argparse
import ssl
import time
import queue

message_queue = queue.Queue()
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# Define global variables
client_id = None
current_turn = None
game_reset_confirmations = 0  # Track confirmations for resetting the game

# UI related variables
root = tk.Tk()
board_buttons = {}
board_canvas = None

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
            print(f"\n{message['message']}")
            if "wins" in message['message']:
                new_game_prompt()
            elif "left the game" in message['message']:
                game_over()

        elif message['type'] == 'game_update':
            message_queue.put(message['state'])  # Put the game state in the queue


def game_over():
    """End the game and ask if the player wants to restart."""
    print("The game is over! Thanks for playing.")
    client.close()
    root.quit()  # Close Tkinter window


def new_game_prompt():
    """Prompt the player for a new game or quit."""
    global game_reset_confirmations
    choice = messagebox.askyesno("Game Over", "Do you want to start a new game?")
    if choice:
        send_message(client, {"type": "reset_game", "confirmation": "yes"})
        game_reset_confirmations += 1
        if game_reset_confirmations == 2:
            send_message(client, {"type": "new_game", "new_game": True})
            game_reset_confirmations = 0  # Reset confirmation count for next game
    else:
        print("Thanks for playing! Exiting...")
        send_message(client, {"type": "reset_game", "confirmation": "no"})
        client.close()
        root.quit()


def handle_game_update(state):
    global client_id, current_turn
    print("\n--- Updated Game State ---")

    for player_id, board in state["boards"].items():
        if int(player_id) == int(client_id):
            render_board(board, is_own_board=True)  # Render your own board
        else:
            render_board(board, is_own_board=False)  # Render opponent's board

    current_turn = state["turn"]
    update_turn_label(f"Current Turn: Player {state['turn']}")



def render_board(board, is_own_board):
    """Render the game board for display with instructions and legend."""
    for i in range(10):
        for j in range(10):
            cell = board_buttons[(i, j)]

            if (i, j) in board["hits"]:
                cell.config(text="X", bg="red")  # Hit
            elif (i, j) in board["misses"]:
                cell.config(text="O", bg="blue")  # Miss
            elif (i, j) in board["ships"]:
                if is_own_board:
                    cell.config(text="S", bg="green")  # Own ships are visible
                else:
                    cell.config(text="", bg="gray")  # Hide ships on the opponent's board
            else:
                cell.config(text="", bg="lightgray")  # Empty cell




def update_turn_label(turn_message):
    turn_label.config(text=turn_message)


def on_cell_click(row, col):
    """Handle the player's move when they click on a cell."""
    if current_turn == client_id:
        move = f"{row} {col}"
        if is_valid_move(move):
            move_data = {"type": "move", "position": move}
            send_message(client, move_data)
        else:
            print("Invalid move.")
    else:
        print("It's not your turn. Please wait.")


def is_valid_move(move):
    try:
        x, y = map(int, move.split())
        return 0 <= x < 10 and 0 <= y < 10
    except ValueError:
        return False


def connect_to_server(host, port, certfile="cert.pem", keyfile="key.pem"):
    """Connect to the Battleship server with SSL encryption."""
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    try:
        context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    except Exception as e:
        logging.error(f"Failed to load certificate or key: {e}")
        return None
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
            root.update_idletasks()
            root.update()  # Update the UI
            
            if current_turn == client_id:
                # Wait for the player to make a move by clicking on the board
                pass

    except socket.error as e:
        logging.error(f"Socket error: {e}")
    finally:
        client.close()


# Set up the Tkinter window and the game board
def setup_ui():
    global board_buttons, root, turn_label
    root.title("Battleship Game")
    root.geometry("400x400")

    # Create a frame for the game board
    board_frame = tk.Frame(root)
    board_frame.grid(row=0, column=0, padx=10, pady=10)

    # Add labels for the columns (0-9)
    for i in range(10):
        tk.Label(board_frame, text=str(i), width=4).grid(row=0, column=i+1)

    # Create the 10x10 grid for the game board
    for i in range(10):
        tk.Label(board_frame, text=str(i), width=4).grid(row=i+1, column=0)
        for j in range(10):
            button = tk.Button(board_frame, text=" ", width=4, height=2, command=lambda i=i, j=j: on_cell_click(i, j))
            button.grid(row=i+1, column=j+1)
            board_buttons[(i, j)] = button

    # Label for the current player's turn
    turn_label = tk.Label(root, text="Current Turn: Player X")
    turn_label.grid(row=1, column=0, columnspan=10)

    # Call update_from_queue periodically to check the message queue
    root.after(100, update_from_queue)


def update_from_queue():
    try:
        # Check if there's a new game state in the queue
        state = message_queue.get_nowait()
        handle_game_update(state)  # Update the game board based on the new state
    except queue.Empty:
        pass

    # Call this function again after 100ms to keep checking the queue
    root.after(100, update_from_queue)


# Main entry point for the client application
if __name__ == "__main__":
    #display_game_instructions()
    setup_ui()
    root.after(100, update_from_queue)  # Start checking the queue



    parser = argparse.ArgumentParser(description="Connect to the Battleship server.")
    parser.add_argument("-i", type=str, required=True, help="Server IP address")
    parser.add_argument("-p", type=int, required=True, help="Server port")
    args = parser.parse_args()

    client = connect_to_server(args.i, args.p)
    if client:
        send_receive_messages(client)
        root.mainloop()
