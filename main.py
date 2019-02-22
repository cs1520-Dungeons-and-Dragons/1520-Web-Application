from flask import Flask, url_for, redirect, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'memeslol'

socketio = SocketIO(app)             # create socket listener


# begin listening for different socket events
# on connection
@socketio.on('connection')
def handle_connect(data):
    status = data['data']
    print (status)
    return 

# on client joining room takes json data of player info
'''
@socketio.on('joinRoom')
def handle_join(data):
    room = data['room']
    uname = data['username']
    print (room)            # DEBUg
    print (uname)           # DEBUG
    return redirect(url_for('play'))
'''

@app.route('/')
def root():
    return redirect("/static/index.html", code=302)

@app.route('/play')
def play():
    return

#ajax post to join room
@app.route('/joinRoom', methods=['POST'])
def join_post():
    print (str(request.json['user']))
    return 'success'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
