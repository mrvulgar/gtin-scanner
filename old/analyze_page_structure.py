#!/usr/bin/env python3
"""
Анализ структуры страницы PDF и поиск data matrix кодов
"""

import fitz
from PIL import Image
from pylibdmtx.pylibdmtx import decode
import io

pdf_path = "gose.pdf"
pdf_document = fitz.open(pdf_path)

# Анализируем первые 3 страницы
for page_num in range(min(3, len(pdf_document))):
    print(f"\n{'='*70}")
    print(f"СТРАНИЦА {page_num + 1}")
    print('='*70)
    
    page = pdf_document[page_num]
    rect = page.rect
    
    print(f"Размер страницы: {rect.width:.1f} x {rect.height:.1f} точек")
    
    # Рендерим полную страницу
    mat = fitz.Matrix(3.0, 3.0)
    pix = page.get_pixmap(matrix=mat)
    
    print(f"Размер изображения: {pix.width} x {pix.height} пикселей")
    
    # Сохраняем полное изображение для просмотра
    full_img_path = f"page_{page_num + 1}_full.png"
    pix.save(full_img_path)
    print(f"Полное изображение сохранено: {full_img_path}")
    
    # Конвертируем в PIL для анализа
    img_data = pix.tobytes("png")
    image = Image.open(io.BytesIO(img_data))
    
    # Ищем data matrix на всей странице
    decoded_full = decode(image)
    
    if decoded_full:
        for i, obj in enumerate(decoded_full):
            code = obj.data.decode('utf-8', errors='replace')
            rect_obj = obj.rect
            print(f"\nКод #{i+1}: {code}")
            print(f"  Позиция: left={rect_obj.left}, top={rect_obj.top}, "
                  f"width={rect_obj.width}, height={rect_obj.height}")
            print(f"  Процент от страницы: "
                  f"X={rect_obj.left/pix.width*100:.1f}%, "
                  f"Y={rect_obj.top/pix.height*100:.1f}%")
    
    # Тестируем обрезку: только левый верхний угол (например, 30% x 30%)
    crop_percent = 0.3
    crop_width = int(pix.width * crop_percent)
    crop_height = int(pix.height * crop_percent)
    
    print(f"\n--- Тест обрезки (левый верхний угол {crop_percent*100:.0f}%) ---")
    
    # Создаем обрезанное изображение
    cropped = image.crop((0, 0, crop_width, crop_height))
    crop_img_path = f"page_{page_num + 1}_cropped.png"
    cropped.save(crop_img_path)
    print(f"Обрезанное изображение: {crop_width}x{crop_height} пикселей")
    print(f"Сохранено: {crop_img_path}")
    
    # Ищем на обрезанном изображении
    decoded_crop = decode(cropped)
    
    if decoded_crop:
        code = decoded_crop[0].data.decode('utf-8', errors='replace')
        print(f"✓ Код найден на обрезанном: {code}")
    else:
        print("✗ Код НЕ найден на обрезанном")
    
    # Тестируем разные размеры обрезки
    print("\n--- Тест разных размеров обрезки ---")
    for percent in [0.2, 0.25, 0.3, 0.4, 0.5]:
        w = int(pix.width * percent)
        h = int(pix.height * percent)
        test_crop = image.crop((0, 0, w, h))
        test_decode = decode(test_crop)
        
        status = "✓" if test_decode else "✗"
        print(f"{status} {percent*100:.0f}% ({w}x{h} пикс): "
              f"{'найден' if test_decode else 'НЕ найден'}")

pdf_document.close()

print(f"\n{'='*70}")
print("Анализ завершён! Проверьте сохранённые изображения.")
print('='*70)

