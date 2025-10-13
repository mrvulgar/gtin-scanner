#!/usr/bin/env python3
"""
Создание тестового PDF с Data Matrix кодами
"""

import fitz  # PyMuPDF
from PIL import Image, ImageDraw
from pylibdmtx.pylibdmtx import encode
import io

def create_test_datamatrix_pdf():
    """Создает тестовый PDF с Data Matrix кодами"""
    
    # Создаем новый PDF документ
    doc = fitz.open()
    
    # Генерируем несколько Data Matrix кодов
    test_codes = [
        "04650505840616",
        "1234567890123", 
        "9876543210987",
        "5555555555555"
    ]
    
    for i, code in enumerate(test_codes):
        # Создаем новую страницу
        page = doc.new_page(width=595, height=842)  # A4 размер
        
        # Генерируем Data Matrix код
        encoded = encode(code.encode('utf-8'))
        
        # Конвертируем в PIL Image
        width = encoded.width
        height = encoded.height
        pixels = encoded.pixels
        
        # Создаем изображение Data Matrix правильно
        dm_img = Image.new('L', (width, height), 255)  # Белый фон
        
        # Заполняем пиксели
        for y in range(height):
            for x in range(width):
                pixel_index = y * width + x
                if pixel_index < len(pixels) and pixels[pixel_index]:
                    dm_img.putpixel((x, y), 0)  # Черный пиксель
        
        # Увеличиваем размер Data Matrix кода для лучшей видимости
        dm_img = dm_img.resize((200, 200), Image.Resampling.NEAREST)
        
        # Создаем фон страницы
        bg_img = Image.new('RGB', (595, 842), 'white')
        draw = ImageDraw.Draw(bg_img)
        
        # Добавляем текст
        draw.text((50, 50), f"Тестовая страница {i+1}", fill='black')
        draw.text((50, 80), f"Data Matrix код: {code}", fill='black')
        
        # Размещаем Data Matrix код в одном и том же месте на всех страницах
        bg_img.paste(dm_img, (150, 150))
        
        # Конвертируем PIL Image в байты
        img_bytes = io.BytesIO()
        bg_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Добавляем изображение на страницу PDF
        img_rect = fitz.Rect(0, 0, 595, 842)
        page.insert_image(img_rect, stream=img_bytes.getvalue())
    
    # Сохраняем PDF
    doc.save("test_datamatrix_codes.pdf")
    doc.close()
    
    print("✅ Тестовый PDF с Data Matrix создан: test_datamatrix_codes.pdf")
    print(f"📄 Страниц: {len(test_codes)}")
    print(f"🔢 Тестовые коды: {test_codes}")

if __name__ == "__main__":
    create_test_datamatrix_pdf()
