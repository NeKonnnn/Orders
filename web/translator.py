import sqlite3
import sys
from typing import Dict

import constants


class Translator:
    def __init__(self, language: str = 'en'):
        self.language = language
        self.translations = self.load_translations()

    def load_translations(self) -> Dict[str, Dict[str, str]]:
        """
        Loads translations from the database.
        :return:  A dictionary of dictionaries, where the first key is the language code,
                  and the second key is the translation key.
        """
        conn = sqlite3.connect('demo.db')
        cursor = conn.cursor()

        translations = {lang: {} for lang in constants.AVAILABLE_LANGUAGES}
        query = 'SELECT translation_key, ' + ', '.join(
            [f'translation_{lang}' for lang in constants.AVAILABLE_LANGUAGES]) + ' FROM translations'

        for row in cursor.execute(query):
            key, *translations_for_languages = row
            for i, lang in enumerate(constants.AVAILABLE_LANGUAGES):
                translations[lang][key] = translations_for_languages[i]

        conn.close()
        return translations

    def get_translation(self, word: str) -> str:
        """
        Returns the translation of a given word in the current language.
        :param word:  The word to translate.
        :return:  The translation of the word in the current language.
        """
        try:
            return self.translations[self.language][word]
        except KeyError:
            sys.stderr.write("Word not found in dictionary: " + word + "\n")
            return "#" + word + "#"

    def available_languages(self) -> list[str]:
        return list(self.translations.keys())

    def get_language_names(self, language_code: str) -> str:
        """
        Returns the full language name for a given language code.
        :param language_code:  The language code.
        :return:  The full language name.
        """
        try:
            return self.translations[language_code]['full_lang_name']
        except KeyError:
            sys.stderr.write("Language name not found for code: " + language_code + "\n")
            return language_code

