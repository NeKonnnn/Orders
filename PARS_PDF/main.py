# Библиотеки для GUI
import tkinter as tk
from tkinter import messagebox
import threading

# Общие библиотеки
import pandas as pd
import re
import os
import sys
import cv2
import numpy as np
import time
import datetime

import fitz

# Для работы с почтой
import imaplib
import email
from email.header import decode_header

# Для работы с google sheet
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Для удаления папок
import shutil

# Для проверки на дубликаты
import hashlib

def calculate_file_hash(file_path):
    BUF_SIZE = 65536  # Размер буфера для чтения частями
    sha1 = hashlib.sha1()

    with open(file_path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()

def is_file_processed_before(file_hash, processed_hashes_file='processed_hashes.txt'):
    if os.path.exists(processed_hashes_file):
        with open(processed_hashes_file, 'r') as file:
            processed_hashes = file.read().splitlines()
            if file_hash in processed_hashes:
                return True
    return False

def mark_file_as_processed(file_hash, processed_hashes_file='processed_hashes.txt'):
    with open(processed_hashes_file, 'a') as file:
        file.write(file_hash + '\n')

def run_script():
    try:
        # Функция для декодирования закодированных строк
        def decode_mime_words(s):
            decoded_words = decode_header(s)
            return ''.join(word.decode(encoding or 'utf8') if isinstance(word, bytes) else word for word, encoding in decoded_words)

        username = "alexowlglobe@gmail.com"
        password = "mzst lhhq bymf axla"  # Используйте пароль приложения
        imap_url = "imap.gmail.com"
        attachment_dir = os.path.join(os.getcwd(), "PDF")
        processed_uids_log = os.path.join(os.getcwd(), "processed_uids.txt")

        if not os.path.isdir(attachment_dir):
            os.mkdir(attachment_dir)

        # Чтение списка обработанных UID
        if os.path.exists(processed_uids_log):
            with open(processed_uids_log, 'r') as file:
                processed_uids = set(file.read().splitlines())
        else:
            processed_uids = set()
            
        # Тест: Вывод содержимого processed_uids после чтения
        #print("Прочитанные UID:", processed_uids)
        
        # Инициализируем file_name перед началом обработки файлов
        file_name = ""
        
        mail = imaplib.IMAP4_SSL(imap_url)
        mail.login(username, password)
        mail.select("inbox")

        # Использование UID вместо обычных номеров сообщений
        status, messages = mail.uid('search', None, 'ALL')
        messages = messages[0].split(b' ')

        # Проверка наличия новых писем
        if not messages:
            print("Нет новых писем для обработки.")
            mail.logout()
            return  # Прерывание выполнения функции, если писем нет
        
        # Чтение списка обработанных UID из файла, если он существует
        processed_uids = set()
        if os.path.exists(processed_uids_log):
            with open(processed_uids_log, 'r') as file:
                processed_uids = set(file.read().splitlines())

        # Использование UID вместо обычных номеров сообщений
        status, messages = mail.uid('search', None, 'ALL')
        messages = messages[0].split(b' ')

        # Фильтрация списка сообщений, исключая уже обработанные
        new_messages = [msg for msg in messages if msg.decode() not in processed_uids]

        # Тест: Вывод новых UID перед их обработкой
        #print("Новые UID для обработки:", [msg.decode() for msg in new_messages])

        for mail_uid in new_messages:
            _, msg = mail.uid('fetch', mail_uid, '(RFC822)')
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])
                    # Здесь начинаем обрабатывать части сообщения
                    for part in msg.walk():
                        if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                            continue

                        file_name = part.get_filename()
                        if file_name:
                            decoded_file_name = decode_mime_words(file_name)
                            unique_file_name = f"{mail_uid.decode()}_{decoded_file_name}"  # Добавление UID к имени файла для уникальности
                            file_path = os.path.join(attachment_dir, unique_file_name)
                            if not os.path.exists(file_path):  # Проверка на существование файла
                                with open(file_path, 'wb') as f:
                                    f.write(part.get_payload(decode=True))
                                # Новый блок кода начинается здесь
                                file_hash = calculate_file_hash(file_path)
                                if is_file_processed_before(file_hash):
                                    print(f"Файл {unique_file_name} был ранее обработан. Пропускаем.")
                                    os.remove(file_path)  # Удаляем файл, если он уже обрабатывался
                                    continue  # Пропускаем дальнейшую обработку этого файла
                                else:
                                    mark_file_as_processed(file_hash)  # Отмечаем файл как обработанный

            # Добавляем UID обработанного письма в лог
            processed_uids.add(mail_uid.decode())
            with open(processed_uids_log, 'a') as log_file:
                log_file.write(mail_uid.decode() + '\n')

                # Тест: Вывод UID после его добавления
                #print("Добавлен UID:", mail_uid.decode())

        mail.close()
        mail.logout()

        def convert_pdf_to_txt_with_layout(pdf_folder, txt_folder):
            """
            Конвертирует PDF-файлы из указанной папки в текстовые файлы, сохраняя приблизительное расположение текста.
            Пропускает переименование файлов, если файл с целевым именем уже существует.
            Сохраняет текстовые файлы в указанную папку с соответствующими именами.

            :param pdf_folder: Путь к папке с PDF-файлами.
            :param txt_folder: Путь к папке для сохранения текстовых файлов.
            """
            if not os.path.exists(txt_folder):
                os.makedirs(txt_folder)

            pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]

            for i, file_name in enumerate(sorted(pdf_files), start=1):
                new_file_name = f'{i}.pdf'
                new_file_path = os.path.join(pdf_folder, new_file_name)

                # Проверка на существование файла с целевым именем
                if not os.path.exists(new_file_path):
                    os.rename(os.path.join(pdf_folder, file_name), new_file_path)

                with fitz.open(new_file_path) as doc:
                    full_text = ''
                    for page in doc:
                        blocks = page.get_text("dict")["blocks"]
                        last_block_y0 = None
                        for b in blocks:
                            if 'lines' in b:
                                for line in b["lines"]:
                                    line_text = ''.join([span["text"] for span in line["spans"]])
                                    if last_block_y0 is not None and b["bbox"][1] - last_block_y0 > 15:  # Новый абзац
                                        full_text += '\n'
                                    full_text += line_text + '\n'
                                    last_block_y0 = b["bbox"][3]

                    with open(os.path.join(txt_folder, f'{i}.txt'), 'w') as txt_file:
                        txt_file.write(full_text)

        pdf_folder = 'PDF'
        txt_folder = 'TXT'
        convert_pdf_to_txt_with_layout(pdf_folder, txt_folder)

        # Список для хранения данных о блоках
        blocks_data = []

        # Получаем список всех PDF-файлов в папке
        pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]

        # Анализ координат текстовых блоков в каждом файле
#         if not pdf_files:  # Если список pdf_files пуст
#             print("В папке PDF нет файлов для обработки.")
#         else:
        blocks_data = []
        for file_name in pdf_files:
            file_path = os.path.join(pdf_folder, file_name)
            try:
                with fitz.open(file_path) as doc:
                    for page_number in range(len(doc)):
                        page = doc[page_number]
                        blocks = page.get_text("dict")["blocks"]
                        for block in blocks:
                            if 'lines' in block:
                                block_dict = {
                                    'file_name': file_name,
                                    'page_number': page_number + 1,
                                    'bbox': block['bbox'],
                                    'text': " ".join([line['spans'][0]['text'] for line in block['lines']])
                                }
                                blocks_data.append(block_dict)
            except Exception as e:
                print(f"Ошибка при обработке файла {file_name}: {e}")

        # Если blocks_data не пуст, продолжаем дальнейшую обработку
        if blocks_data:

            # Создаем DataFrame из списка словарей
            df_blocks = pd.DataFrame(blocks_data)

            # Добавляем новый столбец 'file_number', в котором хранится числовая часть имени файла
            df_blocks['file_number'] = df_blocks['file_name'].str.extract('(\d+)').astype(int)

            # Сортируем DataFrame сначала по 'file_number', затем по 'page_number'
            df_blocks_sorted = df_blocks.sort_values(by=['file_number', 'page_number'])

            # Удаляем столбец 'file_number', если он вам больше не нужен
            df_blocks_sorted = df_blocks_sorted.drop('file_number', axis=1)

            # Применяем стиль для переноса текста в столбце 'bbox'
            df_styled = df_blocks_sorted.style.set_properties(subset=['bbox'], **{'width': '300px', 'white-space': 'pre-wrap'})

        # Функция для создания папки, если она не существует
        def ensure_folder_exists(folder_path):
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                #print(f"Создана папка: {folder_path}")  # Для отладки
                
        def save_pdf_by_content(pdf_folder, output_base_folder):
            if not os.path.exists(output_base_folder):
                os.makedirs(output_base_folder)

            pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
            unclassified_files = []

            for file_name in pdf_files:
                file_path = os.path.join(pdf_folder, file_name)
                classified = False

                with fitz.open(file_path) as doc:
                    for page in doc:
                        rules = {
                            "Alfa": [("АО «АЛЬФА-БАНК»", (400.63, 532.01, 471.38, 541.38))],
                            "Modul": [("МОСКОВСКИЙ ФИЛИАЛ АО КБ", (408.04, 595.41, 523.66, 622.18))],
                            "Moskomertz": [("КБ \"Москоммерцбанк\" (АО) г. Москва", (392.37, 599.90, 553.63, 609.87))],
                            "Otkritie": [
                                ("ПАО БАНК \"ФК ОТКРЫТИЕ\"", (405.60, 605.59, 524.32, 645.20)),
                                ("ТОЧКА ПАО БАНКА \"ФК", (441.52, 519.34, 520.49, 527.16))
                            ],
                            "OTP": [("АО \"ОТП Банк\" г. Москва", (104.08, 575.77, 521.17, 595.40))],
                            "Peterburg": [("Ф-Л ПАО \"БАНК \"САНКТ-ПЕТЕРБУРГ\"", (408.92, 640.00, 560.10, 649.32))],
                            "Raifaizen": [("АО \"РАЙФФАЙЗЕНБАНК\" Г МОСКВА", (398.64, 533.16, 537.38, 542.10))],
                            "Rosbank": [("РОСБАНК", (408.75, 470.27, 443.27, 479.06))],
                            "Rosselxoz": [
                                ("РФ АО \"Россельхозбанк\" - \"ЦРМБ\"", (413.97, 585.38, 543.03, 594.33)),
                                ("РФ АО \"Россельхозбанк\" - \"ЦРМБ\"", (403.97, 575.26, 533.03, 584.20))
                            ],
                            "Sber": [
                                ("ПАО Сбербанк", (405.98, 485.51, 458.02, 494.37)),
                                ("ПАО Сбербанк", (418.0, 563.86, 471.89, 574.21)),
                                ("ПАО Сбербанк", (394.98, 510.91, 449.02, 519.77))
                            ],
                            "VTB": [("ФИЛИАЛ \"ЦЕНТРАЛЬНЫЙ\" БАНКА", (417.0, 596.34, 549.35, 634.60))],
                            "GPB": [("Банк ГПБ (АО)", (54.96, 233.37, 447.91, 258.18))],
                            "Tinkoff": [("АО ТИНЬКОФФ БАНК", (418.77, 581.83, 499.22, 590.83))],
                            "SovkombankF": [("Филиал \"Корпоративный\" ПАО \"Совкомбанк\" (МОСКВА)", (34.02, 280.23, 298.07, 290.71))]
                        }

                        for bank, conditions in rules.items():
                            for idx, (text, rect) in enumerate(conditions, start=1):
                                extracted_text = page.get_textbox(rect)
                                if text in extracted_text:
                                    bank_folder = os.path.join(output_base_folder, bank)
                                    sub_folder_path = os.path.join(bank_folder, f"{bank}_{idx}")
                                    ensure_folder_exists(sub_folder_path)  # Убедитесь, что папка существует перед сохранением файла

                                    # Сохраняем файл в соответствующую подпапку
                                    doc.save(os.path.join(sub_folder_path, file_name))
                                    classified = True
                                    break
                            if classified:
                                break
                        if classified:
                            break
                        
                    if not classified:
                        neopredelenie_folder = os.path.join(output_base_folder, 'Neopredelenie')
                        ensure_folder_exists(neopredelenie_folder)
                        doc.save(os.path.join(neopredelenie_folder, file_name))
                        unclassified_files.append(file_name)
# ТУТА РАСКОММЕНТИТЬ ПОТОМ!!!
            # Вывод списка неклассифицированных файлов
#             if unclassified_files:
#                 print("Не удалось классифицировать следующие файлы:")
#                 for file_name in unclassified_files:
#                     print(file_name)

        pdf_folder = 'PDF'
        output_base_folder = 'PDF_razbivka'
        save_pdf_by_content(pdf_folder, output_base_folder)

        class PDFProcessor:
            def __init__(self, pdf_folder, config):
                self.pdf_folder = pdf_folder
                self.config = config  # Словарь с координатами и другими параметрами для конкретной подпапки

            # Функция для преобразования числительных, записанных словами, в числа
            def word_to_number(self, words):
                number_dict = {
                    'ноль': 0, 'один': 1, 'одна': 1, 'два': 2, 'две': 2, 'три': 3, 'четыре': 4,
                    'пять': 5, 'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9,
                    'десять': 10, 'одиннадцать': 11, 'двенадцать': 12,
                    'тринадцать': 13, 'четырнадцать': 14, 'пятнадцать': 15,
                    'шестнадцать': 16, 'семнадцать': 17, 'восемнадцать': 18,
                    'девятнадцать': 19, 'двадцать': 20, 'тридцать': 30,
                    'сорок': 40, 'пятьдесят': 50, 'шестьдесят': 60,
                    'семьдесят': 70, 'восемьдесят': 80, 'девяносто': 90,
                    'сто': 100, 'двести': 200, 'триста': 300, 'четыреста': 400,
                    'пятьсот': 500, 'шестьсот': 600, 'семьсот': 700,
                    'восемьсот': 800, 'девятьсот': 900
                }
                multiplier_dict = {
                    'тысяча': 1000, 'тысячи': 1000, 'тысяч': 1000,
                    'миллион': 1000000, 'миллиона': 1000000, 'миллионов': 1000000,
                    'миллиард': 1000000000, 'миллиарда': 1000000000, 'миллиардов': 1000000000
                }

                words = words.split()
                total_sum = 0
                current_sum = 0
                current_multiplier = 1

                for word in words:
                    if word in number_dict:
                        current_sum += number_dict[word]
                    elif word in multiplier_dict:
                        current_multiplier = multiplier_dict[word]
                        if current_sum == 0:  # Обработка случаев вроде "миллион" без предшествующего числа
                            current_sum = 1
                        total_sum += current_sum * current_multiplier
                        current_sum = 0  # Сброс текущей суммы после умножения на множитель

                total_sum += current_sum  # Добавляем оставшееся значение, если оно не было умножено на множитель

                return total_sum

            def find_and_convert_sum(self, page, coords):
                text = self.extract_text_by_coords(page, coords).lower()
                # Улучшенное регулярное выражение для захвата суммы прописью и копеек
                match = re.search(r'((?:\w+\s+)+)\s*(?:рубль|рубля|рублей)\s*(\d*)\s*(?:копейка|копейки|копеек)?', text)
                if match:
                    sum_in_words = match.group(1).strip()
                    sum_in_kopecks = match.group(2) or '00'  # Убедитесь, что '00' используется, если копейки не указаны
                    sum_in_numbers = self.word_to_number(sum_in_words)  # Предполагается, что эта функция работает корректно

                    return f"{sum_in_numbers}.{sum_in_kopecks.zfill(2)}"
                else:
                    return None

            def find_payment_order_number(self, text):
                # Регулярное выражение для поиска номера платежного поручения, который может следовать за датой или идти самостоятельно
                # Опционально: дата в формате дд.мм.гггг, за которой следует номер
                match = re.search(r'(?:\d{2}\.\d{2}\.\d{4}\s+)?(?:электронно\s+)?[^\d]*(\d+)', text)
                if match:
                    return match.group(1)  # Возвращаем номер, который может следовать за датой или идти самостоятельно
                else:
                    return None  # Если совпадений нет, возвращаем None

            def extract_text_by_coords(self, page, coords):
                rect = fitz.Rect(coords)
                text = page.get_text("text", clip=rect)
                return text.strip()

            def clean_name(self, name):
                # Регулярное выражение, учитывающее кавычки в начале и в конце названия
                pattern = r'(ООО|ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ|АО|АКЦИОНЕРНОЕ ОБЩЕСТВО|ИП|ИНДИВИДУАЛЬНЫЙ ПРЕДПРИНИМАТЕЛЬ)[\s\S]*?(?="*\s*$)'
                match = re.search(pattern, name, flags=re.IGNORECASE | re.DOTALL)
                if match:
                    # Обеспечивает включение кавычек в начале и в конце, если они есть
                    clean_name = match.group().strip()
                    if name.startswith('"') and not clean_name.startswith('"'):
                        clean_name = '"' + clean_name
                    if name.endswith('"') and not clean_name.endswith('"'):
                        clean_name += '"'
                    return clean_name
                else:
                    # Если ключевые слова не найдены, возвращает исходное название
                    return name

            def find_inn(self, text):
                # Ищем ИНН как строгую последовательность из 10 или 12 цифр
                strict_matches = re.findall(r'(?<!\d)\d{10,12}(?!\d)', text)
                if strict_matches:
                    return strict_matches[0]  # Возвращаем первый подходящий ИНН

                # Затем ищем ИНН, следующий за ключевым словом "ИНН" с учетом пробелов и других символов
                keyword_matches = re.findall(r'ИНН\s+([0-9]{10,12})', text)
                if keyword_matches:
                    return keyword_matches[0]  # Возвращаем первый ИНН, найденный после ключевого слова "ИНН"

                return None  # Если ИНН не найден ни одним из способов, возвращаем None

            def process_pdfs(self):
                data = []
                pdf_files = [f for f in os.listdir(self.pdf_folder) if f.endswith('.pdf')]

                for file_name in pdf_files:
                    file_path = os.path.join(self.pdf_folder, file_name)

                    with fitz.open(file_path) as doc:
                        for page in doc:
                            extracted_data = {'Имя файла': file_name}

                            for key, coords_list in self.config.items():
                                texts = []  # Список для хранения текстов из разных областей для одного ключа

                                for coords in coords_list:
                                    text = self.extract_text_by_coords(page, coords)

                                    # Здесь можно применить специфическую логику обработки для каждого ключа
                                    if key in ['Плательщик', 'Получатель']:
                                        cleaned_text = self.clean_name(text)
                                        if cleaned_text:  # Проверяем, что после очистки текст не пустой
                                            texts.append(cleaned_text)
                                    elif key == 'ИНН плательщика' or key == 'ИНН получателя':
                                        inn = self.find_inn(text)
                                        if inn:  # Проверяем, что ИНН найден
                                            texts.append(inn)
                                    elif key == 'Сумма':
                                        sum_text = self.find_and_convert_sum(page, coords)
                                        if sum_text:  # Проверяем, что сумма найдена и сконвертирована
                                            texts.append(sum_text)
                                    elif key == 'Дата':
                                        date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', text)
                                        if date_match:  # Проверяем, что дата найдена
                                            texts.append(date_match.group(0))
                                    elif key == 'Номер платежного поручения':
                                        order_number = self.find_payment_order_number(text)
                                        if order_number:  # Проверяем, что номер платежного поручения найден
                                            texts.append(order_number)
                                    else:
                                        texts.append(text)

                                # Объединяем все найденные тексты для текущего ключа, разделяя их символами переноса строки
                                extracted_data[key] = '\n'.join(texts)

                            data.append(extracted_data)

                return data  # Возвращаем список словарей с данными

        alfa_config = {
            'Номер платежного поручения': [(26.0, 66.00, 345.08, 79.08)],
            'Дата': [(26.0, 66.00, 345.08, 79.08)],
            'Сумма': [(86.0, 96.00, 444.08, 107.72)], 
            'Плательщик': [(26.00, 161.00, 298.97, 184.36)],
            'ИНН плательщика': [(26.0, 144.18, 246.50, 155.90)],
            'Получатель': [(26.0, 346.00, 26.0 + (298.97 - 26.00), 346.00 + (184.36 - 161.00))],
            'ИНН получателя': [(26.0, 326.00, 464.20, 340.90)]
        }

        modul_config = {
            'Номер платежного поручения': [(23.70, 81.46, 422.37, 93.86)],
            'Дата': [(23.70, 81.46, 422.37, 93.86)],
            'Сумма': [(77.81, 115.51, 341.90, 125.85)],
            'Плательщик': [(25.55, 158.06, 123.15, 168.40)], # подумать над размерами прямоугольника как сделать их больше
            'ИНН плательщика': [(25.55, 142.80, 437.64, 153.14)],
            'Получатель': [(25.55, 334.74, 100.95, 345.07)], # подумать над размерами прямоугольника как сделать их больше
            'ИНН получателя': [(25.55, 319.48, 505.63, 329.81)]
        }

        moskomertz_config = { # доработать логику парсинга внутри функций выше
            'Номер платежного поручения': [(211.0, 103.64, 401.5, 114.71)],
            'Дата': [(211.0, 103.64, 401.5, 114.71)],
            'Сумма': [(127.0, 141.64, 385.53, 152.71)],
            'Плательщик': [(64.0, 193.64, 323.77, 216.21)],
            'ИНН плательщика': [(97.0, 181.89, 280.0, 192.96)],
            'Получатель': [(64.0, 385.64, 64.0 + (323.77 - 26.0), 385.64 + (216.21 - 193.64))], # (64.0, 385.64, 116.30, 396.71) изначально корректные координаты
            'ИНН получателя': [(96.0, 373.64, 483.0, 384.96)]
        }

        otkritie_1_config = { 
            'Номер платежного поручения': [(200.00, 174.94, 215.01, 185.00)],
            'Дата': [(327.49, 174.94, 372.51, 185.00)],
            'Сумма': [(115.00, 229.62, 522.76, 239.68)],
            'Плательщик': [(60.0, 276.94, 418.03, 292.18)],
            'ИНН плательщика': [(95.0, 256.94, 285.04, 267.00)],
            'Получатель': [(60.0, 457.12, 123.49, 467.18)],
            'ИНН получателя': [(60.0, 426.94, 285.04, 437.00)]
        }

        otkritie_2_config = { # доработать логику парсинга внутри функций выше
            'Номер платежного поручения': [(56.0, 76.09, 438.36, 86.15)],
            'Дата': [(56.0, 76.09, 438.36, 86.15)],
            'Сумма': [(114.0, 97.44, 266.58, 107.50)],
            'Плательщик': [(56.0, 155.44, 56.0 + (275.28 - 56.0), 155.44 + (344.85 - 324.44))], # сделать динамичным квадрат,
            'ИНН плательщика': [(81.0, 141.44, 268.04, 151.50)],
            'Получатель': [(56.0, 324.44, 275.28, 344.85)],
            'ИНН получателя': [(56.0, 311.44, 131.04, 321.50)]
        }

        otp_config = {
            'Номер платежного поручения': [(73.50, 98.65, 400.05, 109.27)],
            'Дата': [(73.50, 98.65, 400.05, 109.27)],
            'Сумма': [(137.15, 135.34, 541.47, 145.96)],
            'Плательщик': [(76.36, 185.70, 147.06, 196.32)],
            'ИНН плательщика': [(75.41, 174.19, 429.02, 184.81)],
            'Получатель': [(76.37, 370.60, 126.55, 381.22)],
            'ИНН получателя': [(75.41, 346.86, 478.57, 369.71)]
        }

        peterburg_config = {
            'Номер платежного поручения': [(35.0, 105.25, 370.02, 118.99)],
            'Дата': [(35.0, 105.25, 370.02, 118.99)],
            'Сумма': [(108.0, 141.00, 456.13, 152.64)],
            'Плательщик': [(35.0, 187.00, 164.19, 198.64)],
            'ИНН плательщика': [(63.0, 169.18, 258.24, 180.82)],
            'Получатель': [(35.0, 439.00, 185.60, 450.64)],
            'ИНН получателя': [(63.0, 421.18, 258.24, 432.82)]
        }

        raifaizen_config = {
            'Номер платежного поручения': [(209.0, 73.33, 225.68, 84.50)],
            'Дата': [(309.00, 65.26, 349.00, 74.20)],
            'Сумма': [(106.0, 106.26, 392.88, 124.40)],
            'Плательщик': [(47.0, 155.26, 245.89, 164.50)],
            'ИНН плательщика': [(79.0, 142.26, 123.48, 151.20)],
            'Получатель': [(47.0, 327.26, 101.07, 336.20)],
            'ИНН получателя': [(79.0, 314.26, 219.15, 323.20)]
        }

        rosbank_config = {
            'Номер платежного поручения': [(87.75, 79.50, 342.49, 91.98)],
            'Дата': [(87.75, 79.50, 342.49, 91.98)],
            'Сумма': [(135.38, 111.21, 438.31, 120.00)],
            'Плательщик': [(90.75, 158.50, 153.70, 167.29)],
            'ИНН плательщика': [(90.75, 144.76, 403.04, 154.72)],
            'Получатель': [(90.75, 292.60, 172.50, 301.38)],
            'ИНН получателя': [(90.75, 278.67, 453.49, 288.84)]
        }

        rosselxoz_1_config = {
            'Номер платежного поручения': [(205.0, 99.49, 349.01, 110.66)],
            'Дата': [(205.0, 99.49, 349.01, 110.66)],
            'Сумма': [(105.0, 141.49, 372.56, 152.66)],
            'Плательщик': [(40.0, 193.49, 161.86, 204.66)],
            'ИНН плательщика': [(70.0, 172.49, 408.20, 186.91)],
            'Получатель': [(40.0, 375.49, 105.59, 386.66)],
            'ИНН получателя': [(70.0, 352.49, 480.20, 367.91)]
        }

        rosselxoz_2_config = {
            'Номер платежного поручения': [(195.0, 89.33, 339.01, 100.50)],
            'Дата': [(195.0, 89.33, 339.01, 100.50)],
            'Сумма': [(95.0, 131.33, 358.91, 142.50)],
            'Плательщик': [(30.0, 183.33, 151.86, 194.50)],
            'ИНН плательщика': [(60.0, 162.33, 398.20, 176.75)],
            'Получатель': [(30.0, 365.33, 97.59, 376.50)], 
            'ИНН получателя': [(60.0, 342.33, 470.20, 357.75)]
        }

        sber_1_config = {
            'Номер платежного поручения': [(30.0, 77.90, 203.0, 87.87)],
            'Дата': [(280.0, 71.41, 449.45, 80.27)],
            'Сумма': [(84.0, 105.51, 326.67, 114.37)],
            'Плательщик': [(31.0, 155.51, 128.52, 164.37)],
            'ИНН плательщика': [(38.84, 142.41, 227.0, 151.27)],
            'Получатель': [(31.0, 319.51, 122.00, 328.37)],
            'ИНН получателя': [(38.84, 303.51, 401.0, 315.27)]
        }

        sber_2_config = {
            'Номер платежного поручения': [(40.0, 84.82, 176.45, 97.76)],
            'Дата': [(282.0, 79.86, 318.26, 90.21)],
            'Сумма': [(101.0, 120.86, 324.94, 131.21)],
            'Плательщик': [(40.0, 176.86, 132.58, 187.21)], 
            'ИНН плательщика': [(48.0, 163.86, 238.26, 174.21)],
            'Получатель': [(40.0, 372.86, 150.46, 383.21)], 
            'ИНН получателя': [(48.0, 359.86, 238.26, 370.21)]
        }

        sber_3_config = {
            'Номер платежного поручения': [(30.0, 77.90, 169.99, 87.87)], 
            'Дата': [(280.0, 71.41, 449.45, 80.27)], 
            'Сумма': [(84.0, 105.51, 278.05, 114.37)], 
            'Плательщик': [(31.0, 155.51, 114.04, 164.37)], 
            'ИНН плательщика': [(38.840, 142.41, 227.0, 151.27)], 
            'Получатель': [(31.0, 319.51, 143.47, 328.37)],  
            'ИНН получателя': [(38.84, 303.51, 401.0, 315.27)] 
        }

        vtb_config = {
            'Номер платежного поручения': [(168.0, 104.93, 459.31, 116.00)],
            'Дата': [(168.0, 104.93, 459.31, 116.00)],
            'Сумма': [(113.0, 161.43, 408.09, 172.50)],
            'Плательщик': [(28.0, 223.43, 149.90, 234.50)],
            'ИНН плательщика': [(28.0, 198.18, 238.60, 210.25)],
            'Получатель': [(28.0, 421.43, 168.58, 432.50)],
            'ИНН получателя': [(28.0, 404.93, 238.60, 416.00)]
        }
                
        gpb_config = {
            'Номер платежного поручения': [(51.0, 48.67, 559.99, 68.92)],
            'Дата': [(51.0, 48.67, 559.99, 68.92)],
            'Сумма': [(111.38, 104.13, 387.88, 117.42)],
            'Плательщик': [(54.96, 175.77, 306.14, 200.58)],
            'ИНН плательщика': [(54.96, 147.21, 227.18, 160.50)],
            'Получатель': [(54.96, 359.04, 397.84, 372.33)],
            'ИНН получателя': [(54.96, 345.96, 497.83, 359.25)]
        }

        tinkoff_config = {
            'Номер платежного поручения': [(20.0, 82.99, 161.13, 92.99)],
            'Дата': [(303.72, 77.0, 356.28, 87.0)],
            'Сумма': [(113.0, 113.99, 327.30, 123.99)],
            'Плательщик': [(25.0, 171.99, 307.46, 181.99)],
            'ИНН плательщика': [(52.0, 156.0, 112.90, 166.0)],
            'Получатель': [(25.0, 372.99, 70.17, 382.99)],
            'ИНН получателя': [(25.0, 354.99, 377.29, 367.5)]
        }

        sovkombankf_config = {
            'Номер платежного поручения': [(34.02, 142.30, 196.73, 152.77)],
            'Дата': [(329.54, 133.07, 386.49, 143.55)],
            'Сумма': [(34.02, 169.55, 343.64, 179.09)],
            'Плательщик': [
                (34.02, 206.81, 253.48, 217.28), 
                (34.02, 220.64, 120.07, 231.11)
            ],
            'ИНН плательщика': [(34.02, 192.23, 251.25, 202.71)],
            'Получатель': [(34.02, 425.12, 60.84, 435.59)],
            'ИНН получателя': [(34.02, 396.71, 251.25, 407.19)]
        }

        # Создаем экземпляры класса PDFProcessor для каждой подпапки
        alfa_processor = PDFProcessor('PDF_razbivka/Alfa/Alfa_1', alfa_config)
        modul_processor = PDFProcessor('PDF_razbivka/Modul/Modul_1', modul_config)
        moskomertz_processor = PDFProcessor('PDF_razbivka/Moskomertz/Moskomertz_1', moskomertz_config)
        otkritie_1_processor = PDFProcessor('PDF_razbivka/Otkritie/Otkritie_1', otkritie_1_config)
        otkritie_2_processor = PDFProcessor('PDF_razbivka/Otkritie/Otkritie_2', otkritie_2_config)
        otp_processor = PDFProcessor('PDF_razbivka/OTP/OTP_1', otp_config)
        peterburg_processor = PDFProcessor('PDF_razbivka/Peterburg/Peterburg_1', peterburg_config)
        raifaizen_processor = PDFProcessor('PDF_razbivka/Raifaizen/Raifaizen_1', raifaizen_config)
        rosbank_processor = PDFProcessor('PDF_razbivka/Rosbank/Rosbank_1', rosbank_config)
        rosselxoz_1_processor = PDFProcessor('PDF_razbivka/Rosselxoz/Rosselxoz_1', rosselxoz_1_config)
        rosselxoz_2_processor = PDFProcessor('PDF_razbivka/Rosselxoz/Rosselxoz_2', rosselxoz_2_config)
        sber_1_processor = PDFProcessor('PDF_razbivka/Sber/Sber_1', sber_1_config)
        sber_2_processor = PDFProcessor('PDF_razbivka/Sber/Sber_2', sber_2_config)
        sber_3_processor = PDFProcessor('PDF_razbivka/Sber/Sber_2', sber_3_config)
        vtb_processor = PDFProcessor('PDF_razbivka/VTB/VTB_1', vtb_config)
        gpb_processor = PDFProcessor('PDF_razbivka/GPB/GPB_1', gpb_config)
        tinkoff_processor = PDFProcessor('PDF_razbivka/Tinkoff/Tinkoff_1', tinkoff_config)
        sovkombankf_processor = PDFProcessor('PDF_razbivka/SovkombankF/SovkombankF_1', sovkombankf_config)

        # Обрабатываем PDF файлы и собираем данные
        alfa_data = alfa_processor.process_pdfs()
        modul_data = modul_processor.process_pdfs()
        moskomertz_data = moskomertz_processor.process_pdfs()
        otkritie_1_data = otkritie_1_processor.process_pdfs()
        otkritie_2_data = otkritie_2_processor.process_pdfs()
        otp_data = otp_processor.process_pdfs()
        peterburg_data = peterburg_processor.process_pdfs()
        raifaizen_data = raifaizen_processor.process_pdfs()
        rosbank_data = rosbank_processor.process_pdfs()
        rosselxoz_1_data = rosselxoz_1_processor.process_pdfs()
        rosselxoz_2_data = rosselxoz_2_processor.process_pdfs()
        sber_1_data = sber_1_processor.process_pdfs()
        sber_2_data = sber_2_processor.process_pdfs()
        sber_3_data = sber_3_processor.process_pdfs()
        vtb_data = vtb_processor.process_pdfs()
        gpb_data = gpb_processor.process_pdfs()
        tinkoff_data = tinkoff_processor.process_pdfs()
        sovkombankf_data = sovkombankf_processor.process_pdfs()

        # Объединяем данные из обеих подпапок в один датафрейм
        combined_data = alfa_data + modul_data + moskomertz_data + otkritie_1_data + otkritie_2_data + otp_data + peterburg_data + raifaizen_data + rosbank_data + rosselxoz_1_data + rosselxoz_2_data + sber_1_data + sber_2_data + vtb_data + gpb_data + tinkoff_data + sovkombankf_data #+ sber_3_data

        for item in combined_data:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            item['Имя файла'] = f"{item['Имя файла'].rstrip('.pdf')}_{timestamp}.pdf"
        df_combined = pd.DataFrame(combined_data)

        # Применяем стиль для лучшей читаемости, если необходимо
        df_styled = df_combined.style.set_properties(subset=['Плательщик', 'Получатель'], **{'width': '300px', 'white-space': 'pre-wrap'})

        # Определяем базовый путь. Если скрипт запущен PyInstaller, используем временную директорию
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

        # Настройте следующие переменные в соответствии с вашими данными
        path_to_credentials = os.path.join(base_path, 'pdfparser-413007-a2d94aa51a39.json')  # Указываем путь к нашему файлу с учетными данными
        spreadsheet_name = 'PDFparser'  # Указываем название таблицы в Google Sheets
        worksheet_name = 'first'  # Указываем название листа, куда будут загружаться данные

        # Определите область API, к которой будет предоставлен доступ
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

        # Аутентификация и создание клиента
        credentials = ServiceAccountCredentials.from_json_keyfile_name(path_to_credentials, scope)
        client = gspread.authorize(credentials)

        # Откройте таблицу и выберите лист
        spreadsheet = client.open(spreadsheet_name)
        worksheet = spreadsheet.worksheet(worksheet_name)

        # Проверяем, содержит ли таблица уже какие-либо непустые данные
        existing_data = worksheet.get_all_values()
        has_data = any(row for row in existing_data if any(cell.strip() for cell in row))

        # Теперь данные без заголовков
        data_to_upload = df_combined.values.tolist()

        # Если в таблице нет непустых данных, добавляем заголовки
        if not has_data:
            data_to_upload.insert(0, df_combined.columns.values.tolist())

        # Находим первую пустую строку для добавления данных
        first_empty_row = len(existing_data) + 1 if has_data else 1

        # Обновляем данные, начиная с первой пустой строки
        worksheet.update(f'A{first_empty_row}', data_to_upload)
        # Тест: Подтверждение успешной загрузки данных
        #print("Данные успешно загружены в Google Sheets. Количество строк:", len(data_to_upload))

        #print("Данные успешно загружены в Google Sheets")

        # Функция для перемещения файлов из одной папки в другую
        def move_files_to_archive(source_folder, target_folder_base):
            #print(f"Проверка папки: {source_folder}")  # Для отладки
            if os.path.exists(source_folder):
                for root, dirs, files in os.walk(source_folder):
                    for file_name in files:
                        source_file = os.path.join(root, file_name)
                        relative_path = os.path.relpath(root, source_folder)  # Относительный путь от source_folder до текущей папки
                        target_folder = os.path.join(target_folder_base, relative_path)  # Целевая папка с учетом относительного пути
                        ensure_folder_exists(target_folder)  # Создаем целевую папку, если она не существует
                        #print(f"Целевая папка для архивации: {target_folder}")  # Для отладки

                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                        base_name, ext = os.path.splitext(file_name)
                        new_file_name = f"{base_name}_{timestamp}{ext}"
                        target_file = os.path.join(target_folder, new_file_name)

                        shutil.copy(source_file, target_file)  # Копирование файла в целевую папку
                        #print(f"Файл скопирован: {target_file}")  # Для отладки
                        os.remove(source_file)  # Удаление файла из исходной папки
                        #print(f"Файл удален: {source_file}")  # Для отладки
            #else:
                #print(f"Исходная папка не существует: {source_folder}")  # Для отладки
                    
        archive_folder = 'Archive'  # Определение базовой папки для архивации
        processed_folder = os.path.join(archive_folder, 'Processed')  # Папка для обработанных файлов

        # Использование переменной в коде
        move_files_to_archive('PDF', processed_folder)

        # Рекурсивное удаление файлов из всех подпапок в PDF_razbivka
        for bank_folder in os.listdir('PDF_razbivka'):
            bank_folder_path = os.path.join('PDF_razbivka', bank_folder)
            if os.path.isdir(bank_folder_path):
                for subfolder in os.listdir(bank_folder_path):
                    subfolder_path = os.path.join(bank_folder_path, subfolder)
                    if os.path.isdir(subfolder_path):
                        move_files_to_archive(subfolder_path, processed_folder)

### ОТСЮДА ПРОВЕРЯЕМ!!!
        # Удаляем папку PDF
        shutil.rmtree(pdf_folder)

        neopredelenie_folder = 'PDF_razbivka/Neopredelenie'
        not_processed_folder = os.path.join(archive_folder, 'Not_processed')

        # Перемещаем файлы из Neopredelenie в Archive/Not_processed
        move_files_to_archive(neopredelenie_folder, not_processed_folder)
    
#         # Удаляем папку PDF_razbivka/Neopredelenie
#         shutil.rmtree(neopredelenie_folder)

#         # Путь к корневой папке, которую хотите удалить
#         pdf_razbivka_folder = 'PDF_razbivka'

#         try:
#             shutil.rmtree(pdf_razbivka_folder, ignore_errors=True)
#             print(f"Папка {pdf_razbivka_folder} успешно удалена")
#         except Exception as e:
#             print(f"Ошибка при удалении {pdf_razbivka_folder}: {e}")

        shutil.rmtree('Annotated_PDF', ignore_errors=True)
        shutil.rmtree('TXT', ignore_errors=True)
#         os.remove('processed_uids.txt')
        # Здесь может быть вызов вашего основного метода скрипта, например:
        # main_function()
#         messagebox.showinfo("Информация", "Скрипт успешно выполнен")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Во время выполнения скрипта произошла ошибка с файлом '{file_name}': {e}")      
        
def start_mail_check_loop():
    while True:
        run_script()  # Вызов функции для проверки почты и обработки PDF
        time.sleep(10)  # Приостановка выполнения на 10 секунд

def on_run_script_click():
    threading.Thread(target=start_mail_check_loop).start()

# Создаем окно
root = tk.Tk()
root.title("PDF_parser")

# Устанавливаем размер окна
root.geometry("300x150")

# Создаем кнопку для запуска скрипта
run_button = tk.Button(root, text="Запустить скрипт", command=on_run_script_click)
run_button.pack(pady=20)

# Запускаем главный цикл Tkinter
root.mainloop()