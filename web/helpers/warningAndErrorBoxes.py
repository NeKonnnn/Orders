from PySide6.QtWidgets import QMessageBox

from translator import Translator


def generate_message_box(self, translator: Translator, text: str, box_type: str) -> None:
    """
    Generates a message box with a given text and type.
    :param self:  The parent widget.
    :param translator:  The translator object.
    :param text:  The text to show in the message box.
    :param box_type:  The type of the message box. Can be 'warning', 'error', or 'success'.
    :return:  None.
    """
    msg = QMessageBox(self)

    box_types = {
        'warning': (QMessageBox.Icon.Warning, 'warning'),
        'error': (QMessageBox.Icon.Critical, 'error'),
        'success': (QMessageBox.Icon.Information, 'success'),
    }

    if box_type not in box_types:
        raise ValueError("Invalid box_type. Expected 'warning', 'error', or 'success'.")

    icon, title_key = box_types[box_type]
    msg.setIcon(icon)
    msg.setWindowTitle(translator.get_translation(title_key))
    msg.setText(translator.get_translation(text))
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec()
