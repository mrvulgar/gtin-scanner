#!/usr/bin/env python3
"""
Быстрая версия с многопоточностью для извлечения GTIN data matrix кодов из PDF
"""

import sys
import csv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

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


def process_page(pdf_path, page_num, total_pages):
    """
    Обрабатывает одну страницу PDF
    
    Args:
        pdf_path: путь к PDF файлу
        page_num: номер страницы
        total_pages: общее количество страниц
        
    Returns:
        tuple: (page_num, code or None)
    """
    try:
        # Открываем PDF для этого потока
        pdf_document = fitz.open(pdf_path)
        page = pdf_document[page_num]
        
        # Используем масштаб 2.0x - достаточно для маленьких страниц
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        
        # Конвертируем в PIL Image
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        
        # Распознаём data matrix коды
        decoded_objects = decode(image)
        
        pdf_document.close()
        
        if decoded_objects:
            # Берём первый найденный код
            try:
                code_data = decoded_objects[0].data.decode('utf-8')
                return (page_num, code_data)
            except UnicodeDecodeError:
                code_data = decoded_objects[0].data.decode('latin-1')
                return (page_num, code_data)
        
        return (page_num, None)
        
    except Exception as e:
        print(f"Ошибка на странице {page_num + 1}: {e}")
        return (page_num, None)


def extract_datamatrix_from_pdf_parallel(pdf_path, output_csv_path, max_workers=8):
    """
    Извлекает data matrix коды из PDF с использованием многопоточности
    
    Args:
        pdf_path: путь к PDF файлу
        output_csv_path: путь к выходному CSV файлу
        max_workers: количество параллельных потоков
    """
    print(f"Обработка PDF: {pdf_path}")
    print(f"Количество потоков: {max_workers}")
    
    # Получаем общее количество страниц
    pdf_document = fitz.open(pdf_path)
    total_pages = len(pdf_document)
    pdf_document.close()
    
    print(f"Всего страниц: {total_pages}")
    print("Начинаем обработку...\n")
    
    start_time = time.time()
    
    # Словарь для хранения кодов (page_num: code)
    codes_dict = {}
    processed = 0
    found = 0
    
    # Обрабатываем страницы параллельно
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Запускаем задачи
        futures = {
            executor.submit(process_page, pdf_path, page_num, total_pages): page_num
            for page_num in range(total_pages)
        }
        
        # Собираем результаты
        for future in as_completed(futures):
            page_num, code = future.result()
            processed += 1
            
            if code:
                codes_dict[page_num] = code
                found += 1
            
            # Показываем прогресс каждые 50 страниц
            if processed % 50 == 0 or processed == total_pages:
                elapsed = time.time() - start_time
                speed = processed / elapsed if elapsed > 0 else 0
                eta = (total_pages - processed) / speed if speed > 0 else 0
                progress = processed / total_pages * 100
                
                print(f"Прогресс: {processed}/{total_pages} ({progress:.1f}%) | "
                      f"Найдено: {found} | Скорость: {speed:.1f} стр/сек | "
                      f"Осталось: ~{eta:.0f}сек")
    
    # Сортируем коды по номеру страницы
    all_codes = [codes_dict[i] for i in sorted(codes_dict.keys())]
    
    elapsed_time = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"Обработка завершена за {elapsed_time:.1f} секунд")
    print(f"Всего найдено кодов: {len(all_codes)} из {total_pages} страниц")
    print(f"Средняя скорость: {total_pages/elapsed_time:.1f} страниц/сек")
    
    # Сохраняем в CSV
    if all_codes:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            for code in all_codes:
                writer.writerow([code])
        
        print(f"\nКоды сохранены в: {output_csv_path}")
    else:
        print("\nВНИМАНИЕ: Коды не найдены!")
    
    return all_codes


if __name__ == "__main__":
    pdf_file = "goze1.pdf"
    output_file = f"{Path(pdf_file).stem}_extracted.csv"
    
    if not Path(pdf_file).exists():
        print(f"Файл не найден: {pdf_file}")
        sys.exit(1)
    
    # Используем 8 потоков для ускорения (можно увеличить до 16)
    codes = extract_datamatrix_from_pdf_parallel(pdf_file, output_file, max_workers=8)
    
    print(f"\n{'='*60}")
    print(f"✓ Готово! Извлечено {len(codes)} кодов")
    print(f"✓ Результат: {output_file}")

