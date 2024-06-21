import pandas as pd
from generators.baseGenerator import BaseGenerator


class ExcelGenerator(BaseGenerator):
    def export_table_to_excel(self):
        self.show_selection_dialog('export', 'export', self.table_selected_for_export)

    def table_selected_for_export(self, dialog, combobox):
        table_name = combobox.currentText()
        dialog.accept()
        df = self.fetch_and_process_table_data(table_name)
        self.export_to_excel(df, f"{table_name}_export.xlsx")

    def export_db_to_excel(self, merged_df: pd.DataFrame):
        self.export_to_excel(merged_df, "database_export.xlsx")
