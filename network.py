import socket
import threading

class SocketConnection:

    def __init__(self, app, host="127.0.0.1", port=2000) -> None:
        self.host = host
        self.port = port
        self.app = app 
        self.socket = None

    def send_message(self, message: str) -> None:
        message = "TXT:" + message + "\n"
        self.socket.sendall(message.encode("utf-8"))

    def send_image(self, image_data: str) -> None:
        message = "IMG:" + image_data + "\n"
        self.socket.sendall(message.encode("utf-8"))

    def listen(self) -> None:
        buffer = ""
        while True:
            try:
                data = self.socket.recv(4096).decode("utf-8")
                if not data:
                    break  # Break if connection is closed
                buffer += data
                while "\n" in buffer:
                    header, buffer = buffer.split("\n", 1)
                    if header.startswith("IMG:") or header.startswith("TXT:"):
                        self.app.receive_signal.emit(header)
                    else:
                        print(f"Unknown message type received: {header}")
            except Exception as e:
                print(f"Connection error: {e}")
                break

class Client(SocketConnection):
    def __init__(self, app, host="127.0.0.1", port=2000) -> None:
        super().__init__(app, host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        threading.Thread(target=self.listen, daemon=True).start()

class Server(SocketConnection):
    def __init__(self, app, host="127.0.0.1", port=2000) -> None:
        super().__init__(app, host, port)

    def run(self) -> None:
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(16)
        print(f"🟢 Server started on {self.host}:{self.port}.")

        self.client_socket, self.client_address = self.server_socket.accept()
        self.socket = self.client_socket
        print(f"Client {self.client_address} connected.")

        threading.Thread(target=self.listen, daemon=True).start()