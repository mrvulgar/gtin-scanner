#!/usr/bin/env python3
"""
Анализ качества PDF для оптимизации обработки
"""

import fitz
from PIL import Image
import io

pdf_path = "goze1.pdf"
pdf_document = fitz.open(pdf_path)

print(f"PDF: {pdf_path}")
print(f"Всего страниц: {len(pdf_document)}")
print("\nАнализ первых 3 страниц:")

for page_num in range(min(3, len(pdf_document))):
    page = pdf_document[page_num]
    
    # Получаем размер страницы
    rect = page.rect
    print(f"\nСтраница {page_num + 1}:")
    print(f"  Размер: {rect.width:.0f} x {rect.height:.0f} точек")
    
    # Тестируем разные масштабы
    for scale in [1.0, 1.5, 2.0, 2.5]:
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat)
        
        img_size = len(pix.tobytes("png")) / 1024  # размер в KB
        print(f"  Масштаб {scale}x: {pix.width} x {pix.height} пикселей, размер: {img_size:.0f} KB")

pdf_document.close()

