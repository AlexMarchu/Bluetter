import sys
from PyQt6 import QtCore, QtWidgets, QtGui
from server import Server

class AdminApp(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Admin")
        self.setWindowIcon(QtGui.QIcon('assets/icon.png'))

        font = QtGui.QFont()
        font.setPointSize(32) 

        self.messageQueue = list()

        self.__text = QtWidgets.QLabel('Hello World', alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.__text.setFont(font)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.__text)

        self.__serverSocket = Server(self)
        self.__serverSocket.run()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateText)
        self.timer.start(1)

    def updateText(self) -> None:
        if self.messageQueue:
            newMessage = self.messageQueue.pop(0)
            self.__text.setText(newMessage)

    def receiveMessage(self, message) -> None:
        self.messageQueue.append(message)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    widget = AdminApp()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
