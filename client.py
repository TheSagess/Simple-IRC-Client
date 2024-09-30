import sys
import socket
import threading
from PyQt5 import QtWidgets, QtGui, QtCore

class IRCClient(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Local IRC Client")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: #2C2C2C; color: white;")

        # Server management
        self.servers = []  # List to store server details
        self.selected_server = QtWidgets.QComboBox()

        # Layouts
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Chat log area
        self.chat_log = QtWidgets.QTextEdit()
        self.chat_log.setReadOnly(True)
        layout.addWidget(self.chat_log)

        # Message input area
        self.message_input = QtWidgets.QLineEdit()
        layout.addWidget(self.message_input)

        # Button layout
        button_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(button_layout)

        # Server selection dropdown
        button_layout.addWidget(self.selected_server)

        # Connect button
        self.connect_button = QtWidgets.QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect)
        button_layout.addWidget(self.connect_button)

        # Add Server button
        self.add_server_button = QtWidgets.QPushButton("Add Server")
        self.add_server_button.clicked.connect(self.add_server)
        button_layout.addWidget(self.add_server_button)

        # Port input
        self.port_input = QtWidgets.QLineEdit()
        self.port_input.setPlaceholderText("Enter server port (e.g., 6667)")
        button_layout.addWidget(self.port_input)

        # Save button
        self.save_button = QtWidgets.QPushButton("Save Chat")
        self.save_button.clicked.connect(self.save_chat)
        button_layout.addWidget(self.save_button)

        self.sock = None
        self.username = "User"

        # Connect message input to send message on Enter
        self.message_input.returnPressed.connect(self.send_message)

    def add_server(self):
        server_address, ok = QtWidgets.QInputDialog.getText(self, "Add Server", "Enter server address (e.g., localhost):")
        if ok and server_address:
            server_port = self.port_input.text()  # Get port from the input box
            if server_port.isdigit():  # Check if the port is a valid integer
                server_info = f"{server_address}:{server_port}"
                if server_info not in self.servers:
                    self.servers.append(server_info)
                    self.selected_server.addItem(server_info)
                    QtWidgets.QMessageBox.information(self, "Server Added", f"Server {server_info} added successfully.")
                else:
                    QtWidgets.QMessageBox.warning(self, "Warning", "This server is already added.")
            else:
                QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a valid port number.")

    def connect(self):
        server = self.selected_server.currentText()
        if not server:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a valid server to connect.")
            return

        address, port = server.split(":")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((address, int(port)))
            self.chat_log.append(f"Connected to {server}.")
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Connection Failed", str(e))

    def send_message(self):
        message = self.message_input.text()
        if message and self.sock:
            self.chat_log.append(f"{self.username}: {message}")
            self.message_input.clear()
            self.sock.sendall(f"{self.username}: {message}\n".encode())

    def receive_messages(self):
        while True:
            try:
                message = self.sock.recv(1024).decode()
                if message:
                    self.chat_log.append(f"Server: {message}")
                else:
                    break
            except Exception as e:
                self.chat_log.append(f"Error receiving message: {e}")
                break

    def save_chat(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Chat Log", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'w') as f:
                chat_content = self.chat_log.toPlainText()
                f.write(chat_content)
            QtWidgets.QMessageBox.information(self, "Chat Saved", "Chat log saved successfully.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    client = IRCClient()
    client.show()
    sys.exit(app.exec_())
