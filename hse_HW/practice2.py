import random
import re
from typing import Iterable

UNCULTURED_WORDS = ('kotleta', 'pirog')

def greet_user(name: str) -> str:
    greeting = "Hello, {}! Welcome to our service!".format(name)
    return greeting

def get_amount() -> float:
    amount = round(random.uniform(100, 1000000), 2)
    return amount

def is_phone_correct(phone_number: str) -> bool:
    pattern = r'\+7\d{10}'
    return re.fullmatch(pattern, phone_number) is not None

def is_amount_correct(current_amount: float, transfer_amount: str) -> bool:
    transfer_amount = float(transfer_amount)
    return current_amount >= transfer_amount

def moderate_text(text: str, uncultured_words: Iterable[str]) -> str:
    text = text.lower().strip().capitalize()
    text = text.replace("\"", "").replace("\'", "")
    for word in uncultured_words:
        text = text.replace(word, '#' * len(word))
    return text

def create_request_for_loan(user_info: str) -> str:
    user_info_list = user_info.split(',')
    result = "Фамилия: {}\nИмя: {}\nОтчество: {}\nДата рождения: {}\nЗапрошенная сумма: {}".format(*user_info_list)
    return result