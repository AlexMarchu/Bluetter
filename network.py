import socket 
import threading 

class SocketConnection():
    def __init__(self, app, host='127.0.0.1', port=2000) -> None:
        self.host = host 
        self.port = port
        self.app = app 
        self.socket = None

    def sendMessage(self, message: str) -> None:
        self.socket.send(message.encode('utf-8'))

    def listen(self) -> None:
        while True:
            data = self.socket.recv(1024).decode('utf-8')
            self.app.receiveMessage(data)

class Client(SocketConnection):
    def __init__(self, app, host='127.0.0.1', port=2000) -> None:
        super().__init__(app, host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        threading.Thread(target=self.listen, daemon=True).start()

class Server(SocketConnection):
    def __init__(self, app, host='127.0.0.1', port=2000) -> None:
        super().__init__(app, host, port)
        self.clientSocket = None

    def run(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(16)
        print(f'🟢 Server started on {self.host}:{self.port}.')

        self.clientSocket, self.clientAddress = self.socket.accept()
        print(f'Client {self.clientAddress} connected.')

        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self) -> None:
        while True:
            data = self.clientSocket.recv(1024).decode('utf-8')
            self.app.receiveMessage(data)

    def sendMessage(self, message: str) -> None:
        self.clientSocket.send(message.encode('utf-8'))
        