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
  - check/report heartbeat
  - check for new command (TODO)
  - report command completed (TODO)
- for operator
  - list all agents
  - check command history, their status and results
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
6. Example functionalities:
```
http://127.0.0.1:5000/about
http://127.0.0.1:5000/register?id=1235
http://127.0.0.1:5000/heartbeat/<base64>
http://127.0.0.1:5000/ls/agents
http://127.0.0.1:5000/ls/agent?id=1235
http://127.0.0.1:5000/command?id=1235&command=whoami
```
