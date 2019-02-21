from flask import Flask
from flask import redirect
from flask_socketio import SocketIO

io = SocketIO()             # create socket listener

app = Flask(__name__)

# begin listening for different socket events


@app.route('/')
def root():
    return redirect("/static/index.html", code=302)



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
