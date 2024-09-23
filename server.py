import socket
import threading

class Server:
    def __init__(self, adminApp, host='127.0.0.1', port=2000) -> None:
        self.__host = host
        self.__port = port
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__adminApp = adminApp

    def run(self) -> None:
        self.__server.bind((self.__host, self.__port))
        self.__server.listen(16)
        print(f'🟢 Server started on {self.__host}:{self.__port}.')
        self.clientSocket, self.clientAddress = self.__server.accept()
        print(f'Client {self.clientSocket} connected.')
        threading.Thread(target=self.acceptConnections, daemon=True).start()

    def acceptConnections(self) -> None:
        while True:
            data = self.clientSocket.recv(1024).decode('utf-8')
            print(f'Received message: {data}.')

            self.__adminApp.receiveMessage(data)

            self.clientSocket.send('Hello from server.'.encode('utf-8'))
