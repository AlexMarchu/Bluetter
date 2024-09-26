import sys
import random
import os
import base64

from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtGui import QPixmap

from network import Client, Server

class Application(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setup_connection()

        self.setWindowTitle("Blutter")
        self.setWindowIcon(QtGui.QIcon("assets/icon.png"))

        font = QtGui.QFont()
        font.setPointSize(32)

        self.message_queue = list()

        self.__text = QtWidgets.QLabel("Hello World", alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.__text.setFont(font)

        self.__button = QtWidgets.QPushButton("Click Me!")
        self.__button.setFont(font)
        self.__button.clicked.connect(self.response)

        self.__image_button = QtWidgets.QPushButton("Send Image")
        self.__image_button.setFont(font)
        self.__image_button.clicked.connect(self.send_image)

        self.__image_label = QtWidgets.QLabel(self)
        self.__image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.__text)
        self.layout.addWidget(self.__button)
        self.layout.addWidget(self.__image_button)
        self.layout.addWidget(self.__image_label)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_text)
        self.timer.start(100)

    def setup_connection(self) -> None:
        try:
            self.__socket = Client(self)
        except ConnectionRefusedError:
            self.__socket = Server(self)
            self.__socket.run()

    def update_text(self) -> None:
        if self.message_queue:
            new_message = self.message_queue.pop(0)
            self.__text.setText(new_message)

    def receive_message(self, message) -> None:
        if message.startswith("IMG:"):
            image_data = message[4:]
            pixmap = QPixmap()
            pixmap.loadFromData(QtCore.QByteArray.fromBase64(image_data.encode("utf-8")))
            self.__image_label.setPixmap(pixmap)
        elif message.startswith("TXT:"):
            text_message = message[4:]
            self.message_queue.append(text_message)
        else:
            print(f"Unknown message type: {message}")

    def response(self):
        messages = [
            "Привет, мир!",   
            "Hello, World!",  
            "Hola, Mundo!",
            "Bonjour, le monde!",  
            "Hallo, Welt!",   
            "Ciao, Mondo!",   
            "こんにちは、世界！",  
            "안녕, 세계야!",   
            "Olá, Mundo!",    
            "नमस्ते दुनिया!",  
        ]
        selected_message = random.choice(messages)
        print(f"Sending message: {selected_message}")
        self.__socket.send_message(selected_message)

    def send_image(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            if os.path.exists(file_path):
                with open(file_path, "rb") as image_file:
                    image_data = image_file.read()
                    encoded_image = base64.b64encode(image_data).decode()
                    print(f"Sending image: {encoded_image[:30]}...")
                    self.__socket.send_image(encoded_image)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    widget = Application()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
