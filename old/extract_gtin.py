#!/usr/bin/env python3
"""
Скрипт для извлечения GTIN data matrix кодов из PDF файла
"""

import sys
import csv
from pathlib import Path

try:
    import fitz  # PyMuPDF
    from pylibdmtx.pylibdmtx import decode
    from PIL import Image
    import io
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("\nУстановите необходимые библиотеки:")
    print("pip install PyMuPDF pylibdmtx Pillow")
    sys.exit(1)


def extract_datamatrix_from_pdf(pdf_path, output_csv_path):
    """
    Извлекает data matrix коды из PDF и сохраняет в CSV
    
    Args:
        pdf_path: путь к PDF файлу
        output_csv_path: путь к выходному CSV файлу
    """
    print(f"Обработка PDF: {pdf_path}")
    
    # Открываем PDF
    pdf_document = fitz.open(pdf_path)
    all_codes = []
    total_pages = len(pdf_document)
    
    print(f"Всего страниц: {total_pages}")
    print("Начинаем обработку...")
    
    # Обрабатываем каждую страницу
    for page_num in range(total_pages):
        # Показываем прогресс каждые 10 страниц
        if (page_num + 1) % 10 == 0 or page_num == 0:
            progress = (page_num + 1) / total_pages * 100
            print(f"Прогресс: {page_num + 1}/{total_pages} ({progress:.1f}%) | Найдено кодов: {len(all_codes)}")
        
        page = pdf_document[page_num]
        
        # Конвертируем страницу в изображение с оптимальным разрешением
        mat = fitz.Matrix(2.5, 2.5)  # немного снизили для скорости
        pix = page.get_pixmap(matrix=mat)
        
        # Конвертируем в PIL Image
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        
        # Распознаём data matrix коды
        decoded_objects = decode(image)
        
        for obj in decoded_objects:
            # Декодируем данные
            try:
                code_data = obj.data.decode('utf-8')
                all_codes.append(code_data)
            except UnicodeDecodeError:
                # Если не UTF-8, пробуем latin-1
                code_data = obj.data.decode('latin-1')
                all_codes.append(code_data)
    
    pdf_document.close()
    
    print(f"\nВсего найдено кодов: {len(all_codes)}")
    
    # Сохраняем в CSV
    if all_codes:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            for code in all_codes:
                # Проверяем, нужны ли кавычки (если есть двойные кавычки внутри)
                if '"' in code:
                    # CSV writer автоматически обработает это
                    writer.writerow([code])
                else:
                    writer.writerow([code])
        
        print(f"Коды сохранены в: {output_csv_path}")
    else:
        print("ВНИМАНИЕ: Коды не найдены!")
        print("Попробуйте:")
        print("1. Проверить качество PDF")
        print("2. Убедиться, что это действительно Data Matrix коды")
        print("3. Увеличить разрешение при сканировании")
    
    return all_codes


if __name__ == "__main__":
    pdf_file = "goze1.pdf"
    output_file = f"{Path(pdf_file).stem}_extracted.csv"
    
    if not Path(pdf_file).exists():
        print(f"Файл не найден: {pdf_file}")
        sys.exit(1)
    
    codes = extract_datamatrix_from_pdf(pdf_file, output_file)
    
    print(f"\n{'='*50}")
    print(f"Готово! Извлечено {len(codes)} кодов")
    print(f"Результат сохранён в: {output_file}")


