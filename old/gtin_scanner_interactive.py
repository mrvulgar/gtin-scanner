#!/usr/bin/env python3
"""
Интерактивное веб-приложение для извлечения GTIN data matrix кодов из PDF файлов
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
        self.preview_image = None
        
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
            self.preview_image = Image.open(io.BytesIO(img_data))
            
            total_pages = len(self.pdf_document)
            message = f"✅ PDF загружен: {Path(self.pdf_path).name}\n📄 Страниц: {total_pages}\n\n🎨 Используйте инструмент 'Select region' на изображении выше, чтобы выделить область с QR кодом"
            
            return self.preview_image, message
            
        except Exception as e:
            return None, f"❌ Ошибка при загрузке PDF: {str(e)}"
    
    def process_selected_region(self, edited_image):
        """Обработка выделенной области из ImageEditor"""
        if edited_image is None:
            return "⚠️ Выделите область с QR кодом на изображении"
        
        try:
            # edited_image содержит информацию о выделенной области
            if hasattr(edited_image, 'layers') and edited_image.layers:
                # Получаем координаты выделенной области
                layers = edited_image.layers
                if len(layers) > 0:
                    layer = layers[0]
                    if hasattr(layer, 'bbox'):
                        bbox = layer.bbox
                        x1, y1, x2, y2 = bbox
                        
                        # Сохраняем координаты
                        self.crop_rect = (int(x1), int(y1), int(x2), int(y2))
                        
                        width = int(x2 - x1)
                        height = int(y2 - y1)
                        
                        return f"✅ Область выбрана: {width}x{height} px\n📍 Координаты: ({int(x1)},{int(y1)}) - ({int(x2)},{int(y2)})\n\n▶️ Теперь нажмите 'Начать сканирование'"
            
            return "⚠️ Выделите область с QR кодом, используя инструмент 'Select region'"
            
        except Exception as e:
            return f"❌ Ошибка при обработке области: {str(e)}"
    
    def scan_pdf(self, progress=gr.Progress()):
        """Сканирование PDF с прогресс-баром"""
        if self.pdf_document is None:
            yield "❌ PDF файл не загружен", None, "Загрузите PDF файл"
            return
        
        if self.crop_rect is None:
            yield "❌ Область не выбрана", None, "Выделите область с QR кодом на изображении"
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
    2. **Выделите область с QR кодом** прямо на изображении (используйте инструмент "Select region")
    3. **Нажмите "Подтвердить выделение"** 
    4. **Нажмите "Начать сканирование"** для обработки всех страниц
    5. **Скачайте результат** в формате CSV
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            # Загрузка PDF
            pdf_input = gr.File(
                label="📁 Загрузите PDF файл",
                file_types=[".pdf"],
                type="filepath"
            )
            
            # Интерактивное превью с возможностью выделения области
            preview_image = gr.ImageEditor(
                label="📄 Превью первой страницы - выделите область с QR кодом",
                height=600,
                brush=gr.Brush(default_size=5, colors=["#FF0000"]),
                transforms=["crop", "select_region"]
            )
            
            load_status = gr.Textbox(
                label="📝 Статус",
                value="Ожидание загрузки PDF...",
                lines=3
            )
        
        with gr.Column(scale=1):
            # Кнопки управления
            gr.Markdown("### 🎯 Выделение области")
            
            confirm_selection_btn = gr.Button(
                "✅ Подтвердить выделение",
                variant="secondary",
                size="lg"
            )
            
            selection_status = gr.Textbox(
                label="Статус выделения",
                value="Выделите область с QR кодом на изображении",
                lines=3
            )
            
            # Кнопки управления сканированием
            gr.Markdown("### ▶️ Управление сканированием")
            
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
    
    confirm_selection_btn.click(
        fn=scanner.process_selected_region,
        inputs=[preview_image],
        outputs=[selection_status]
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
    **💡 Как выделить область:**
    1. Загрузите PDF и посмотрите на превью
    2. Найдите QR/Data Matrix код на изображении
    3. Используйте инструмент **"Select region"** (иконка прямоугольника с пунктиром)
    4. Нарисуйте прямоугольник вокруг QR кода
    5. Нажмите "✅ Подтвердить выделение"
    6. Запустите сканирование
    
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
