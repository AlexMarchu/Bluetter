import sys, base64, io
from PyQt6 import QtCore, QtWidgets, QtGui
from network import Client, Server
from PIL import Image, ImageDraw

FONT = QtGui.QFont("Segoe UI", 12)
FONT_METRICS = QtGui.QFontMetrics(FONT)
MAX_MESSAGE_WIDTH = 200
MAX_MESSAGE_TEXT_EDIT_HEIGHT = 130
MESSAGE_EDIT_WIDTH = 370

class QMessage(QtWidgets.QFrame):

    def __init__(self, alignment: QtCore.Qt.AlignmentFlag, text: str = "", attachment: QtCore.QByteArray = None) -> None:
        super().__init__()

        width = MAX_MESSAGE_WIDTH if attachment else min(MAX_MESSAGE_WIDTH, FONT_METRICS.size(0, text).width())        
        self.setProperty("alignment", "left" if alignment == QtCore.Qt.AlignmentFlag.AlignLeft else "right")

        y = 4

        if text:
            self.text_label = QtWidgets.QLabel(self, text = text)
            self.text_label.setWordWrap(True)
            self.text_label.setFixedWidth(width)
            self.text_label.adjustSize()
            self.text_label.move(8, y)
            y += self.text_label.height() + 4
        
        if attachment:
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(attachment.data())
            r = pixmap.height() / pixmap.width()
            height = int(r * width)
            self.attachment_label = QtWidgets.QLabel(self)
            self.attachment_label.setObjectName("attachment")
            self.attachment_label.setPixmap(pixmap)
            self.attachment_label.setScaledContents(True)
            self.attachment_label.setFixedSize(width, height)
            self.attachment_label.move(8, y)
            y += height + 4

        self.alignment = alignment
        self.setFixedSize(width + 16, y)
    
    def get_rounded_image(self, image_bytes: bytes) -> QtCore.QByteArray:
        image = Image.open(io.BytesIO(image_bytes))
        rounded_image = Image.new("RGBA", image.size)
        draw = ImageDraw.Draw(rounded_image)
        draw.rounded_rectangle([(0, 0), image.size], 10, fill = "white")
        result = Image.alpha_composite(image.convert('RGBA'), rounded_image)
        byte_array = io.BytesIO()
        result.save(byte_array, image.format)
        return QtCore.QByteArray(byte_array.getvalue())

class QMessageEdit(QtWidgets.QFrame):

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)

        self.setGeometry(20, 0, MESSAGE_EDIT_WIDTH, 70)

        self.attachment = None

        self.attachment_label = QtWidgets.QLabel(self)
        self.attachment_label.setObjectName("attachment_label")
        self.attachment_label.setGeometry(12, 24, MESSAGE_EDIT_WIDTH - 24, 22)

        self.remove_attachment_button = QtWidgets.QPushButton(self.attachment_label)
        self.remove_attachment_button.setObjectName("remove_attachment_button")
        self.remove_attachment_button.setGeometry(MESSAGE_EDIT_WIDTH - 46, 0, 22, 22)
        self.remove_attachment_button.setIcon(QtGui.QIcon(QtGui.QPixmap("assets/icons/cross.png")))
        self.remove_attachment_button.setIconSize(QtCore.QSize(16, 16))
        self.remove_attachment_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        self.text_edit = QtWidgets.QPlainTextEdit(self)
        self.text_edit.setObjectName("text_edit")
        self.text_edit.setGeometry(0, 24, MESSAGE_EDIT_WIDTH, 46)
        self.text_edit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_edit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_edit.setPlaceholderText("Введите сообщение...")

        self.attachment_button = QtWidgets.QPushButton(self.text_edit)
        self.attachment_button.setObjectName("attachment_button")
        self.attachment_button.setGeometry(MESSAGE_EDIT_WIDTH - 46, 0, 46, 46)
        self.attachment_button.setIcon(QtGui.QIcon(QtGui.QPixmap("assets/icons/attachment.png")))
        self.attachment_button.setIconSize(QtCore.QSize(28, 28))
        self.attachment_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        self.attachment_animation = QtCore.QPropertyAnimation(self.attachment_label, b"pos")
        self.attachment_animation.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
        self.attachment_animation.setDuration(250)
        self.attachment_animation.setStartValue(self.attachment_label.pos())
        self.attachment_animation.setEndValue(QtCore.QPoint(12, 0))

        self.text_edit.textChanged.connect(self.update_height)
        self.attachment_button.clicked.connect(self.add_attachment)
        self.remove_attachment_button.clicked.connect(self.remove_attachment)

        self.text_edit.textChanged.connect(self.update_state)
    
    def update_state(self) -> None:
        if self.text_edit.toPlainText():
            self.attachment_button.setDisabled(True)
        else:
            self.attachment_button.setDisabled(False)
    
    def update_height(self) -> None:
        lines = self.text_edit.document().lineCount() - 1
        height = min(MAX_MESSAGE_TEXT_EDIT_HEIGHT, 46 + lines * 23)
        self.setFixedHeight(height + 24)
        self.text_edit.setFixedHeight(height)
        self.parent().setFixedHeight(height + 24)
    
    def add_attachment(self) -> None:
        file_name = QtWidgets.QFileDialog.getOpenFileName(caption = "Выберите изображение",
            filter = "Изображение (*.png; *.jpg; *.jpeg)")[0]
        if file_name:
            with open(file_name, "rb") as file:
                self.attachment = QtCore.QByteArray(file.read())
            self.attachment_label.setText(file_name)

            self.attachment_animation.setDirection(QtCore.QAbstractAnimation.Direction.Forward)
            self.attachment_animation.start()

            self.text_edit.setDisabled(True)
    
    def remove_attachment(self) -> None:
        if self.attachment:
            self.attachment = None
            self.attachment_animation.setDirection(QtCore.QAbstractAnimation.Direction.Backward)
            self.attachment_animation.start()

            self.text_edit.setDisabled(False)

class QChatWidget(QtWidgets.QScrollArea):

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setObjectName("content_widget")
        self.setWidget(self.content_widget)

        self.content_widget.setFixedHeight(8)
    
    def add_message(self, message: QMessage) -> None:
        message.setParent(self.content_widget)

        if message.alignment == QtCore.Qt.AlignmentFlag.AlignLeft:
            x = 10
        else:
            x = self.content_widget.width() - 10 - message.width()
        
        message.move(x, self.content_widget.height())
        message.show()

        self.content_widget.setFixedHeight(self.content_widget.height() + message.height() + 8)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

class QWindow(QtWidgets.QWidget):
    
    def __init__(self) -> None:
        super().__init__()
        self.receive_signal.connect(self.receive_message)
        
        self.setup_connection()

        self.setFixedSize(450, 520)
        self.setWindowTitle("Bluetter")
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap("assets/icons/logo.png")))

        window_layout = QtWidgets.QVBoxLayout()
        window_layout.setSpacing(0)
        window_layout.setContentsMargins(0, 0, 0, 14)
        self.setLayout(window_layout)

        self.title_label = QtWidgets.QLabel()
        self.title_label.setObjectName("title_label")
        self.title_label.setFixedHeight(41)
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        window_layout.addWidget(self.title_label)

        self.separator = QtWidgets.QFrame()
        self.separator.setObjectName("separator")
        self.separator.setFixedHeight(2)

        window_layout.addWidget(self.separator)

        self.chat_widget = QChatWidget()
        window_layout.addWidget(self.chat_widget)

        self.bottom_container = QtWidgets.QWidget()
        self.bottom_container.setFixedHeight(70)

        self.message_edit = QMessageEdit(self.bottom_container)

        self.send_button = QtWidgets.QPushButton(self.bottom_container)
        self.send_button.setObjectName("send_button")
        self.send_button.setGeometry(394, 22, 46, 46)
        self.send_button.setIcon(QtGui.QIcon(QtGui.QPixmap("assets/icons/send.png")))
        self.send_button.setIconSize(QtCore.QSize(28, 28))
        self.send_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.send_button.clicked.connect(self.send_message)

        window_layout.addWidget(self.bottom_container)
    
    receive_signal = QtCore.pyqtSignal(str)
    
    def check_queue(self) -> None:
        if self.message_queue:
            self.chat_widget.add_message(self.message_queue.pop(0))
    
    def setup_connection(self) -> None:
        # try:
        #     self.socket = Client(self)
        # except ConnectionRefusedError:
        #     self.socket = Server(self)
        #     self.socket.run()
        type = "server"
        if type == "server":
            self.socket = Server(self)
            self.socket.run()
        if type == "client":
            self.socket = Client(self)
            self.socket.connect_to_server()
    
    def send_message(self) -> None:
        text = self.message_edit.text_edit.toPlainText()
        attachment = self.message_edit.attachment
        if text:
            self.socket.send_message(text)
        else:
            encoded_image = base64.b64encode(attachment.data()).decode()
            self.socket.send_image(encoded_image)
        self.chat_widget.add_message(QMessage(QtCore.Qt.AlignmentFlag.AlignRight, text, attachment))

        self.message_edit.remove_attachment()
        self.message_edit.attachment_button.setDisabled(False)
        self.message_edit.text_edit.clear()
        self.message_edit.text_edit.setDisabled(False)

    def receive_message(self, message) -> None:
        if message.startswith("IMG:"):
            image_data = message[4:]
            attachment = QtCore.QByteArray.fromBase64(image_data.encode("utf-8"))
            message = QMessage(alignment = QtCore.Qt.AlignmentFlag.AlignLeft, attachment = attachment)
        elif message.startswith("TXT:"):
            text_message = message[4:]
            message = QMessage(alignment = QtCore.Qt.AlignmentFlag.AlignLeft, text = text_message)
        self.chat_widget.add_message(message)

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

    sys.exit(application.exec())