import socket
import threading

class SocketConnection:

    def __init__(self, app, host="127.0.0.1", port=2000) -> None:
        self.host = host
        self.port = port
        self.app = app 
        self.socket = None

    def send_message(self, message: str) -> None:
        message = "TXT:" + message + "||"
        self.socket.sendall(message.encode("utf-8"))

    def send_image(self, image_data: str) -> None:
        message = "IMG:" + image_data + "||"
        self.socket.sendall(message.encode("utf-8"))

    def listen(self) -> None:
        buffer = ""
        while True:
            try:
                data = self.socket.recv(4096).decode("utf-8")
                if not data:
                    break  # Break if connection is closed
                buffer += data
                while "||" in buffer:
                    header, buffer = buffer.split("||", 1)
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
        # self.socket.connect((self.host, self.port))
        self.server_ip = None

        # self.connect_to_server()

    def connect_to_server(self) -> None:
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_socket.bind(('', 2001))

        print("Looking for the server...")

        while not self.server_ip:
            data, address = udp_socket.recvfrom(1024)
            message = data.decode("utf-8")
            if message.startswith("SERVER_IP:"):
                self.server_ip = message.split(":")[1]

                print(f"Server {self.server_ip} founded")
                break

        if self.server_ip:
            print(1)
            self.socket.connect((self.server_ip, 2000))
            print("Connected to the server.")
            self.start_listen()


    def start_listen(self) -> None:
        threading.Thread(target=self.listen, daemon=True).start()

class Server(SocketConnection):
    def __init__(self, app, host="127.0.0.1", port=2000) -> None:
        super().__init__(app, host, port)
        self.broadcast_event = threading.Event()

    def broadcast_ip(self) -> None:
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        server_ip = socket.gethostbyname(socket.gethostname())
        broadcast_message = f"SERVER_IP:{server_ip}".encode("utf-8")

        while not self.broadcast_event.is_set():
            broadcast_socket.sendto(broadcast_message, ('<broadcast>', 2001))
            print(f"Broadcasting server: {server_ip}")

            self.broadcast_event.wait(1)

    def run(self) -> None:
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("", self.port))
        self.server_socket.listen(16)
        print(f"🟢 Server started on {self.host}:{self.port}. Broadcasting IP for client...")

        self.broadcast_thread = threading.Thread(target=self.broadcast_ip, daemon=True).start()

        self.client_socket, self.client_address = self.server_socket.accept()
        self.socket = self.client_socket
        print(f"Client {self.client_address} connected.")

        self.broadcast_event.set()
        # if self.broadcast_thread.is_alive():
        #     self.broadcast_thread.join()

        # print("Broadcasting stopped.")
        # self.app.connection_signal.emit()
        threading.Thread(target=self.listen, daemon=True).start()