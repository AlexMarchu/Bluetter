import sys
import random

from PyQt6 import QtCore, QtWidgets, QtGui

from network import Client, Server

class Application(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setupConnection()

        self.setWindowTitle('Blutter')
        self.setWindowIcon(QtGui.QIcon('assets/icon.png'))

        font = QtGui.QFont()
        font.setPointSize(32) 

        self.messageQueue = list()

        self.__text = QtWidgets.QLabel('Hello World', alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.__text.setFont(font)

        self.__button = QtWidgets.QPushButton('Click Me!')
        self.__button.setFont(font)
        self.__button.clicked.connect(self.response)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.__text)
        self.layout.addWidget(self.__button)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateText)
        self.timer.start(1)

    def setupConnection(self):
        try:
            self.__socket = Client(self)
        except ConnectionRefusedError:
            self.__socket = Server(self)
            self.__socket.run()

    def updateText(self) -> None:
        if self.messageQueue:
            newMessage = self.messageQueue.pop(0)
            self.__text.setText(newMessage)

    def receiveMessage(self, message) -> None:
        self.messageQueue.append(message)

    def response(self):
        messages = [
            'Привет, мир!',   
            'Hello, World!',  
            'Hola, Mundo!',
            'Bonjour, le monde!',  
            'Hallo, Welt!',   
            'Ciao, Mondo!',   
            'こんにちは、世界！',  
            '안녕, 세계야!',   
            'Olá, Mundo!',    
            'नमस्ते दुनिया!',  
        ]
        self.__socket.sendMessage(random.choice(messages))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    widget = Application()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())