import pandas as pd
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QFileDialog

from helpers.warningAndErrorBoxes import generate_message_box
from plugins.plugin import Plugin


class ImportsPlugin(Plugin):
    def __init__(self, app):
        super().__init__(app)
        self.app = app

    def get_menu_items(self) -> list[QAction]:
        actions = []

        for name, method in [('import_csv', self.import_csv),
                             ('import_json', self.import_json),
                             ('import_excel', self.import_excel),
                             ('import_txt', self.import_txt)]:
            action_text = self.app.translator.get_translation(name)
            # adds [<filetype>] to the action text
            if '[' in action_text and ']' in action_text:
                left_text, right_text = action_text.split('[', 1)
                action_text = f"{left_text}\t[{right_text}"

            action = QAction(QIcon(':/images/down_arrow.jpg'), action_text, self.app)
            action.triggered.connect(lambda *args, m=method: m(*args))
            actions.append(action)

        return actions

    def import_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self.app, "Open CSV File", "", "CSV files (*.csv)")
        if file_name:
            self.import_file(file_name, 'csv')

    def import_json(self):
        file_name, _ = QFileDialog.getOpenFileName(self.app, "Open JSON File", "", "JSON files (*.json)")
        if file_name:
            self.import_file(file_name, 'json')

    def import_excel(self):
        file_name, _ = QFileDialog.getOpenFileName(self.app, "Open Excel File", "", "Excel files (*.xlsx *.xls)")
        if file_name:
            self.import_file(file_name, 'excel')

    def import_txt(self):  # Новый метод для импорта текстовых файлов
        file_name, _ = QFileDialog.getOpenFileName(self.app, "Open Text File", "", "Text files (*.txt)")
        if file_name:
            self.import_file(file_name, 'txt')

    def import_file(self, file_name: str, file_type: str):
        try:
            if file_type == 'csv':
                df = pd.read_csv(file_name)
            elif file_type == 'json':
                df = pd.read_json(file_name)
            elif file_type == 'excel':
                df = pd.read_excel(file_name)
            elif file_type == 'txt':  # Обработка текстовых файлов
                df = pd.read_csv(file_name, delimiter='\t')  # Предполагаем разделение табуляцией
            else:
                raise ValueError("Unsupported file type")

            self.insert_data_into_table(df)
        except Exception as e:
            generate_message_box(self.app, self.app.translator, text=str(e), box_type='error')



    def insert_data_into_table(self, df: pd.DataFrame):
        table_name = self.app.table_widget.property("current_table")
        try:
            if table_name:
                columns = self.app.db_handler.fetch_table_columns(table_name)
                for _, row in df.iterrows():
                    if set(row.index) == set(columns):
                        self.app.db_handler.insert_into_table(table_name, columns, row.tolist())
                    else:
                        raise ValueError("Data columns do not match table columns")

                self.app.show_table_crud(table_name)
            else:
                generate_message_box(self.app, self.app.translator, text="No table is currently selected",
                                     box_type='error')
        except Exception as e:
            generate_message_box(self.app, self.app.translator, text=str(e), box_type='error')
