import pandas as pd
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog
from constants import PATH_TO_REPORTS


class BaseGenerator:
    def __init__(self, app):
        self.app = app

    def show_selection_dialog(self, title_key, btn_key, callback) -> None:
        """
        Shows a dialog with a combobox to select a table.
        :param title_key:  The key of the title in the translations table.
        :param btn_key:  The key of the button in the translations table.
        :param callback:  The callback function to call when the button is clicked.
        :return:  None
        """
        dialog = QDialog()
        dialog.setWindowTitle(self.app.translator.get_translation(title_key))
        layout = QVBoxLayout()
        label = QLabel(self.app.translator.get_translation('table'))
        combobox = QComboBox()
        tables = self.app.db_handler.fetch_all_tables(depending_on_user=True)
        combobox.addItems(tables)
        btn = QPushButton(self.app.translator.get_translation(btn_key))
        btn.clicked.connect(lambda: callback(dialog, combobox))
        for widget in [label, combobox, btn]:
            layout.addWidget(widget)
        dialog.setLayout(layout)
        dialog.exec_()

    def fetch_and_process_table_data(self, table_name):
        records = self.app.db_handler.fetch_table_data(table_name)
        columns = self.app.db_handler.fetch_table_columns(table_name)
        return pd.DataFrame(records, columns=columns)

    def export_to_excel(self, df, default_name):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self.app,
                                                   "Save File",
                                                   PATH_TO_REPORTS + default_name,
                                                   "Excel Files (*.xlsx)",
                                                   options=options)
        if file_name:
            if not file_name.endswith('.xlsx'):
                file_name += '.xlsx'
            df.to_excel(file_name, index=False)
