import sys

from PySide6.QtWidgets import QApplication, QTextEdit

import constants


class DummyFile:
    """
    A dummy file-like object that redirects writes to a QTextEdit widget.

    Attributes:
        widget (QTextEdit): The QTextEdit widget to which text is redirected.
    """

    def __init__(self, widget):
        """
        Initialize the DummyFile object with a QTextEdit widget.

        Args:
            widget (QTextEdit): The QTextEdit widget to which text will be redirected.
        """
        self.widget = widget

    def write(self, text):
        """
        Write the given text to the QTextEdit widget.

        Args:
            text (str): The text to write to the widget.
        """
        # Insert the text at the current cursor position in the widget
        self.widget.insertPlainText(text)

        # Ensure the latest text is visible in the widget
        self.widget.ensureCursorVisible()

        # Process all pending events to update the widget immediately
        QApplication.processEvents()

    def flush(self):
        """Flush the stream buffer."""
        # In this case, flush does nothing since we don't need to clear any buffer for the widget.
        pass


class ConsoleWidget(QTextEdit):
    """
    A custom QTextEdit widget that closes when any key is pressed.
    """

    def keyPressEvent(self, event):
        """
        Handle key press events by closing the widget.

        Args:
            event: The event that triggered the key press.
        """
        # Close the widget when a key is pressed
        self.close()


def execute_with_redirected_output(func, *args, **kwargs):
    """
    Execute a function with its output redirected to a QTextEdit widget.

    Args:
        func (callable): The function to execute.
        *args: Variable length argument list to pass to the function.
        **kwargs: Arbitrary keyword arguments to pass to the function.

    Returns:
        The result of the function execution.
    """
    # Create a console-like widget to display output
    console_widget = ConsoleWidget()
    console_widget.setWindowTitle("Report Generation Output")
    # Set the size of the console widget
    console_widget.resize(800, 400)

    # Read the stylesheet from a .qss file and apply it to the console widget
    with open(constants.get_absolute_path(__file__, constants.CONSOLE_STYLE_PATH), "r") as f:
        console_widget.setStyleSheet(f.read())

    # Show the console widget on the screen
    console_widget.show()

    # Create a dummy file object that writes to the console widget
    dummy_file = DummyFile(console_widget)

    # Save the current state of stdout and stderr
    old_stdout, old_stderr = sys.stdout, sys.stderr
    # Redirect stdout and stderr to the dummy file
    sys.stdout, sys.stderr = dummy_file, dummy_file

    try:
        # Execute the function with the redirected output
        result = func(*args, **kwargs)
        # Inform the user that the operation is complete
        console_widget.append("\nOperation complete. Press any key to close.")
        return result
    finally:
        # Restore the original stdout and stderr
        sys.stdout, sys.stderr = old_stdout, old_stderr
