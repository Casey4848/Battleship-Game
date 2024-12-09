# Battleship-Game
This is a simple Battleship game implemented using Python and sockets.

**How to play:**
1. **Start the server:** Run the `pyhton Server.py -p <port number>` script.
2. **Connect clients:** Run the `pyhton Client.py -i <IP address of host> -p <port number>` script on two different machines or terminals.
3. Game state is syncronized across clients and shown.
4. Boards will be shown with ships on the board as 'S'
5. Hits are 'X', misses are 'O', and empty spaces are '.'
6. Ships are automatically put on board for now.
7. Once all ships are eliminated, press enter and the game will ask if you want to reset or quit.
8. Game tells each playr whos turn it is and keeps track of it.
9.If a player leaves it will end the game after sending the other client a messsage.
10. Added in encryption for connecting clients and server.


**Technologies used:**
* Python
* Sockets
* Threading
* openssl to generate encryption keys

**Additional resources:**
* https://github.com/Casey4848/Battleship-Game/blob/2a258803ddb1d3522a44704f605c80d672e60fb0/Statement%20of%20Work%20(SOW).md

