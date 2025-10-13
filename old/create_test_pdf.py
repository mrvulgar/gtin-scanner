#!/usr/bin/env python3
"""
Создание тестового PDF с QR кодами для отладки
"""

import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import qrcode
import io

def create_test_pdf():
    """Создает тестовый PDF с QR кодами"""
    
    # Создаем новый PDF документ
    doc = fitz.open()
    
    # Генерируем несколько QR кодов
    test_codes = [
        "04650505840616",
        "1234567890123", 
        "9876543210987",
        "5555555555555"
    ]
    
    for i, code in enumerate(test_codes):
        # Создаем новую страницу
        page = doc.new_page(width=595, height=842)  # A4 размер
        
        # Генерируем QR код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(code)
        qr.make(fit=True)
        
        # Создаем изображение QR кода
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Увеличиваем размер QR кода
        qr_img = qr_img.resize((200, 200))
        
        # Создаем фон страницы
        bg_img = Image.new('RGB', (595, 842), 'white')
        draw = ImageDraw.Draw(bg_img)
        
        # Добавляем текст
        draw.text((50, 50), f"Тестовая страница {i+1}", fill='black')
        draw.text((50, 80), f"QR код: {code}", fill='black')
        
        # Размещаем QR код в одном и том же месте на всех страницах
        bg_img.paste(qr_img, (150, 150))
        
        # Конвертируем PIL Image в байты
        img_bytes = io.BytesIO()
        bg_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Добавляем изображение на страницу PDF
        img_rect = fitz.Rect(0, 0, 595, 842)
        page.insert_image(img_rect, stream=img_bytes.getvalue())
    
    # Сохраняем PDF
    doc.save("test_qr_codes.pdf")
    doc.close()
    
    print("✅ Тестовый PDF создан: test_qr_codes.pdf")
    print(f"📄 Страниц: {len(test_codes)}")
    print(f"🔢 Тестовые коды: {test_codes}")

if __name__ == "__main__":
    create_test_pdf()
