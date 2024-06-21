from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QTextBrowser, QVBoxLayout, QWidget
import markdown2

from translator import Translator


class SupplementaryWindow(QWidget):
    """
    SupplementaryWindow is a custom QWidget that displays markdown text
    in a rich text format. It uses QTextBrowser for rendering the markdown text
    that has been converted to HTML, and it's meant to show translated text using
    a provided 'Translator' instance.

    Attributes:
        translator (Translator): An instance of Translator class to handle text translations.
        title (str): The initial title text that will be translated and set as window title.
        text (str): The markdown text to be displayed after translation.
        layout (QVBoxLayout): The layout manager to arrange widgets vertically in the window.
        text_browser (QTextBrowser): A rich text browser to display HTML content.
    """

    def __init__(self, translator: Translator, title: str, text: str):
        """
        Initialize the SupplementaryWindow instance.

        Parameters:
            translator (Translator): The translator instance used to translate the title and text.
            title (str): The original title of the window, before translation.
            text (str): The original markdown text to be displayed, before translation.
        """
        super().__init__()

        # Instance of Translator class to handle the translations
        self.translator = translator
        # Title of the window
        self.title = title
        # Text to be displayed in markdown format
        self.text = text

        # Setup the main layout for the window
        self.layout = QVBoxLayout(self)

        # Initialize QTextBrowser to display the markdown text as HTML
        self.text_browser = QTextBrowser(self)
        # Connect the signal for when an anchor is clicked in the QTextBrowser
        self.text_browser.anchorClicked.connect(self.on_anchor_clicked)
        # Add the QTextBrowser to the vertical layout
        self.layout.addWidget(self.text_browser)

        # Show the initial data on the window
        self.show_data()

    def show_data(self) -> None:
        """
        Translates the title and text using the translator instance, converts the
        markdown text to HTML, sets the window title, and displays the HTML in the QTextBrowser.
        """
        # Translate the title and text using the provided translator instance
        help_text = self.translator.get_translation(self.text)
        window_title = self.translator.get_translation(self.title)

        # Convert the markdown text to HTML, with header IDs for anchor navigation
        help_text_html = markdown2.markdown(help_text, extras=['header-ids'])

        # Set the HTML content to the QTextBrowser
        self.text_browser.setHtml(f"{help_text_html}")
        # Set the window title to the translated title
        self.setWindowTitle(window_title)
        # Set a fixed width for the text browser
        self.text_browser.setFixedWidth(800)
        # Set a minimum height for the text browser
        self.text_browser.setMinimumHeight(400)
        # Allow QTextBrowser to open external links
        self.text_browser.setOpenExternalLinks(True)

    def on_anchor_clicked(self, url: QUrl) -> None:
        """
        Slot connected to the anchorClicked signal of the QTextBrowser.
        It scrolls the view to the clicked anchor.

        Parameters:
            url (QUrl): The QUrl of the clicked anchor containing the fragment identifier.
        """
        # Extract the fragment (anchor identifier) from the QUrl
        anchor = url.fragment()
        # If an anchor was clicked, scroll to the corresponding anchor in the text browser
        if anchor:
            self.text_browser.scrollToAnchor(anchor)
