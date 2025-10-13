#!/usr/bin/env python3
"""
Извлечение GTIN data matrix кодов из PDF с прогресс-баром и высоким качеством
"""

import sys
import csv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import timedelta

try:
    import fitz  # PyMuPDF
    from pylibdmtx.pylibdmtx import decode
    from PIL import Image
    from tqdm import tqdm
    import io
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("\nУстановите необходимые библиотеки:")
    print("pip install PyMuPDF pylibdmtx Pillow tqdm")
    sys.exit(1)


def process_page(pdf_path, page_num, scale=3.0):
    """
    Обрабатывает одну страницу PDF с высоким качеством
    
    Args:
        pdf_path: путь к PDF файлу
        page_num: номер страницы
        scale: масштаб для рендеринга (3.0 = высокое качество)
        
    Returns:
        tuple: (page_num, code or None, success)
    """
    try:
        # Открываем PDF для этого потока
        pdf_document = fitz.open(pdf_path)
        page = pdf_document[page_num]
        
        # Высокое качество: масштаб 3.0x
        mat = fitz.Matrix(scale, scale)
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
                return (page_num, code_data, True)
            except UnicodeDecodeError:
                code_data = decoded_objects[0].data.decode('latin-1')
                return (page_num, code_data, True)
        
        return (page_num, None, False)
        
    except Exception as e:
        return (page_num, None, False)


def extract_datamatrix_from_pdf_parallel(pdf_path, output_csv_path, max_workers=8, scale=3.0):
    """
    Извлекает data matrix коды из PDF с прогресс-баром
    
    Args:
        pdf_path: путь к PDF файлу
        output_csv_path: путь к выходному CSV файлу
        max_workers: количество параллельных потоков
        scale: масштаб рендеринга (больше = выше качество)
    """
    print("\n" + "="*70)
    print(f"📄 ИЗВЛЕЧЕНИЕ GTIN DATA MATRIX КОДОВ ИЗ PDF")
    print("="*70)
    
    # Получаем общее количество страниц
    pdf_document = fitz.open(pdf_path)
    total_pages = len(pdf_document)
    pdf_document.close()
    
    print(f"\n📋 Файл: {pdf_path}")
    print(f"📊 Всего страниц: {total_pages:,}")
    print(f"🔧 Потоков: {max_workers}")
    print(f"🎨 Качество: {scale}x (высокое)")
    print(f"\n⏳ Начинаем обработку...\n")
    
    start_time = time.time()
    
    # Словарь для хранения кодов (page_num: code)
    codes_dict = {}
    found = 0
    errors = 0
    
    # Создаём прогресс-бар
    with tqdm(total=total_pages, 
              desc="🔍 Сканирование",
              unit="стр",
              bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]',
              colour='green',
              ncols=100) as pbar:
        
        # Обрабатываем страницы параллельно
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Запускаем задачи
            futures = {
                executor.submit(process_page, pdf_path, page_num, scale): page_num
                for page_num in range(total_pages)
            }
            
            # Собираем результаты
            for future in as_completed(futures):
                page_num, code, success = future.result()
                
                if success and code:
                    codes_dict[page_num] = code
                    found += 1
                elif not success:
                    errors += 1
                
                # Обновляем прогресс-бар с дополнительной информацией
                pbar.set_postfix({
                    'найдено': found,
                    'ошибок': errors
                })
                pbar.update(1)
    
    # Сортируем коды по номеру страницы
    all_codes = [codes_dict[i] for i in sorted(codes_dict.keys())]
    
    elapsed_time = time.time() - start_time
    
    # Итоговая статистика
    print("\n" + "="*70)
    print("📊 РЕЗУЛЬТАТЫ ОБРАБОТКИ")
    print("="*70)
    print(f"✓ Обработано страниц: {total_pages:,}")
    print(f"✓ Найдено кодов: {found:,}")
    print(f"✗ Не распознано: {total_pages - found:,}")
    if errors > 0:
        print(f"⚠ Ошибок: {errors}")
    print(f"⏱ Время обработки: {timedelta(seconds=int(elapsed_time))}")
    print(f"🚀 Скорость: {total_pages/elapsed_time:.1f} страниц/сек")
    print(f"📈 Успешность: {(found/total_pages*100):.1f}%")
    
    # Сохраняем в CSV
    if all_codes:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            for code in all_codes:
                writer.writerow([code])
        
        print(f"\n💾 Коды сохранены в: {output_csv_path}")
        
        # Показываем примеры первых и последних кодов
        print("\n📝 Примеры кодов:")
        print(f"   Первый: {all_codes[0]}")
        if len(all_codes) > 1:
            print(f"   Последний: {all_codes[-1]}")
    else:
        print("\n⚠️  ВНИМАНИЕ: Коды не найдены!")
    
    print("="*70 + "\n")
    
    return all_codes


if __name__ == "__main__":
    pdf_file = "gose.pdf"
    output_file = f"{Path(pdf_file).stem}_extracted.csv"
    
    if not Path(pdf_file).exists():
        print(f"❌ Файл не найден: {pdf_file}")
        sys.exit(1)
    
    # Параметры обработки
    NUM_WORKERS = 8   # Количество потоков (можно увеличить до 12-16)
    SCALE = 3.0       # Масштаб: 3.0 = высокое качество
    
    codes = extract_datamatrix_from_pdf_parallel(
        pdf_file, 
        output_file, 
        max_workers=NUM_WORKERS,
        scale=SCALE
    )
    
    if codes:
        print(f"✅ Успешно извлечено {len(codes)} GTIN кодов!")
    else:
        print("❌ Не удалось извлечь коды")
        sys.exit(1)

