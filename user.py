import sys
import random
from PyQt6 import QtWidgets, QtGui
from client import Client

class UserApp(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.__clientSocket = Client()

        self.setWindowTitle("User")
        self.setWindowIcon(QtGui.QIcon('assets/icon.png'))

        self.helloMessages = [
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

        self.button = QtWidgets.QPushButton('Click Me!')
        self.button.clicked.connect(self.magic)

        font = QtGui.QFont()
        font.setPointSize(32) 
        self.button.setFont(font)
        self.button.adjustSize()

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.button)

    def magic(self) -> None:
        self.__clientSocket.sendMessage(random.choice(self.helloMessages))

if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    widget = UserApp()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
