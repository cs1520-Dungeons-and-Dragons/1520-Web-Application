from flask import Flask, url_for, redirect, render_template, request
from flask import session, jsonify
from flask_sockets import Sockets
import random
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'memeslol'

sockets = Sockets(app)             # create socket listener
#u_to_r = {}                  # map users to rooms
r_to_client = {}                # map room to list of Clients connected`(uses Object from gevent API)
last_client = []            # use to store previous clients list, compare to track clients

# helper to roll dice, takes dice type and adv/disadv attributes
def roll_dice(size, adv, dis, uname):
  r1 = random.randint(1, size)
  if (adv != dis):
    # if distinct values, means rolled 2 dice
    r2 = random.randint(1, size)
    msg = ('(d' + str(size) + '): ' + uname + ' rolled ' + str(r1) + ' and ' + str(r2) + 
    ' with ' + ('advantage' if adv else 'disadvantage') + ': use roll ' 
    + (str(max(r1, r2)) if adv else str(min(r1, r2))))
  else:
    # just 1 roll
    msg = '(d' + str(size) + '): ' + uname + ' rolled a ' + str(r1)
  return msg

# helper for when new client enters room, track
def add_client(clients, room):
  # take set difference of new list of clients and old
  # difference should be one new client added
  global last_client 
  global r_to_client
  new_client = list(set(clients) - set(last_client))
  if room not in r_to_client.keys():
    r_to_client[room] = []  # if empty, create new list
  r_to_client[room].append(new_client[0]) # append first element in collection, new client
  last_client = clients # save new client list

# helper to determine what type of request based on header, form response
def decide_request(req, uname, clients, room):
  resp = ""
  req_type = req['type']
  if req_type == 'enter':
    # person has joined room, must take difference of new clients list and old
    # use to track person in room
    add_client(clients, room)
    resp = {'msg': uname + ' has entered the battle!', 'color': 'red', 'type': 'status'}
  elif req_type == 'text':
    # someone is sending a message
    resp = {'msg': uname + ': ' + req['msg'], 'color': 'blue', 'type': 'chat'}
  elif req_type == 'dice_roll':
    # someone is asking for dice rolls
    msg = roll_dice(int(req['dice_type']), req['adv'], req['disadv'], uname)
    resp = {'msg': msg, 'color':'green', 'weight':'bold', 'type': 'roll'}
  return json.dumps(resp) # convert JSON to string



# begin listening for different socket events

# on client joining chat room, process request and decide how to form response
@sockets.route('/play')
def chat_socket(ws):
  # while socket is open, process messages
  while not ws.closed:
    message = ws.receive()
    if message is None:  # message is "None" if the client has closed.
      continue
    # store name of sender
    uname = session.get('name')
    global r_to_client
    msg = json.loads(message) # convert to dict
    # now process message dependent on type + room, clients
    clients = list(ws.handler.server.clients.values())
    room = session.get('room')
    resp = decide_request(msg, uname, clients, room)
    # send response to every one in sender's room
    # filter out clients that aren't in room
    #in_room = list(filter(lambda x: x.address in r_to_ip[room], clients))
    for client in r_to_client[room]:
      print("sending")
      print(resp)
      client.ws.send(resp)
    

'''

# on client leaving room
@socketio.on('left', namespace='/play')
def handle_leave(message):
    room = session.get('room')
    uname = session.get('name')
    leave_room(room)
    emit('status', {'msg': uname + ' has left the battle!', 'color': 'red'}, room=room)

'''
@app.route('/')
def root():
    return redirect("/static/index.html", code=302)

@app.route('/play')
def play():
    #print ('in play\n')
    room = session.get('room')
    name = session.get('name')
    return render_template('play.html', room=room, name=name)

#post to join room, store session data for user
# redirect them to play url
@app.route('/joinRoom', methods=['POST'])
def join_post():
  # store session info for use
  session['name'] = request.form['uname']
  session['room'] = request.form['rname']
  #rname = request.form['rname']
  '''
  # store IP, port tuple of client connected to room
  client_tup = (request.remote_addr, int(request.environ.get('REMOTE_PORT')))
  print(client_tup) # DEBUG
  if rname in r_to_ip.keys():
    r_to_ip[rname].append(client_tup)
  else:
    r_to_ip[rname] = []
    r_to_ip[rname].append(client_tup)
  #msg = session.get('name') + ' joined room: ' + session.get('room')
  #print(msg)
  '''
  return redirect(url_for('.play'), code=302)

# disabling caching by modifying headers of each response
@app.after_request
def add_header(resp):
  resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
  resp.headers['Pragma'] = 'no-cache'
  resp.headers['Expires'] = '0'
  return resp


if __name__ == '__main__':
  print("""
  This can not be run directly because the Flask development server does not
  support web sockets. Instead, use gunicorn:

  gunicorn -b 127.0.0.1:8080 -k flask_sockets.worker main:app

  """)
