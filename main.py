from app import create_app,socketio
# from app.extensions import socketio

if __name__ == "__main__":
    app = create_app()
    socketio.run(app)
    # app.run( debug=True)