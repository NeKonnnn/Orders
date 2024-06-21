import os

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
from barcode import EAN13
from barcode.writer import ImageWriter

import constants
from generators.baseGenerator import BaseGenerator
from helpers.warningAndErrorBoxes import generate_message_box


class BarcodeGenerator(BaseGenerator):
    def generate_barcode_for_selected_row(self) -> None:
        """
        Generates a barcode for the currently selected row in the table.
        :return:  None
        """
        current_row = self.app.table_widget.currentRow()
        if current_row == -1:
            generate_message_box(self.app, self.app.translator, 'no_row_selected', box_type='warning')
            return

        # Get the data for the entire row
        row_data = {}
        for column in range(self.app.table_widget.columnCount()):
            item = self.app.table_widget.item(current_row, column)
            if item is not None:  # Check if the cell is not empty
                header = self.app.table_widget.horizontalHeaderItem(column).text()
                row_data[header] = item.text()

        # Find the first column that contains "Код" or "id"
        for column, value in row_data.items():
            if "Код" in column or "id" in column:
                product_code = str(value)
                break
        else:
            generate_message_box(self.app, self.app.translator, 'no_suitable_column', box_type='warning')
            return

        # Pad the product code with zeros if necessary to make it the right length for EAN-13
        # (12 digits excluding the check digit)
        ean_base = product_code.zfill(12)

        # Calculate the check digit and generate the complete EAN-13 number
        check_digit = self.calculate_check_digit(ean_base)
        barcode_number = f"{ean_base}{check_digit}"

        # Generate the barcode image
        barcode_image = self.generate_barcode_image(barcode_number)

        # Save the barcode image to the path specified in constants.PATH_TO_REPORTS
        file_path = self.save_barcode_image(barcode_image, barcode_number)

        # Display the barcode image in a new window
        self.display_barcode_image_with_data(file_path, row_data)

    def calculate_check_digit(self, ean: str) -> int:
        """
        Calculate the EAN-13 check digit for a 12-digit EAN code.
        """
        ean = list(map(int, ean))  # Convert to a list of integers
        sum_odd = sum(ean[::2])  # Sum of digits at odd indices
        sum_even = sum(ean[1::2])  # Sum of digits at even indices
        total = (sum_odd * 3) + sum_even
        check_digit = (10 - (total % 10)) % 10
        return check_digit

    def generate_barcode_image(self, barcode_number: str) -> EAN13:
        # Generate the barcode using the EAN-13 number
        ean = EAN13(barcode_number, writer=ImageWriter())
        # Return the barcode object for further processing
        return ean

    def display_barcode_image_with_data(self, file_path: str, row_data: dict) -> None:
        # Create a dialog to display the barcode image and data
        dialog = QDialog()
        layout = QVBoxLayout()

        # Barcode Image
        label = QLabel()
        pixmap = QPixmap(file_path)
        label.setPixmap(pixmap)
        layout.addWidget(label)

        # Data from the current row
        for key, value in row_data.items():
            data_label = QLabel(f"{key}: {value}")
            layout.addWidget(data_label)

        dialog.setLayout(layout)
        dialog.setWindowTitle("Barcode with Data")
        dialog.exec_()

    def save_barcode_image(self, barcode_image, encoding: str) -> str:
        # Define the path where the barcode image will be saved
        output_file_folder = constants.PATH_TO_REPORTS
        os.makedirs(output_file_folder, exist_ok=True)  # Create the folder if it doesn't exist
        output_file = os.path.join(output_file_folder, f"{encoding}_barcode")

        # Save the barcode image to the file
        barcode_image.save(output_file)
        # Return the path of the saved file for any further processing or information
        return output_file
