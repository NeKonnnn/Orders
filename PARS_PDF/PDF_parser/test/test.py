import os
import easyocr

def text_recognition(file_path, text_file_name="result.txt"):
    reader = easyocr.Reader(["ru", "en"])
    result = reader.readtext(file_path, detail=0, paragraph=True)
    
    with open(text_file_name, "w", encoding="utf-8") as file:  # Указываем кодировку utf-8
        for line in result:
            file.write(f"{line}\n\n")
    
    return f"Result wrote into {text_file_name}"

def main():
    input_folder = r"C:\Users\NeKonn\orders\PDF_parser\Output_Images"
    output_folder = r"C:\Users\NeKonn\orders\PDF_parser\test\TEXT"

    # Создание папки output, если она не существует
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Получение списка всех JPG файлов
    jpg_files = [f for f in os.listdir(input_folder) if f.endswith('.jpg')]

    # Обработка каждого файла
    for file_name in jpg_files:
        file_path = os.path.join(input_folder, file_name)
        text_file_name = os.path.join(output_folder, os.path.splitext(file_name)[0] + ".txt")
        result = text_recognition(file_path, text_file_name)
        print(result)

if __name__ == "__main__":
    main()