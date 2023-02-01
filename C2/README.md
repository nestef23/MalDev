## Intro
This is my implementation of very simple server <-> agent C2 framework

## Files
**c2_server.py** - Flask HTTP server written in Python 3 with SQLite database.

**agent.ps1** - PowerShell agent that communicates with server and executes commands.
TODO client?

### Server
Functionalities
- for agent
  - register itself
  - update basic host info
  - check for new command
  - report heartbeat
      - by itself
      - with completed command output
- for operator
  - list all agents
  - check specific agent status ,command history and results
  - issue command to agent
  - change agent note

### Agent
Functionalities
  - register itself with C2 server
  - regularly check-in with heartbeat
  - retrieve commands, execute them and report results
  - run until something breaks

## How to run it
### Server
0. Start with host with Python
1. Copy **c2_server.py** into some folder
2. Create virtual env inside this folder - https://flask.palletsprojects.com/en/2.2.x/installation/#virtual-environments
3. Install Flask - https://flask.palletsprojects.com/en/2.2.x/installation/#install-flask
4. start the server with `python -m flask --app c2_server run --host=0.0.0.0` from this folder
5. Server will be availbe on `http://127.0.0.1:5000/`

## Agent
0. Copy the powershell script to victim host
1. Run it with `.\agent.ps1 <Domain|IP>[:port]`
2. Wait for setup to complete. Agent should be visible on server list
3. Issue commands on the server and watch how they get executed by agent :)
