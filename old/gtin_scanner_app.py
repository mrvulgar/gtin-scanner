#!/usr/bin/env python3
"""
Веб-приложение для извлечения GTIN data matrix кодов из PDF файлов
"""

import sys
import csv
import io
import time
from pathlib import Path
from typing import Optional, Tuple

try:
    import gradio as gr
    import fitz  # PyMuPDF
    from pylibdmtx.pylibdmtx import decode
    from PIL import Image, ImageDraw
    import numpy as np
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("\nУстановите необходимые библиотеки:")
    print("pip install gradio PyMuPDF pylibdmtx Pillow")
    sys.exit(1)


class GTINScanner:
    def __init__(self):
        self.pdf_document = None
        self.pdf_path = None
        self.crop_rect = None
        self.stop_requested = False
        
    def load_pdf_preview(self, pdf_file):
        """Загрузка первой страницы PDF для выбора области"""
        if pdf_file is None:
            return None, "⚠️ Пожалуйста, загрузите PDF файл"
        
        try:
            self.pdf_path = pdf_file.name
            self.pdf_document = fitz.open(self.pdf_path)
            page = self.pdf_document[0]
            
            # Рендерим первую страницу с высоким разрешением
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            
            # Конвертируем в PIL Image
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            
            total_pages = len(self.pdf_document)
            message = f"✅ PDF загружен: {Path(self.pdf_path).name}\n📄 Страниц: {total_pages}\n\n👆 Выделите область с QR кодом на изображении выше"
            
            # Для AnnotatedImage нужно вернуть кортеж (изображение, None)
            return (image, None), message
            
        except Exception as e:
            return None, f"❌ Ошибка при загрузке PDF: {str(e)}"
    
    def process_crop_selection(self, image_data):
        """Обработка выделенной области"""
        if image_data is None:
            return "⚠️ Сначала загрузите PDF и выделите область"
        
        # Проверяем, что image_data - это кортеж (изображение, аннотации)
        if isinstance(image_data, tuple) and len(image_data) >= 2:
            annotations = image_data[1]
            
            if annotations and len(annotations) > 0:
                # Получаем данные о выделенной области
                box = annotations[0]
                x1, y1 = int(box['xmin']), int(box['ymin'])
                x2, y2 = int(box['xmax']), int(box['ymax'])
                
                # Сохраняем координаты с учетом масштаба 2.0
                self.crop_rect = (x1, y1, x2, y2)
                
                width = x2 - x1
                height = y2 - y1
                
                return f"✅ Область выбрана: {width}x{height} px\n\n▶️ Теперь нажмите 'Начать сканирование'"
        
        return "⚠️ Выделите область с QR кодом, используя инструмент выделения"
    
    def scan_pdf(self, progress=gr.Progress()):
        """Сканирование PDF с прогресс-баром"""
        if self.pdf_document is None:
            yield "❌ PDF файл не загружен", None, "Загрузите PDF файл"
            return
        
        if self.crop_rect is None:
            yield "❌ Область не выбрана", None, "Выделите область с QR кодом"
            return
        
        all_codes = []
        total_pages = len(self.pdf_document)
        self.stop_requested = False
        
        try:
            progress(0, desc="Начинаем сканирование...")
            
            for page_num in range(total_pages):
                if self.stop_requested:
                    status = f"⏹ Остановлено на странице {page_num}/{total_pages}\n✅ Найдено кодов: {len(all_codes)}"
                    yield status, None, f"Обработано {page_num} из {total_pages} страниц"
                    break
                
                # Обновляем прогресс
                progress_value = (page_num + 1) / total_pages
                progress(progress_value, desc=f"Обработка страницы {page_num + 1}/{total_pages}")
                
                # Получаем страницу
                page = self.pdf_document[page_num]
                
                # Рендерим страницу с тем же масштабом
                mat = fitz.Matrix(2.5, 2.5)
                pix = page.get_pixmap(matrix=mat)
                
                # Конвертируем в PIL Image
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                
                # Обрезаем по выделенной области (с учетом масштаба)
                scale = 2.5 / 2.0  # соотношение масштабов рендеринга и превью
                crop_x1 = int(self.crop_rect[0] * scale)
                crop_y1 = int(self.crop_rect[1] * scale)
                crop_x2 = int(self.crop_rect[2] * scale)
                crop_y2 = int(self.crop_rect[3] * scale)
                
                cropped_image = image.crop((crop_x1, crop_y1, crop_x2, crop_y2))
                
                # Распознаём data matrix коды
                decoded_objects = decode(cropped_image)
                
                for obj in decoded_objects:
                    try:
                        code_data = obj.data.decode('utf-8')
                        all_codes.append(code_data)
                    except UnicodeDecodeError:
                        code_data = obj.data.decode('latin-1')
                        all_codes.append(code_data)
                
                # Обновляем статус
                status = f"📊 Прогресс: {page_num + 1}/{total_pages} ({progress_value*100:.1f}%)\n✅ Найдено кодов: {len(all_codes)}"
                stats = f"Страниц: {page_num + 1}/{total_pages} | Кодов: {len(all_codes)}"
                
                yield status, None, stats
            
            # Генерируем CSV файл
            if all_codes and not self.stop_requested:
                csv_content = self._generate_csv(all_codes)
                output_filename = f"{Path(self.pdf_path).stem}_extracted.csv"
                
                final_status = f"✅ Сканирование завершено!\n📄 Страниц обработано: {total_pages}\n✅ Найдено кодов: {len(all_codes)}\n💾 Файл готов к скачиванию"
                final_stats = f"Завершено: {total_pages}/{total_pages} | Кодов: {len(all_codes)}"
                
                yield final_status, csv_content, final_stats
            elif not all_codes:
                yield "⚠️ Коды не найдены в выделенной области", None, "Проверьте выделенную область"
            
        except Exception as e:
            yield f"❌ Ошибка при сканировании: {str(e)}", None, "Ошибка"
    
    def _generate_csv(self, codes):
        """Генерация CSV файла"""
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        for code in codes:
            writer.writerow([code])
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content
    
    def stop_scan(self):
        """Остановка сканирования"""
        self.stop_requested = True
        return "⏹ Запрос на остановку отправлен..."


# Создаем экземпляр сканера
scanner = GTINScanner()


# Создаем интерфейс Gradio
with gr.Blocks(title="GTIN Scanner", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # 🔍 GTIN Scanner - Извлечение Data Matrix кодов из PDF
    
    ### Инструкция:
    1. **Загрузите PDF файл** в поле ниже
    2. **Выделите область с QR кодом** на превью первой страницы (используйте инструмент выделения)
    3. **Нажмите "Начать сканирование"** для обработки всех страниц
    4. **Скачайте результат** в формате CSV
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            # Загрузка PDF
            pdf_input = gr.File(
                label="📁 Загрузите PDF файл",
                file_types=[".pdf"],
                type="filepath"
            )
            
            # Превью с возможностью выделения области
            preview_image = gr.AnnotatedImage(
                label="📄 Превью первой страницы (выделите область с QR кодом)",
                height=600
            )
            
            load_status = gr.Textbox(
                label="📝 Статус",
                value="Ожидание загрузки PDF...",
                lines=3
            )
        
        with gr.Column(scale=1):
            # Кнопки управления
            gr.Markdown("### Управление")
            
            crop_btn = gr.Button(
                "✂️ Подтвердить выделение",
                variant="secondary",
                size="lg"
            )
            
            scan_btn = gr.Button(
                "▶️ Начать сканирование",
                variant="primary",
                size="lg"
            )
            
            stop_btn = gr.Button(
                "⏹ Остановить",
                variant="stop",
                size="lg"
            )
            
            # Прогресс и статистика
            gr.Markdown("### 📊 Статистика")
            
            stats_display = gr.Textbox(
                label="Прогресс",
                value="Готов к работе",
                lines=2
            )
            
            scan_status = gr.Textbox(
                label="Детали сканирования",
                value="",
                lines=5
            )
            
            # Результат
            gr.Markdown("### 💾 Результат")
            
            csv_output = gr.File(
                label="Скачать CSV файл",
                visible=True
            )
    
    # Обработчики событий
    pdf_input.change(
        fn=scanner.load_pdf_preview,
        inputs=[pdf_input],
        outputs=[preview_image, load_status]
    )
    
    crop_btn.click(
        fn=scanner.process_crop_selection,
        inputs=[preview_image],
        outputs=[load_status]
    )
    
    scan_btn.click(
        fn=scanner.scan_pdf,
        outputs=[scan_status, csv_output, stats_display]
    )
    
    stop_btn.click(
        fn=scanner.stop_scan,
        outputs=[scan_status]
    )
    
    gr.Markdown("""
    ---
    **Примечание:** Убедитесь, что QR коды расположены в одном и том же месте на всех страницах PDF.
    """)


if __name__ == "__main__":
    print("🚀 Запуск GTIN Scanner...")
    print("📱 Приложение откроется в браузере")
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True
    )

