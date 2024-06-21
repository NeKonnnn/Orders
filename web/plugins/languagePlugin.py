from PySide6.QtGui import QAction

from .plugin import Plugin


class LanguagePlugin(Plugin):
    def __init__(self, app):
        super().__init__(app)
        self.app = app

    def get_menu_items(self) -> list[QAction]:
        actions = []

        for lang in self.app.translator.available_languages():
            language_name = self.app.translator.get_language_names(lang)
            action = QAction(language_name, self.app)

            # https://stackoverflow.com/questions/19837486/lambda-in-a-loop
            action.triggered.connect((lambda lg: lambda: self.switch_language(lg))(lang))
            actions.append(action)

        return actions

    def switch_language(self, lang: str) -> None:
        self.app.close()
        self.app.translator.language = lang
        self.app.create_main_window(tl=self.app.translator,
                                    table_name=self.app.last_opened_table,
                                    user_in_static=self.app.user,
                                    last_size=self.app.last_size, )
