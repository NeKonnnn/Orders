from PySide6.QtGui import QAction


class Plugin:
    def __init__(self, app):
        self.app = app

    def get_menu_items(self) -> list[QAction]:
        """Return a list of QActions for the menu."""
        return []

    def initialize(self):
        """Any initialization the plugin needs."""
        pass
