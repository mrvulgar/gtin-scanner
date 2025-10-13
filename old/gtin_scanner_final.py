#!/usr/bin/env python3
"""
Финальная версия веб-приложения для извлечения Data Matrix кодов из PDF файлов
"""

import sys
import csv
import io
import time
import threading
import logging
from pathlib import Path
from typing import Optional, Tuple

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gtin_scanner_final.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

try:
    import gradio as gr
    import fitz  # PyMuPDF
    from pylibdmtx.pylibdmtx import decode
    from PIL import Image, ImageDraw, ImageEnhance
    import numpy as np
except ImportError as e:
    logger.error(f"Ошибка импорта: {e}")
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
        self.selection_start = None
        self.selection_end = None
        self.scanning = False
        self.scan_results = {
            "status": "Готов к работе",
            "progress": "Ожидание запуска сканирования",
            "csv_content": None
        }
        
        logger.info("GTINScanner Final инициализирован")
        
    def load_pdf_preview(self, pdf_file):
        """Загрузка первой страницы PDF для выбора области"""
        logger.info(f"load_pdf_preview вызвана с файлом: {pdf_file}")
        
        if pdf_file is None:
            logger.warning("PDF файл не предоставлен")
            return None, "⚠️ Пожалуйста, загрузите PDF файл"
        
        try:
            self.pdf_path = pdf_file.name
            logger.info(f"Открываем PDF: {self.pdf_path}")
            
            self.pdf_document = fitz.open(self.pdf_path)
            page = self.pdf_document[0]
            logger.info(f"Первая страница загружена")
            
            # Рендерим первую страницу с высоким разрешением для превью
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            logger.info(f"Страница отрендерена: {pix.width}x{pix.height}")
            
            # Конвертируем в PIL Image
            img_data = pix.tobytes("png")
            self.preview_image = Image.open(io.BytesIO(img_data))
            logger.info(f"PIL Image создан: {self.preview_image.size}")
            
            total_pages = len(self.pdf_document)
            message = f"✅ PDF загружен: {Path(self.pdf_path).name}\n📄 Страниц: {total_pages}\n\n⚠️ Для больших файлов рекомендуется сначала протестировать на первых 10-50 страницах\n🖱️ Кликните дважды на изображении выше для выделения области с Data Matrix кодом"
            
            logger.info(f"PDF успешно загружен: {total_pages} страниц")
            return self.preview_image, message
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке PDF: {str(e)}", exc_info=True)
            return None, f"❌ Ошибка при загрузке PDF: {str(e)}"
    
    def handle_image_click(self, evt: gr.SelectData):
        """Обработка клика по изображению"""
        logger.info(f"handle_image_click вызвана с данными: {evt}")
        
        if self.preview_image is None:
            logger.warning("Превью изображение не загружено")
            return "⚠️ Сначала загрузите PDF файл"
        
        x, y = evt.index[0], evt.index[1]
        logger.info(f"Клик по координатам: ({x}, {y})")
        
        if self.selection_start is None:
            # Первый клик - начало выделения
            self.selection_start = (x, y)
            logger.info(f"Начальная точка установлена: {self.selection_start}")
            return f"📍 Начальная точка: ({x}, {y})\n🖱️ Нажмите еще раз, чтобы завершить выделение"
        else:
            # Второй клик - завершение выделения
            self.selection_end = (x, y)
            logger.info(f"Конечная точка установлена: {self.selection_end}")
            
            # Определяем координаты прямоугольника
            x1 = min(self.selection_start[0], self.selection_end[0])
            y1 = min(self.selection_start[1], self.selection_end[1])
            x2 = max(self.selection_start[0], self.selection_end[0])
            y2 = max(self.selection_start[1], self.selection_end[1])
            
            # Сохраняем координаты
            self.crop_rect = (x1, y1, x2, y2)
            logger.info(f"Область обрезки установлена: {self.crop_rect}")
            
            width = x2 - x1
            height = y2 - y1
            
            # Сбрасываем выделение для следующего раза
            self.selection_start = None
            self.selection_end = None
            
            result_msg = f"✅ Область выбрана: {width}x{height} px\n📍 Координаты: ({x1},{y1}) - ({x2},{y2})\n\n▶️ Теперь нажмите 'Начать сканирование'"
            logger.info(f"Область успешно выбрана: {width}x{height}")
            return result_msg
    
    def scan_pdf_with_progress(self, max_pages=None):
        """Сканирование PDF с прогрессом"""
        logger.info("scan_pdf_with_progress начато")
        
        if self.pdf_document is None:
            logger.warning("PDF документ не загружен")
            self.scan_results["status"] = "❌ PDF файл не загружен"
            self.scan_results["progress"] = "Загрузите PDF файл"
            return "❌ PDF файл не загружен", None, "Загрузите PDF файл"
        
        if self.crop_rect is None:
            logger.warning("Область обрезки не выбрана")
            self.scan_results["status"] = "❌ Область не выбрана"
            self.scan_results["progress"] = "Выделите область с Data Matrix кодом кликом мыши"
            return "❌ Область не выбрана", None, "Выделите область с Data Matrix кодом кликом мыши"
        
        if self.scanning:
            return "⚠️ Сканирование уже выполняется", None, "Дождитесь завершения текущего сканирования"
        
        # Запускаем сканирование в отдельном потоке
        self.scanning = True
        self.stop_requested = False
        self.scan_results["status"] = "🔄 Сканирование запущено..."
        self.scan_results["progress"] = "Инициализация..."
        
        def scan_thread():
            try:
                all_codes = []
                total_pages = len(self.pdf_document)
                
                # Ограничиваем количество страниц для тестирования
                if max_pages and max_pages > 0:
                    total_pages = min(total_pages, max_pages)
                
                logger.info(f"Начинаем сканирование {total_pages} страниц с областью: {self.crop_rect}")
                
                start_time = time.time()
                
                for page_num in range(total_pages):
                    if self.stop_requested:
                        logger.info(f"Сканирование остановлено пользователем на странице {page_num}")
                        break
                    
                    page_start_time = time.time()
                    logger.info(f"Обрабатываем страницу {page_num + 1}/{total_pages}")
                    
                    # Обновляем прогресс
                    self.scan_results["progress"] = f"Обработка страницы {page_num + 1}/{total_pages} | Найдено кодов: {len(all_codes)}"
                    
                    # Получаем страницу
                    page = self.pdf_document[page_num]
                    
                    # Рендерим страницу с ОПТИМАЛЬНЫМ разрешением для Data Matrix
                    mat = fitz.Matrix(3.0, 3.0)  # Увеличили разрешение для лучшего распознавания
                    pix = page.get_pixmap(matrix=mat)
                    logger.debug(f"Страница {page_num + 1} отрендерена: {pix.width}x{pix.height}")
                    
                    # Конвертируем в PIL Image
                    img_data = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_data))
                    logger.debug(f"PIL Image для страницы {page_num + 1}: {image.size}")
                    
                    # Обрезаем по выделенной области (с учетом масштаба)
                    scale = 3.0 / 2.0  # соотношение масштабов рендеринга и превью
                    crop_x1 = int(self.crop_rect[0] * scale)
                    crop_y1 = int(self.crop_rect[1] * scale)
                    crop_x2 = int(self.crop_rect[2] * scale)
                    crop_y2 = int(self.crop_rect[3] * scale)
                    
                    logger.debug(f"Область обрезки с масштабом: ({crop_x1},{crop_y1}) - ({crop_x2},{crop_y2})")
                    
                    # Проверяем, что область обрезки не выходит за границы изображения
                    img_width, img_height = image.size
                    if crop_x2 > img_width or crop_y2 > img_height:
                        logger.warning(f"Область обрезки выходит за границы изображения: {img_width}x{img_height}")
                        crop_x2 = min(crop_x2, img_width)
                        crop_y2 = min(crop_y2, img_height)
                    
                    cropped_image = image.crop((crop_x1, crop_y1, crop_x2, crop_y2))
                    logger.debug(f"Обрезанное изображение: {cropped_image.size}")
                    
                    # Оптимизируем изображение для лучшего распознавания Data Matrix
                    cropped_image = self._optimize_for_datamatrix(cropped_image)
                    
                    # Распознаём data matrix коды
                    try:
                        decode_start = time.time()
                        decoded_objects = decode(cropped_image)
                        decode_time = time.time() - decode_start
                        
                        logger.info(f"На странице {page_num + 1} найдено {len(decoded_objects)} объектов за {decode_time:.2f}с")
                        
                        for i, obj in enumerate(decoded_objects):
                            try:
                                code_data = obj.data.decode('utf-8')
                                all_codes.append(code_data)
                                logger.info(f"Код {i+1} на странице {page_num + 1}: {code_data}")
                            except UnicodeDecodeError:
                                code_data = obj.data.decode('latin-1')
                                all_codes.append(code_data)
                                logger.info(f"Код {i+1} на странице {page_num + 1} (latin-1): {code_data}")
                                
                    except Exception as decode_error:
                        logger.error(f"Ошибка при декодировании на странице {page_num + 1}: {decode_error}")
                    
                    page_time = time.time() - page_start_time
                    logger.info(f"Страница {page_num + 1} обработана за {page_time:.2f}с")
                
                total_time = time.time() - start_time
                logger.info(f"Сканирование завершено за {total_time:.2f}с. Найдено {len(all_codes)} кодов")
                
                # Генерируем CSV файл
                if all_codes:
                    try:
                        csv_content = self._generate_csv(all_codes)
                        logger.info(f"CSV файл создан, размер: {len(csv_content)} байт")
                        
                        self.scan_results.update({
                            "status": f"✅ Сканирование завершено за {total_time:.1f}с!\n📄 Страниц обработано: {total_pages}\n✅ Найдено кодов: {len(all_codes)}\n💾 Файл готов к скачиванию",
                            "progress": f"Завершено: {total_pages}/{total_pages} | Кодов: {len(all_codes)} | Время: {total_time:.1f}с",
                            "csv_content": csv_content
                        })
                        
                    except Exception as csv_error:
                        logger.error(f"Ошибка при создании CSV: {csv_error}", exc_info=True)
                        self.scan_results.update({
                            "status": f"❌ Ошибка при создании CSV: {str(csv_error)}\n📄 Страниц обработано: {total_pages}\n✅ Найдено кодов: {len(all_codes)}",
                            "progress": "Ошибка при сохранении результатов",
                            "csv_content": None
                        })
                else:
                    logger.warning("Коды не найдены")
                    self.scan_results.update({
                        "status": "⚠️ Коды не найдены в выделенной области",
                        "progress": "Проверьте выделенную область",
                        "csv_content": None
                    })
                
            except Exception as e:
                logger.error(f"Критическая ошибка при сканировании: {e}", exc_info=True)
                self.scan_results.update({
                    "status": f"❌ Ошибка при сканировании: {str(e)}",
                    "progress": "Ошибка",
                    "csv_content": None
                })
            finally:
                self.scanning = False
        
        # Запускаем поток
        thread = threading.Thread(target=scan_thread, daemon=True)
        thread.start()
        
        return "🔄 Сканирование запущено в фоновом режиме", None, "Сканирование начато..."
    
    def get_current_status(self):
        """Получение текущего статуса"""
        return self.scan_results["status"], self.scan_results["progress"], self.scan_results["csv_content"]
    
    def _optimize_for_datamatrix(self, image):
        """Оптимизация изображения для лучшего распознавания Data Matrix"""
        try:
            # Конвертируем в grayscale если нужно
            if image.mode != 'L':
                image = image.convert('L')
            
            # Увеличиваем контрастность
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)  # Увеличиваем контраст в 2 раза
            
            # Увеличиваем резкость
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)  # Увеличиваем резкость в 2 раза
            
            logger.debug("Изображение оптимизировано для Data Matrix")
            return image
            
        except Exception as e:
            logger.warning(f"Ошибка при оптимизации изображения: {e}")
            return image
    
    def _generate_csv(self, codes):
        """Генерация CSV файла"""
        logger.info(f"Генерируем CSV для {len(codes)} кодов")
        
        # Создаем временный файл
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        
        # Используем QUOTE_NONE чтобы избежать кавычек
        writer = csv.writer(temp_file, quoting=csv.QUOTE_NONE, escapechar='\\')
        
        for i, code in enumerate(codes):
            # Очищаем код от специальных символов для безопасности
            clean_code = code.strip().replace('\n', '').replace('\r', '')
            writer.writerow([clean_code])
            logger.debug(f"Записан код {i+1}: {clean_code}")
        
        temp_file.close()
        
        logger.info(f"CSV файл создан: {temp_file.name}")
        return temp_file.name
    
    def stop_scan(self):
        """Остановка сканирования"""
        logger.info("Запрос на остановку сканирования")
        self.stop_requested = True
        self.scan_results["status"] = "⏹ Запрос на остановку отправлен..."
        return "⏹ Запрос на остановку отправлен...", "Остановка...", None


# Создаем экземпляр сканера
scanner = GTINScanner()
logger.info("GTIN Scanner Final приложение запущено")


# Создаем интерфейс Gradio
with gr.Blocks(title="GTIN Scanner Final", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # ⚡ GTIN Scanner Final - Быстрое извлечение Data Matrix кодов из PDF
    
    ### Инструкция:
    1. **Загрузите PDF файл** в поле ниже
    2. **Выделите область с Data Matrix кодом** кликом мыши на изображении
    3. **Выберите количество страниц** для сканирования (для больших файлов)
    4. **Нажмите "Начать сканирование"** для обработки страниц
    5. **Скачайте результат** в формате CSV
    
    ### Особенности:
    - ✅ Простой и надежный интерфейс
    - ✅ Возможность ограничить количество страниц
    - ✅ Фоновое сканирование без блокировки интерфейса
    - ✅ Подробное логирование времени выполнения
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            # Загрузка PDF
            pdf_input = gr.File(
                label="📁 Загрузите PDF файл",
                file_types=[".pdf"],
                type="filepath"
            )
            
            # Превью с возможностью клика
            preview_image = gr.Image(
                label="",
                height=600,
                interactive=True
            )
            
            load_status = gr.Textbox(
                label="📝 Статус",
                value="Ожидание загрузки PDF...",
                lines=3
            )
        
        with gr.Column(scale=1):
            # Статус выделения
            gr.Markdown("### 🎯 Выделение области")
            
            selection_status = gr.Textbox(
                label="Статус выделения",
                value="Кликните дважды на изображении для выделения области",
                lines=4
            )
            
            # Настройки сканирования
            gr.Markdown("### ⚙️ Настройки сканирования")
            
            max_pages_input = gr.Number(
                label="Максимум страниц (0 = все)",
                value=50,
                minimum=0,
                maximum=10000,
                step=1
            )
            
            # Кнопки управления сканированием
            gr.Markdown("### ▶️ Управление сканированием")
            
            scan_btn = gr.Button(
                "⚡ Начать сканирование",
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
    
    preview_image.select(
        fn=scanner.handle_image_click,
        outputs=[selection_status]
    )
    
    scan_btn.click(
        fn=scanner.scan_pdf_with_progress,
        inputs=[max_pages_input],
        outputs=[scan_status, csv_output, stats_display]
    )
    
    stop_btn.click(
        fn=scanner.stop_scan,
        outputs=[scan_status, stats_display, csv_output]
    )
    
    # Кнопка для обновления статуса
    refresh_btn = gr.Button("🔄 Обновить статус", variant="secondary")
    refresh_btn.click(
        fn=scanner.get_current_status,
        outputs=[scan_status, stats_display, csv_output]
    )
    
    gr.Markdown("""
    ---
    **💡 Как выделить область:**
    1. Загрузите PDF и посмотрите на превью
    2. Найдите Data Matrix код на изображении
    3. **Первый клик** - начальная точка (левый верхний угол)
    4. **Второй клик** - конечная точка (правый нижний угол)
    5. Область будет автоматически определена как прямоугольник между этими точками
    6. Выберите количество страниц для сканирования
    7. Запустите сканирование
    
    **⚡ Оптимизации скорости:**
    - Увеличено разрешение рендеринга (3x)
    - Оптимизация контрастности и резкости
    - Фоновое сканирование
    - Возможность ограничить количество страниц для тестирования
    
    **🔄 Для обновления статуса:** Нажмите кнопку "Обновить статус" во время сканирования
    """)


if __name__ == "__main__":
    print("⚡ Запуск GTIN Scanner Final...")
    print("📱 Приложение откроется в браузере")
    print("📝 Логи записываются в файл gtin_scanner_final.log")
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True
    )