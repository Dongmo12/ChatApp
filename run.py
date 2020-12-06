from app import app
from app import application


if __name__ == "__main__":
    application.socketio.run(app, debug = True)
