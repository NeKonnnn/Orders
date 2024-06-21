import os
import sys
from functools import partial
from typing import Dict

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMenuBar,
                               QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
                               QFormLayout, QMessageBox, QHeaderView)

import constants
from databaseHandler import DatabaseHandler
from helpers.warningAndErrorBoxes import generate_message_box
from plugins.importPlugin import ImportsPlugin
from plugins.languagePlugin import LanguagePlugin
from plugins.pluginManager import PluginManager
from plugins.reportPlugin import ReportPlugin
from translator import Translator
from users.user import User
from windows.loginWindow import LoginWindow
from windows.supplementaryWindow import SupplementaryWindow


class TableCRUDApp(QMainWindow):
    def __init__(self, db_hndl: DatabaseHandler, tl: Translator, title="CRUD App for Multiple Tables",
                 last_opened_table=None):
        super().__init__()

        # Basic setup
        self.menubar = None
        self.setWindowTitle(title)
        self.user_resized = False
        self.last_size = self.size()
        self.resizeEvent = self.custom_resize_event

        # Database and translator setup
        self.db_handler = db_hndl
        self.user = db_hndl.user
        self.translator = tl

        # Table widget setup
        self.table_widget = QTableWidget()
        self.setCentralWidget(self.table_widget)

        # Plugin setup
        self.plugin_classes = {
            'reports': ReportPlugin,
            'imports': ImportsPlugin,
        }
        # Add language plugin if more than one language is available
        if len(constants.AVAILABLE_LANGUAGES) > 1:
            self.plugin_classes['languages'] = LanguagePlugin
        self.plugin_manager = PluginManager(self, tl)
        self.plugins = {}

        # Supplementary window for showing extra data
        self.supplementary_window = None

        # Menu and table setup
        self.create_menu()
        # fetch all tables() returns: ['translations', 'users', 'user_roles', ...]
        self.last_opened_table = last_opened_table or db_hndl.fetch_all_tables()[3]
        self.show_table_crud(self.last_opened_table)

    def custom_resize_event(self, event) -> None:
        if event.spontaneous():
            self.last_size = self.size()
            QMainWindow.resizeEvent(self, event)

    def create_menu(self) -> None:
        """
        Creates the menu.
        :return:  None
        """
        self.menubar = QMenuBar()
        self.setMenuBar(self.menubar)

        # Tables Menu
        tables_menu = self.menubar.addMenu(self.translator.get_translation('tables'))
        all_tables = self.db_handler.fetch_all_tables()
        user_role = self.db_handler.get_user_role(self.user.user_id)
        tables = [table for table in all_tables if constants.allowed_to_see(user_role, table)]

        for table_name in tables:
            action = QAction(table_name, self)
            action.triggered.connect(lambda checked=False, tn=table_name: self.show_table_crud(tn))
            tables_menu.addAction(action)

        # Plugins
        self.plugin_manager.load_plugins()

        # About Menu
        self.add_menu_item_with_text_only('about', self.show_supplementary_window)

        # Help Menu
        self.add_menu_item_with_text_only('help', self.show_supplementary_window)

    def add_menu_item_with_text_only(self, menu_key: str, slot_function) -> None:
        action = QAction(self.translator.get_translation(menu_key), self)
        action.triggered.connect(lambda: slot_function(menu_key))
        self.menubar.addAction(action)

    def show_supplementary_window(self, window_type):
        if hasattr(self, 'supplementary_window') and self.supplementary_window:
            # Close the existing window to avoid multiple instances
            self.supplementary_window.close()

        self.supplementary_window = SupplementaryWindow(translator=self.translator,
                                                        title=f'{window_type}',
                                                        text=f'{window_type}_text')
        self.supplementary_window.show()

    def setup_crud_buttons(self, table_name: str) -> QHBoxLayout:
        """
        Sets up the buttons for CRUD operations.
        :param table_name:  The name of the table to perform the operations on.
        :return:  A QHBoxLayout with the buttons.
        """
        btn_layout = QHBoxLayout()

        # Determine the available actions based on the permissions
        user_permissions = self.db_handler.get_user_permissions(user_id=self.user.user_id,
                                                                required_permissions=constants.AVAILABLE_BUTTONS)
        accessible_buttons = [action for action in constants.AVAILABLE_BUTTONS if user_permissions.get(action, False)]

        for action in constants.AVAILABLE_BUTTONS:
            btn = QPushButton(self.translator.get_translation(action))
            btn.setEnabled(action in accessible_buttons)
            btn.clicked.connect(partial(getattr(self, f'{action}'), table_name))
            btn_layout.addWidget(btn)

        return btn_layout

    def setup_info_search_layout(self, table_name: str, num_rows: int, num_cols: int) -> QHBoxLayout:
        """
        Sets up the layout with the table info and the search button.
        :param table_name:  The name of the table.
        :param num_rows:  The number of rows in the table.
        :param num_cols:  The number of columns in the table.
        :return:  A QHBoxLayout with the table info and the search button.
        """
        info_search_layout = QHBoxLayout()
        table_info_label = QLabel(f"{self.translator.get_translation('selected_table')}: {table_name}\n"
                                  f"{self.translator.get_translation('rows')}: {num_rows}\n"
                                  f"{self.translator.get_translation('columns')}: {num_cols}")

        search_permission = self.db_handler.get_user_permissions(self.user.user_id, ['search_record'])
        search_btn = QPushButton(self.translator.get_translation('search_record'))
        search_btn.setEnabled(search_permission['search_record'])  # anythin != 0 will be True
        search_btn.clicked.connect(partial(self.show_search_dialog, table_name))
        search_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        info_search_layout.addWidget(table_info_label)
        info_search_layout.addWidget(search_btn)
        return info_search_layout

    def update_table(self, records: list, columns: list) -> None:
        """
        Updates the table with the given records and columns.
        :param records:  The records to display in the table.
        :param columns:  The columns to display in the table.
        :return:
        """
        self.table_widget.setRowCount(len(records))
        self.table_widget.setColumnCount(len(columns))
        self.table_widget.setHorizontalHeaderLabels(columns)
        self.table_widget.setSortingEnabled(True)
        for row, record in enumerate(records):
            for col, value in enumerate(record):
                self.table_widget.setItem(row, col, QTableWidgetItem(str(value)))

    def show_table_crud(self, table_name: str) -> None:
        """
        Shows the table with CRUD operations.
        :param table_name:  The name of the table to show.
        :return:  None
        """
        self.last_opened_table = table_name
        if table_name:
            records, columns = self.db_handler.fetch_table_data(table_name), self.db_handler.fetch_table_columns(
                table_name)
            self.update_table(records=records, columns=columns)
            self.table_widget.setProperty("current_table", table_name)

            btn_layout = self.setup_crud_buttons(table_name)
            info_search_layout = self.setup_info_search_layout(table_name, len(records), len(columns))

            main_layout = QVBoxLayout()
            main_layout.addLayout(info_search_layout)
            main_layout.addWidget(self.table_widget)
            main_layout.addLayout(btn_layout)

            widget = QWidget()
            widget.setLayout(main_layout)
            self.setCentralWidget(widget)
            self.resize_window()
        else:
            QMessageBox.warning(self, self.translator.get_translation('warning'),
                                self.translator.get_translation('no_table_available'))

    def resize_window(self) -> None:
        """
        Resizes the window to fit the table.
        :return:
        """
        self.resize(self.last_size or (
            self.table_widget.horizontalHeader().length(), self.table_widget.verticalHeader().length()))

    def show_search_dialog(self, table_name: str) -> None:
        """
        Shows the search dialog.
        :param table_name:  The name of the table to search in.
        :return:  None
        """
        columns = self.db_handler.fetch_table_columns(table_name)
        dialog, form_layout, entries = QDialog(self), QFormLayout(), {col: QLineEdit() for col in columns}
        dialog.setWindowTitle(self.translator.get_translation('search_record'))
        for col, entry in entries.items():
            form_layout.addRow(QLabel(col), entry)
        search_btn = QPushButton(self.translator.get_translation('search_record'))
        search_btn.clicked.connect(lambda: self.execute_search(table_name, entries))
        form_layout.addRow(search_btn)
        dialog.setLayout(form_layout)
        dialog.exec()

    def create_results_table(self, columns: list, search_results: list) -> QTableWidget:
        """
        Creates a table with the given columns and search results.
        :param columns: The columns to display in the table.
        :param search_results: The search results to display in the table.
        :return: A QTableWidget with the given columns and search results.
        """
        results_table = QTableWidget()
        results_table.setRowCount(len(search_results))
        results_table.setColumnCount(len(columns))
        results_table.setHorizontalHeaderLabels(columns)

        # Set the minimum height of the table
        results_table.setMinimumHeight(250)

        # Set dynamic column widths and calculate total width
        header = results_table.horizontalHeader()
        total_width = 0
        for col in range(len(columns)):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
            results_table.resizeColumnToContents(col)
            total_width += header.sectionSize(col)

        # Set minimum width based on total column widths
        min_width = min(total_width + 31, 800)
        results_table.setMinimumWidth(min_width)

        # Populate the table with items
        for row, record in enumerate(search_results):
            for col, value in enumerate(record):
                results_table.setItem(row, col, QTableWidgetItem(str(value)))

        return results_table

    def execute_search(self, table_name: str, entries: dict) -> None:
        """
        Executes the search.
        :return:  None
        """
        search_results = self.db_handler.search_table_data(table_name,
                                                           {col: entry.text() for col, entry in entries.items()})
        results_window = QDialog(self)
        results_window.setWindowTitle(self.translator.get_translation('search_results'))
        layout = QVBoxLayout()
        results_table = self.create_results_table(list(entries.keys()), search_results)
        layout.addWidget(results_table)
        results_window.setLayout(layout)
        results_window.resize(results_table.horizontalHeader().length(), results_table.verticalHeader().length())
        results_window.exec()

    def add_record(self, table_name) -> None:
        columns = self.db_handler.fetch_table_columns(table_name)
        dialog, layout, entries = QDialog(self), QVBoxLayout(), {col: QLineEdit() for col in columns if col != "id"}
        dialog.setWindowTitle(self.translator.get_translation('add_record'))
        for col, entry in entries.items():
            layout.addWidget(QLabel(col))
            layout.addWidget(entry)
        add_btn = QPushButton(self.translator.get_translation('add'))
        add_btn.clicked.connect(lambda: self.save_new_record(dialog, table_name, entries))
        layout.addWidget(add_btn)
        dialog.setLayout(layout)
        dialog.exec()

    def save_new_record(self, dialog: QDialog, table_name: str, entries: Dict[str, QLineEdit]) -> None:
        '''
        Saves a new record to the table.
        :param dialog:  The dialog to close.
        :param table_name:      The name of the table.
        :param entries:       The entries to save.
        :return:  None
        '''
        self.db_handler.insert_into_table(table_name, list(entries.keys()),
                                          [entry.text() for entry in entries.values()])
        dialog.accept()
        self.show_table_crud(table_name)

    def edit_record(self, table_name):
        """
        Edits a record in the table.
        :param table_name:  The name of the table.
        :return: None
        """
        current_row = self.table_widget.currentRow()
        if current_row == -1:
            return QMessageBox.warning(self, self.translator.get_translation('warning'),
                                       self.translator.get_translation('warning_select_text'))
        try:
            columns = self.db_handler.fetch_table_columns(table_name)
        except Exception as e:
            return QMessageBox.critical(self, "Error", str(e))

        dialog, form_layout, entries = QDialog(self), QFormLayout(), {col: QLineEdit(
            self.table_widget.item(current_row, index).text() if self.table_widget.item(current_row, index) else "") for
            index, col in enumerate(columns)}
        dialog.setWindowTitle(self.translator.get_translation('edit_record'))
        for col, entry in entries.items():
            form_layout.addRow(QLabel(col), entry)
        save_btn = QPushButton(self.translator.get_translation('save'))
        save_btn.clicked.connect(lambda: self.save_edited_record(dialog, table_name, current_row, entries))
        form_layout.addRow(save_btn)
        dialog.setLayout(form_layout)
        dialog.exec()

    def save_edited_record(self, dialog: QDialog, table_name: str, row: int, entries: Dict[str, QLineEdit]) -> None:
        self.db_handler.update_table_data(table_name, list(entries.keys()),
                                          [entry.text() for entry in entries.values()],
                                          [self.table_widget.item(row, col).text() for col in
                                           range(self.table_widget.columnCount())])
        dialog.accept()
        self.show_table_crud(table_name)

    def confirm_deletion(self):
        confirm_box = QMessageBox()
        confirm_box.setText("Confirm Deletion")
        confirm_box.setInformativeText("Are you sure you want to delete the selected row(s)?")
        confirm_box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        return confirm_box.exec()

    def delete_record(self, table_name) -> None:
        selected_items = self.table_widget.selectedItems()
        if self.confirm_deletion() == QMessageBox.Cancel:
            return

        if len(selected_items) == 1:
            current_row = self.table_widget.currentRow()
            if current_row == -1:
                return QMessageBox.warning(self, self.translator.get_translation('warning'),
                                           self.translator.get_translation('warning_delete_text'))
            self.db_handler.delete_from_table(
                table_name,
                [self.table_widget.horizontalHeaderItem(col).text() for col in range(self.table_widget.columnCount())],
                [self.table_widget.item(current_row, col).text() for col in range(self.table_widget.columnCount())]
            )

        else:
            self.delete_rows(selected_items, table_name)
        self.show_table_crud(table_name)

    def delete_rows(self, selected_items: list[QTableWidgetItem], table_name=None) -> None:
        # Extract unique row indices from the selected items
        row_indices = {item.row() for item in selected_items}

        for row_index in row_indices:
            self.db_handler.delete_from_table(
                table_name,
                [self.table_widget.horizontalHeaderItem(col).text() for col in range(self.table_widget.columnCount())],
                [self.table_widget.item(row_index, col).text() for col in range(self.table_widget.columnCount())]
            )

    @staticmethod
    def create_main_window(tl: Translator, table_name: str = None, user_in_static: User = None, last_size=None):
        new_handler = DatabaseHandler(constants.DB_PATH)
        new_handler.user = user_in_static
        window = TableCRUDApp(db_hndl=new_handler, tl=tl, title=constants.DEFAULT_NAME,
                              last_opened_table=table_name)
        if last_size:
            window.resize(last_size)
        window.show()
        return window


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # icon above left
    icon_path = os.path.abspath(constants.ICON_PATH)
    app.setWindowIcon(QIcon(icon_path))

    translator = Translator()
    try:
        with open(os.path.abspath(constants.GENERAL_STYLE_PATH), "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        generate_message_box(app, translator, text='warning_stylesheet_not_found', box_type='error')

    db_handler = DatabaseHandler(constants.DB_PATH)
    translator = Translator(constants.DEFAULT_LANGUAGE)

    login_window = LoginWindow(db_handler, allow_register=constants.ALLOW_REGISTER, tl=translator)
    if login_window.exec() == QDialog.Accepted:
        user = User(user_id=login_window.user_id,
                    login=db_handler.get_login_by_user_id(login_window.user_id),
                    )
        db_handler.user = user
        main_window = TableCRUDApp(db_hndl=db_handler, tl=translator, title=constants.DEFAULT_NAME)
        main_window.show()
        sys.exit(app.exec())
