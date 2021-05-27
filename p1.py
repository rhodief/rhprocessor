import time
import zmq

#sudo netstat -ltnp    kill -9 <pid>

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    message = socket.recv()
    print(f"Received request: {message}")

    socket.send(b"World")