import sys
from collections import defaultdict, deque

import constants
from generators.barcodeGenerator import BarcodeGenerator
from generators.excelGenerator import ExcelGenerator
from generators.htmlGenerator import HTMLGenerator
from generators.pdfGenerator import PDFGenerator
from plugins.plugin import Plugin

import pandas as pd
from PySide6.QtGui import QAction


class ReportPlugin(Plugin):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.pdf_generator = PDFGenerator(app)
        self.html_generator = HTMLGenerator(app)
        self.excel_generator = ExcelGenerator(app)
        self.barcode_generator = BarcodeGenerator(app)

    def get_menu_items(self) -> list[QAction]:
        actions = []

        for name, method in [('table_report', self.generate_table_report),
                             ('db_report', self.generate_db_report),
                             ('export_table_to_excel', self.export_table_to_excel),
                             ('export_db_to_excel', self.export_db_to_excel),
                             ('generate_pdf', self.generate_pdf_for_selected_row),
                             ('generate_barcode', self.generate_barcode_for_selected_row)]:
            action_text = self.app.translator.get_translation(name)
            # adds [<filetype>] to the action text
            if '[' in action_text and ']' in action_text:
                left_text, right_text = action_text.split('[', 1)
                action_text = f"{left_text}\t[{right_text}"

            action = QAction(action_text, self.app)
            action.triggered.connect(lambda *args, m=method: m(*args))
            actions.append(action)

        return actions

    def generate_pdf_for_selected_row(self):
        merged_df = self.merge_tables()
        self.pdf_generator.generate_pdf_for_selected_row(merged_df)

    def export_table_to_excel(self):
        self.excel_generator.export_table_to_excel()

    def export_data_for_table(self, table_name: str):
        records = self.app.db_handler.fetch_table_data(table_name)
        columns = self.app.db_handler.fetch_table_columns(table_name)
        df = pd.DataFrame(records, columns=columns)
        self.excel_generator.export_to_excel(df, f"{table_name}_export.xlsx")

    def export_db_to_excel(self):
        merged_df = self.merge_tables()
        self.excel_generator.export_db_to_excel(merged_df)

    def generate_table_report(self):
        self.html_generator.generate_table_report()

    def merge_tables(self):
        # Fetch table names
        table_names = self.app.db_handler.fetch_all_tables(depending_on_user=True)

        # Fetch all tables into dataframes
        dfs = {
            table_name: pd.DataFrame(
                self.app.db_handler.fetch_table_data(table_name),
                columns=[f"{col}.{table_name}" for col in self.app.db_handler.fetch_table_columns(table_name)]
            )
            for table_name in table_names
        }

        # Identify foreign key relationships between tables
        relationships = {}
        for table_name in table_names:
            cursor = self.app.db_handler.conn.execute(f"PRAGMA foreign_key_list({table_name})")
            for row in cursor.fetchall():
                relationships[(table_name, row[3])] = (row[2], row[4])

        relationships = self.sort_relationships_topologically(relationships)

        # Merge dataframes based on relationships
        merged_df = None
        for (child_table, child_col), (parent_table, parent_col) in relationships.items():
            if child_col is None or parent_col is None:
                continue

            if not constants.allowed_to_see(self.app.db_handler.get_user_role(self.app.user.user_id), parent_table):
                continue

            if child_table in dfs and parent_table in dfs:
                if merged_df is None:
                    merged_df = pd.merge(dfs[child_table], dfs[parent_table],
                                         left_on=child_col + "." + child_table,
                                         right_on=parent_col + "." + parent_table,
                                         how='outer')
                else:
                    try:
                        merged_df = pd.merge(merged_df, dfs[parent_table],
                                             left_on=child_col + "." + child_table,
                                             right_on=parent_col + "." + parent_table,
                                             how='outer')
                    except KeyError:
                        # TODO fix sorting maybe?
                        print(f"KeyError: {child_col}.{child_table} or {parent_col}.{parent_table} not found in "
                              f"merged_df",
                              file=sys.stderr)
                        return merged_df

        return merged_df

    def topological_sort(self, relationships) -> list:
        """
        Performs topological sort on a graph represented by a dictionary of relationships.
        :param relationships:  A dictionary of relationships, where the key is a child table, and the value is a tuple
        :return:  A list of tables sorted topologically
        """
        # Create a dictionary to keep track of incoming edges for each table
        incoming_edges = defaultdict(set)
        nodes = set()

        # Fill the dictionary with the relationships data
        for (child, _), (parent, _) in relationships.items():
            incoming_edges[child].add(parent)
            nodes.add(child)
            nodes.add(parent)

        # Set of all nodes that have no incoming edges (independent nodes)
        no_incoming = nodes - set(incoming_edges)

        # Queue to maintain the nodes as we process them
        queue = deque(no_incoming)
        sorted_nodes = []

        while queue:
            node = queue.popleft()
            sorted_nodes.append(node)

            # Nodes that depend on the current node
            to_remove = []
            for child, parents in incoming_edges.items():
                if node in parents:
                    parents.remove(node)
                    if not parents:
                        queue.append(child)
                        to_remove.append(child)

            for child in to_remove:
                incoming_edges.pop(child)

        # If there are still nodes in incoming_edges, we have a cycle
        if any(incoming_edges.values()):
            raise Exception("A cycle was detected in the graph, and topological sort cannot be performed.")

        return sorted_nodes

    def sort_relationships_topologically(self, relationships) -> dict:
        # Perform topological sort on the tables
        sorted_tables = self.topological_sort(relationships)

        # Rebuild the relationships dictionary based on the sorted tables
        sorted_relationships = {}
        for table in sorted_tables:
            for (child, child_col), (parent, parent_col) in relationships.items():
                if child == table or parent == table:
                    sorted_relationships[(child, child_col)] = (parent, parent_col)

        return sorted_relationships

    def generate_db_report(self):
        merged_df = self.merge_tables()
        self.html_generator.generate_db_report(merged_df)

    def generate_barcode_for_selected_row(self):
        self.barcode_generator.generate_barcode_for_selected_row()
