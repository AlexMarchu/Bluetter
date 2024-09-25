import sys
from PyQt6 import QtCore, QtWidgets, QtGui

FONT = QtGui.QFont("Segoe UI", 12)
FONT_METRICS = QtGui.QFontMetrics(FONT)
MAX_MESSAGE_WIDTH = 200

class QMessage(QtWidgets.QFrame):

    def __init__(self, parent: QtWidgets.QWidget, text: str) -> None:
        super().__init__(parent)
        self.content = QtWidgets.QLabel(self, text = text)
        #self.content.setStyleSheet("background-color: black;")
       
        width = min(MAX_MESSAGE_WIDTH, FONT_METRICS.size(0, text).width())
        self.content.setWordWrap(True)
        self.content.setFixedWidth(width)
        self.content.adjustSize()
        
        self.setFixedSize(width + 16, self.content.height() + 8)
        self.content.move(8, 4)

class QWindow(QtWidgets.QWidget):

    def __init__(self) -> None:
        super().__init__()

        self.setObjectName("window")
        self.setFixedSize(450, 520)
        self.setWindowTitle("Bluetter")
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap("assets/icons/logo.png")))

        window_layout = QtWidgets.QVBoxLayout()
        window_layout.setSpacing(0)
        window_layout.setContentsMargins(0, 0, 0, 14)
        self.setLayout(window_layout)

        self.title = QtWidgets.QLabel()
        self.title.setObjectName("title")
        self.title.setFixedHeight(41)
        self.title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        window_layout.addWidget(self.title)

        self.separator = QtWidgets.QFrame()
        self.separator.setObjectName("separator")
        self.separator.setFixedHeight(2)

        window_layout.addWidget(self.separator)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area_content = QtWidgets.QWidget()
        self.scroll_area_content.setObjectName("scroll_area_content")
        self.scroll_area.setWidget(self.scroll_area_content)

        window_layout.addWidget(self.scroll_area)

        self.input_panel = QtWidgets.QWidget()
        self.input_panel.setFixedHeight(54)

        panel_layout = QtWidgets.QHBoxLayout()
        panel_layout.setSpacing(0)
        panel_layout.setContentsMargins(9, 3, 9, 9)

        self.input_panel.setLayout(panel_layout)

        self.message_input = QtWidgets.QPlainTextEdit()
        self.message_input.setObjectName("message_input")
        self.message_input.setFixedSize(372, 46)
        self.message_input.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.message_input.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.message_input.setPlaceholderText("Введите сообщение...")

        panel_layout.addWidget(self.message_input)

        self.send_button = QtWidgets.QPushButton()
        self.send_button.setObjectName("send_button")
        self.send_button.setFixedSize(46, 46)
        
        self.send_button.setIcon(QtGui.QIcon(QtGui.QPixmap("assets/icons/send.png")))
        self.send_button.setIconSize(QtCore.QSize(28, 28))

        panel_layout.addWidget(self.send_button)
        window_layout.addWidget(self.input_panel)

        self.current_y = 15
    
    def addMessage(self, text: str, alignment: QtCore.Qt.AlignmentFlag) -> None:
        message = QMessage(self.scroll_area_content, text)

        if alignment == QtCore.Qt.AlignmentFlag.AlignLeft:
            side = "left"
            x = 10
        else:
            side = "right"
            x = self.width() - 10 - message.width()
        
        message.setProperty("alignment", side)
        message.move(x, self.current_y)
        self.current_y += message.height() + 15
        self.scroll_area_content.setFixedHeight(self.current_y)
        
        message.show()

def loadStyleSheet() -> str:
    file = QtCore.QFile("assets/styles/style.qss")
    file.open(QtCore.QIODeviceBase.OpenModeFlag.ReadOnly | QtCore.QIODeviceBase.OpenModeFlag.Text)
    styleSheet = str(file.readAll(), encoding = "utf-8")
    file.close()

    return styleSheet

if __name__ == "__main__":
    application = QtWidgets.QApplication(sys.argv + ["-platform", "windows:darkmode=0"])
    application.setStyleSheet(loadStyleSheet())
    application.setFont(FONT)

    window = QWindow()
    window.show()

    window.addMessage("Привет!", QtCore.Qt.AlignmentFlag.AlignLeft)
    window.addMessage("Ну привет!", QtCore.Qt.AlignmentFlag.AlignRight)
    window.addMessage("Как дела?", QtCore.Qt.AlignmentFlag.AlignLeft)
    window.addMessage("Да ахуенно! А у тебя?", QtCore.Qt.AlignmentFlag.AlignRight)

    sys.exit(application.exec())