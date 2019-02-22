from flask import Flask
from flask import redirect
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

# on client joining room takes json data
@socketio.on('joinRoom')
def handle_join(data):
    room = data['room']
    print (room)
    return

@app.route('/')
def root():
    return redirect("/static/index.html", code=302)



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
