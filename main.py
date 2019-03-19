from flask import Flask, url_for, redirect, render_template, request
from flask import session, jsonify
from flask_sockets import Sockets
from flask_pymongo import PyMongo
import random
import json
from yattag import Doc

app = Flask(__name__)
app.config['SECRET_KEY'] = 'memeslol'
app.config['MONGO_URI'] = "mongodb+srv://admin:1520isanepicclass%5F@dnd1520-zn4pg.gcp.mongodb.net/play?retryWrites=true"
# initialize mongo client for db ops
mongo = PyMongo(app)


sockets = Sockets(app)             # create socket listener
u_to_client = {}                  # map users to Client object
r_to_client = {}                # map room to list of Clients connected`(uses Object from gevent API)
last_client = []            # use to store previous clients list, compare to track clients
single_events = ['get_sheet'] # track events where should only be sent to sender of event, i.e. not broadcast

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

# helper for when new client enters room, store new Client object, map uname to Client object for removal
def add_client(clients, room, uname):
  # take set difference of new list of clients and old
  # difference should be one new client added
  global last_client
  global r_to_client
  global u_to_client
  new_client = list(set(clients) - set(last_client))
  if room not in r_to_client.keys():
    r_to_client[room] = []  # if empty, create new list
  r_to_client[room].append(new_client[0]) # append first element in collection, new client
  u_to_client[uname] = new_client[0]      # store Client for user
  last_client = clients # save new client list

# helper from when client leaves room, remove Client entry for uname and from room list
# update client list
def remove_client(uname, room):
  global last_client
  global r_to_client
  global u_to_client
  to_rem = u_to_client.pop(uname) # remove leaving client's entry and get val
  if to_rem in r_to_client[room]:
    r_to_client[room].remove(to_rem)
  if to_rem in last_client:
    last_client.remove(to_rem)  # client gone

# helper to form sheet for player based on uname and room, can be either psheet or DM, retrieves from DB
# turns into proper HTML format
def get_player_stats(uname, isPlayer, room):
  # build a dict of response stats (HARD CODED FOR TESTING)
  if isPlayer:
    raw_resp = {
      'name': 'Mikey',
      'class': 'Necromancer',
      'race': 'Dark Elf',
      'str': '74',
      'dex': '56',
      'const': '22',
      'intell': '65',
      'wis': '49',
      'char': '33',
      'level': '88',
      'xp': '300',
      'next_xp': '33',
      'languages':
        ['Elvish', 'Dwarf'],
      'enhan':
        ['fat', 'cool', 'memes'],
      'resist':
        ['air', 'fire'],
      'special':
        ['Breathe water', 'fire breath'],
      'armor': '29',
      'hp': '350',
      'heroics': '15',
      'weapons':
        [{'name': 'Greatsword', 'to_hit': '22',
        'damage': '35', 'range': '12', 'notes': 'It sucks'},
        {'name': 'Holy Bow', 'to_hit': '45',
        'damage': '22', 'range': '65', 'notes': 'Will kill you'}],
      'items':
        [{'name': 'special ring', 'weight': '8', 'notes': 'kills things'},
        {'name': 'old book', 'weight': '12', 'notes': 'eerie...'}],
      'total_weight': '20',
      'max_weight': '100',
      'base_speed': '30',
      'curr_speed': '50',
      'condition': 'fair',
      'treasures':
        {'gp': '32', 'cp': '22',
        'pp': '0', 'ep': '20', 'sp': '0',
        'gems': [{'name': 'rubies', 'num': '2'},
          {'name': 'sapphires', 'num': '3'}]},
      'type': 'sheet'
    }
    # use dict to build HTML using library
    doc, tag, text = Doc().tagtext()
    with tag('div', klass = 'row'):
      with tag('div', klass = 'col sheet_title'):
        text('~ Player Sheet ~')
    with tag('div', klass = 'row'):
      with tag('div', klass = 'col namebox'):
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col namefields'):
            text('Name: ' + raw_resp['name'])
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col namefields'):
            text('Class: ' + raw_resp['class'])
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col namefields'):
            text('Race: ' + raw_resp['race'])
      with tag('div', klass = 'col levelbox'):
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col levelfields'):
            text('Level: ' + raw_resp['level'])
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col levelfields'):
            text('Experience Points: ' + raw_resp['xp'])
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col levelfields'):
            text('Next Level Exp: ' + raw_resp['next_xp'])
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col levelfields'):
            text('Languages: ' + (', ').join(raw_resp['languages']))
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col levelfields'):
            text('Conditions + Enchancements: ' + (', ').join(raw_resp['enhan']))
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col levelfields'):
            text('Resistances: ' + (', ').join(raw_resp['resist']))
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col levelfields'):
            text('Special Skills + Abilities: ' + (', ').join(raw_resp['special']))
    with tag('div', klass = 'row'):
      with tag('div', klass = 'col attrbox'):
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col str'):
            text(raw_resp['str'] + ' Strength')
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col dex'):
            text(raw_resp['dex'] + ' Dexterity')
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col const'):
            text(raw_resp['const'] + ' Constitution')
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col intell'):
            text(raw_resp['intell'] + ' Intelligence')
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col wis'):
            text(raw_resp['wis'] + ' Wisdom')
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col char'):
            text(raw_resp['char'] + ' Charisma')
      with tag('div', klass = 'col statbox'):
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col armor'):
            text(raw_resp['armor'])
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col'):
            text('Armor Class')
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col hp'):
            text(raw_resp['hp'])
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col'):
            text('Hit Points')
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col heroics'):
            text(raw_resp['heroics'])
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col'):
            text('Heroics')
    with tag('div', klass = 'row'):
      with tag('div', klass = 'col wepbox'):
        with tag('div', klass = 'row'):
          with tag('div', klass = 'col wepfields'):
            text('Weapon')
          with tag('div', klass = 'col wepfields'):
            text('To Hit')
          with tag('div', klass = 'col wepfields'):
            text('Damage')
          with tag('div', klass = 'col wepfields'):
            text('Range')
          with tag('div', klass = 'col wepfields'):
            text('Notes')
        for weapon in raw_resp['weapons']:
          with tag('div', klass = 'row'):
            with tag('div', klass = 'col wepfields'):
              text(weapon['name'])
            with tag('div', klass = 'col wepfields'):
              text(weapon['to_hit'])
            with tag('div', klass = 'col wepfields'):
              text(weapon['damage'])
            with tag('div', klass = 'col wepfields'):
              text(weapon['range'])
            with tag('div', klass = 'col wepfields'):
              text(weapon['notes'])
  else:
    #fake response and probably wont have the same parameters as a real one
    raw_resp = {
      'notes' : 'here are my notes we can just save this as plaintext maybe i will find a \nway to make a rich text editor so we can format \nthings better that would be cool.',
      'monsters' : [{
        'type':'man',
        'health':'50',
        'armor class':'13',
        'attack': '12',
        'size':'biig'
      },{
        'type':'cat',
        'health':'1000000',
        'armor class':'1000000',
        'attack': '1000000',
        'size':'small'
      }],
      'encounter' : {
        'monsters':[{
          'name' : 'Big man',
          'type' : 'man'
        },{
          'name' : 'Krusty Louis',
          'type' : 'cat'
        }],
        'turnorder':[]
      }
    }
    # use dict to build HTML using library
    doc, tag, text = Doc().tagtext()
    with tag('div', klass = 'row'):
      with tag('div', klass = 'col sheet_title'):
        text(' ~ DM Sheet ~ ')
    with tag('div', klass = 'row'):
      with tag('div', klass = 'col dmbutton', id='encounter'):
        text('Encounter')
      with tag('div', klass = 'col dmbutton', id='monster'):
        text('Monsters')
      with tag('div', klass = 'col dmbutton', id='notes'):
        text('Notes')
    with tag('div', klass = 'row dmcontent'):
      with tag('div', klass = 'col dmnotes', id='shown'):
        with tag('textarea', placeholder='Notes for campaign go here...', id='dmtextarea'):
          text(raw_resp['notes'])
      with tag('div', klass = 'col dmmonster', id='hidden'):
        with tag('div', klass = 'col col-xs-4 col-sm-4 col-md-4 dmmonsterlist'):
          with tag('div', klass='row'):
            with tag('div', klass='col'):
              text('Monster List')
          with tag('div', klass='row'):
            with tag('div', klass='col', id='mmonsterlist'):
              for monster in raw_resp['monsters']:
                with tag('div', klass = 'col'):
                  text(monster['type'])
                  with tag('div', klass='json'+monster['type'] ,id='hidden'):
                    text(str(monster))
        with tag('div', klass = 'col col-xs-8 col-sm-8 col-md-8 dmmonsteredit'):
          with tag('div', klass = 'row'):
            with tag('div', klass = 'col', id='monsteredit'):
              text('Edit monsters here.')
      with tag('div', klass = 'col dmencounter', id='hidden'):
        with tag('div', klass = 'col col-xs-4 col-sm-4 col-md-4 dmmonsterlist'):
          with tag('div', klass='row'):
            with tag('div', klass='col'):
              text('Monster List')
          with tag('div', klass='row'):
            with tag('div', klass='col', id='emonsterlist'):
              for monster in raw_resp['monsters']:
                with tag('div', klass = 'col'):
                  text(monster['type'])
                  with tag('div', klass='json'+monster['type'], id='hidden'):
                    text(str(monster))
        with tag('div', klass = 'col-xs-8 col-sm-8 col-md-8 dmencountercontent'):
          with tag('div', klass = 'col dmturnorder'):
            text('turn order stuff here')
          with tag('div', klass = 'col', id='dmmonsterinfo'):
            text('specific enemy info here')
  resp = doc.getvalue()
  return resp

# helper to determine what type of request based on header, form response
def decide_request(req, uname, isPlayer, clients, room):
  resp = ""
  req_type = req['type']
  if req_type == 'enter':
    # person has joined room, must take difference of new clients list and old
    # use to track person in room
    add_client(clients, room, uname)
    resp = {'msg': uname + ' has entered the battle!', 'color': 'red', 'type': 'status'}
  elif req_type == 'text':
    # someone is sending a message
    resp = {'msg': uname + ': ' + req['msg'], 'color': 'blue', 'type': 'chat'}
  elif req_type == 'dice_roll':
    # someone is asking for dice rolls
    msg = roll_dice(int(req['dice_type']), req['adv'], req['disadv'], uname)
    resp = {'msg': msg, 'color':'green', 'weight':'bold', 'type': 'roll'}
  elif req_type == 'leave':
    # someone leaving the room, remove from room client list to avoid issues, print status
    remove_client(uname, room)
    resp = {'msg': uname + ' has left the battle.', 'color': 'red', 'type': 'status'}
  elif req_type == 'get_sheet':
    # client asking for psheet OR DM info, depending on type, send requested info in JSON
    data = get_player_stats(uname, isPlayer, room)
    if isPlayer:
        resp = {'msg': data, 'type': 'sheet'}
    else:
        resp = {'msg': data, 'type': 'dmstuff'}
  return json.dumps(resp) # convert JSON to string



# begin listening for different socket events

# on client sending socket message, process request and decide how to form response
@sockets.route('/play')
def chat_socket(ws):
  # while socket is open, process messages
  while not ws.closed:
    message = ws.receive()
    if message is None:  # message is "None" if the client has closed.
      continue
    # store name of sender
    uname = session.get('name')
    isPlayer = session.get('isPlayer')
    global r_to_client
    global u_to_client
    msg = json.loads(message) # convert to dict
    # now process message dependent on type + room, clients
    clients = list(ws.handler.server.clients.values())
    room = session.get('room')
    resp = decide_request(msg, uname, isPlayer, clients, room)
    # check if broadcast or single event
    broadcast = True if msg['type'] not in single_events else False
    # send response to every one in sender's room if broadcast
    if broadcast:
      for client in r_to_client[room]:
        print("sending")
        print(resp)
        client.ws.send(resp)
    else:
      # otherwise only to sender of event
      curr = u_to_client[uname]
      print("sending")
      print(resp)
      curr.ws.send(resp)


@app.route('/')
def root():
    return redirect("/static/index.html", code=302)

@app.route('/play')
def play():
    #print ('in play\n')
    room = session.get('room')
    name = session.get('name')
    isPlayer = session.get('isPlayer')
    return render_template('play.html', room=room, name=name, isPlayer=isPlayer)

#post to join room, store session data for user
# redirect them to play url
@app.route('/joinRoom', methods=['POST'])
def join_post():
  # store session info for use
  session['name'] = request.form['uname']
  session['room'] = request.form['rname']
  session['isPlayer'] = True if request.form['isPlayer'] == "Player" else False
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
