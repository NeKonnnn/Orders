import pandas as pd
import ydata_profiling

import constants
from constants import PATH_TO_REPORTS
from generators.baseGenerator import BaseGenerator
from helpers.warningAndErrorBoxes import generate_message_box
from plugins.third_party_output import execute_with_redirected_output


class HTMLGenerator(BaseGenerator):
    def generate_table_report(self):
        self.show_selection_dialog('create_report', 'create_report', self.table_selected_for_report)

    def table_selected_for_report(self, dialog, combobox):
        table_name = combobox.currentText()
        dialog.accept()
        df = self.fetch_and_process_table_data(table_name)
        self.create_report_for_table(df, table_name)

    def create_report_for_table(self, df: pd.DataFrame, table_name: str) -> None:
        report = ydata_profiling.ProfileReport(df)
        report_file = PATH_TO_REPORTS + f"{table_name}_report.html"
        execute_with_redirected_output(report.to_file, report_file)

    def generate_db_report(self, merged_df: pd.DataFrame):
        if merged_df is not None:
            report = ydata_profiling.ProfileReport(merged_df)
            report_file = constants.PATH_TO_REPORTS + "database_report.html"
            execute_with_redirected_output(report.to_file, report_file)
        else:
            # Handle case where there's no relationship to merge on
            generate_message_box(self.app,
                                 translator=self.app.translator,
                                 text='no_table_connections',
                                 box_type='warning')
