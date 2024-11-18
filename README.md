# Battleship-Game
This is a simple Battleship game implemented using Python and sockets.

**How to play:**
1. **Start the server:** Run the `pyhton Server.py --port <port number>` script.
2. **Connect clients:** Run the `pyhton Client.py --host <IP address of host> --port <port number>` script on two different machines or terminals.
3. Clients can send messages to the server.
4. Game state is syncronized across clients and shown.
5. Boards will be shown with ships on the board as 'S'
6. Hits are 'X', misses are 'O', and empty spaces are '.'
7. Ships are automatically put on board for now.
8. Once all ships are eliminated, press enter and the game will ask if you want to reset or quit.
9. Game tells each playr whos turn it is and keeps track of it.


**Technologies used:**
* Python
* Sockets

**Additional resources:**
* https://github.com/Casey4848/Battleship-Game/blob/2a258803ddb1d3522a44704f605c80d672e60fb0/Statement%20of%20Work%20(SOW).md

