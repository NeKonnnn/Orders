from PySide6.QtWidgets import QVBoxLayout, QDialog, QLineEdit, QLabel, QPushButton
from translator import Translator
from helpers.warningAndErrorBoxes import generate_message_box

"""
This is the login window. It is used to log in to the application.
It is also used to register a new user, if the allow_register argument is True.
"""
class LoginWindow(QDialog):
    def __init__(self, db_handler, tl: Translator, allow_register=True):
        super().__init__()

        self.db_handler = db_handler
        self.translator = tl
        self.user_id = None

        self.setWindowTitle(self.translator.get_translation('login'))
        layout = QVBoxLayout()

        self.login_entry = QLineEdit()
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)

        layout.addWidget(QLabel(self.translator.get_translation('login')))
        layout.addWidget(self.login_entry)
        layout.addWidget(QLabel(self.translator.get_translation('password')))
        layout.addWidget(self.password_entry)

        self.login_btn = QPushButton(self.translator.get_translation('login_button'))
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)

        self.register_btn = QPushButton(self.translator.get_translation('register_button'))
        self.register_btn.clicked.connect(self.handle_register)
        self.register_btn.setEnabled(allow_register)  # Disable or enable based on the argument
        layout.addWidget(self.register_btn)

        self.setLayout(layout)

    def handle_login(self) -> None:
        """
        Handles the login button click.
        :return:  None
        """
        login = self.login_entry.text()
        password = self.password_entry.text()

        # user = tuple (username, password, is_admin, role, can_view, can_edit, can_delete)
        user = self.db_handler.login(login, password)
        if user:
            self.user_id = user[0]
            self.accept()
        else:
            generate_message_box(self, self.translator, 'Invalid login or password', 'error')

    def handle_register(self) -> None:
        """
        Handles the register button click.
        :return:  None
        """
        login = self.login_entry.text()
        password = self.password_entry.text()

        if self.db_handler.register(login, password):
            generate_message_box(self, self.translator, 'register_success', 'success')
        else:
            generate_message_box(self, self.translator, 'login_exists', 'error')
