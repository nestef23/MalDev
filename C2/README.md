## Intro
This is my implementation of agent - server C2 framework

## Files
**c2_server.py** - Flask HTTP server written in Python 3 with SQLite database.
TODO agent
TODO client?

### Server
Functionalities
- for agent
  - register itself
  - report heartbeat with optional completed command results
  - check for new command (TODO)
- for operator
  - list all agents
  - check specific agent status ,command history and results
  - issue command to agent

### Agent
TODO

## How to run it
### Server
0. Start with host with Python
1. Copy **c2_server.py** into some folder
2. Create virtual env inside this folder - https://flask.palletsprojects.com/en/2.2.x/installation/#virtual-environments
3. Install Flask - https://flask.palletsprojects.com/en/2.2.x/installation/#install-flask
4. start the server with `python -m flask --app c2_server run` from this folder
5. Server will be availbe on `http://127.0.0.1:5000/`
