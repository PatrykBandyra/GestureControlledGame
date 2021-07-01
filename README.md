# Gesture controlled game

Description:

Gesture controlled game. Project is separted into 3 modules that can be run on different machines within the same network:
- env_simulation - just a simple 2D shooter; the player can use keyboard or hand gestures (this functionality is implemented in single_board module) to control the game
- single_board - the module that can be run on a single board computer with attached screen; hand detection, gesture recognition, instruction interpretation, displaying camera image with additional informations about detected objects
- server - server to control communication between above modules

Used languages\libraries:
- Python 3
- OpenCV
- MediaPipe
- Socket
- Pickle
- PyGame
- PyTMX

### Hand landmarks
![Alt text](hand_landmarks.png)
