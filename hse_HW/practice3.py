import re
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional


def count_words(text: str) -> Dict[str, int]:
    word_dict = {}
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    for word in words:
        word = word.lower()
        if word in word_dict:
            word_dict[word] += 1
        else:
            word_dict[word] = 1
    return word_dict


def exp_list(numbers: List[int], exp: int) -> List[int]:
    return [num**exp for num in numbers]


def get_cashback(operations: List[Dict[str, Any]], special_category: List[str]) -> float:
    cashback = 0.0
    for operation in operations:
        if operation['category'] in special_category:
            cashback += operation['amount'] * 0.05
        else:
            cashback += operation['amount'] * 0.01
    return cashback


def get_path_to_file() -> Optional[Path]:
    if Path().resolve().name == 'tests':
        base_path = Path().resolve().parent
    else:
        base_path = Path().resolve()
    return base_path / 'tasks' / 'practice3' / 'tasks.csv'


def csv_reader(header: str) -> int:
    with open(get_path_to_file(), 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        unique_elements = set()
        for row in csvreader:
            unique_elements.add(row[header])
    return len(unique_elements)