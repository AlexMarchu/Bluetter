import socket

class Client:
    def __init__(self, host='127.0.0.1', port=2000) -> None:
        self.__host = host
        self.__port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.__host, self.__port))

    def sendMessage(self, message: str = 'Hello from client.') -> None:
        self.client.send(bytes(message, encoding='utf-8'))

        response = self.client.recv(1024).decode('utf-8')
        print(f'Server answered: {response}')
