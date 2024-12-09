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
9. Added error handling for when a player leaves/disconects it will end the game after sending the other client a messsage.
10. There is error handling on the server side as well for disconects and connection issues.
11. Added in encryption for connecting clients and server.
12. I have a UI inplemented with tkinter, but it was not complete.


**Technologies used:**
* Python
* Sockets
* Threading
* openssl to generate encryption keys

**Roadmap:**
* Short-term improvements:
  Add a timer to limit the time each player has to take a turn.
  Include a feature to chat with other players in real-time.
* Long-term improvements:
  Implement AI for single-player mode.
  Enhance the visual UI with better graphics and animations.
  Allow players to customize their ships and boards.

**Retrospective**
* What Went Right:
  The communication between the server and client works smoothly, with the game state being updated in real-time.
  The game’s rules are enforced correctly, and both players can take turns and make moves without issues.
  SSL encryption was successfully integrated for secure communication between the server and client.
* What Could Be Improved:
  Scalability: The game works well for two players, but there is no clear path for handling larger game rooms or matchmaking.
  User Interface: The UI is in another branch and is functional but not finished.

**Additional resources:**
* https://github.com/Casey4848/Battleship-Game/blob/2a258803ddb1d3522a44704f605c80d672e60fb0/Statement%20of%20Work%20(SOW).md

