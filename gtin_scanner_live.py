#!/usr/bin/env python3
"""
GTIN Scanner Live – веб-приложение для извлечения Data Matrix кодов из PDF
"""

import sys
import csv
import io
import time
import threading
import logging
import os
import re
from pathlib import Path
from typing import Optional, Tuple
import queue

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("gtin_scanner_live.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

LOG_LEVEL = os.getenv('GTIN_LOG_LEVEL', 'INFO').upper()
logging.getLogger().setLevel(LOG_LEVEL)

try:
    import gradio as gr
    import fitz  # PyMuPDF
    from pylibdmtx.pylibdmtx import decode
    from PIL import Image, ImageEnhance
except ImportError as e:
    logger.error("Ошибка импорта: %s", e)
    print(f"Ошибка импорта: {e}")
    print("\nУстановите необходимые библиотеки:")
    print("pip install gradio PyMuPDF pylibdmtx Pillow")
    sys.exit(1)


class GTINScanner:
    """Основная логика сканера GTIN."""

    ESCAPE_RE = re.compile(
        r"""\\(x[0-9A-Fa-f]{2}|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8}|['"\/bfnrt])"""
    )

    def __init__(self) -> None:
        self.pdf_document = None
        self.pdf_path: Optional[str] = None
        self.crop_rect: Optional[Tuple[int, int, int, int]] = None
        self.stop_requested = False
        self.preview_image = None
        self.selection_start = None
        self.selection_end = None
        self.scanning = False

        self.progress_queue: "queue.Queue[str]" = queue.Queue()
        self.current_progress = {
            "status": "Готов к работе",
            "current_page": 0,
            "total_pages": 0,
            "found_codes": 0,
            "elapsed_time": 0,
            "current_page_content": "",
            "csv_file": None,
        }

        logger.info("GTINScanner Live инициализирован")

    def load_pdf_preview(self, pdf_file):
        logger.info("load_pdf_preview вызвана с файлом: %s", pdf_file)

        if pdf_file is None:
            logger.warning("PDF файл не предоставлен")
            return None, "⚠️ Пожалуйста, загрузите PDF файл"

        try:
            self.pdf_path = pdf_file.name
            self.pdf_document = fitz.open(self.pdf_path)
            page = self.pdf_document[0]

            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            image_data = pix.tobytes("png")
            self.preview_image = Image.open(io.BytesIO(image_data))

            total_pages = len(self.pdf_document)
            message = (
                f"✅ PDF загружен: {Path(self.pdf_path).name}\n"
                f"📄 Страниц: {total_pages}\n\n"
                "⚠️ Для больших файлов рекомендуется протестировать на первых 10-50 страницах\n"
                "🖱️ Дважды кликните по изображению, чтобы выделить область с Data Matrix (клик на левый верхний угол и правый нижний)"
            )
            return self.preview_image, message
        except Exception as exc:
            logger.error("Ошибка при загрузке PDF: %s", exc, exc_info=True)
            return None, f"❌ Ошибка при загрузке PDF: {exc}"

    def handle_image_click(self, evt: gr.SelectData):
        logger.info("handle_image_click: %s", evt)

        if self.preview_image is None:
            return "⚠️ Сначала загрузите PDF файл"

        x, y = evt.index
        if self.selection_start is None:
            self.selection_start = (x, y)
            return (
                f"📍 Начальная точка: ({x}, {y})\n"
                "🖱️ Нажмите еще раз, чтобы завершить выделение"
            )

        self.selection_end = (x, y)
        x1 = min(self.selection_start[0], self.selection_end[0])
        y1 = min(self.selection_start[1], self.selection_end[1])
        x2 = max(self.selection_start[0], self.selection_end[0])
        y2 = max(self.selection_start[1], self.selection_end[1])
        self.crop_rect = (x1, y1, x2, y2)

        width = x2 - x1
        height = y2 - y1

        self.selection_start = None
        self.selection_end = None

        return (
            f"✅ Область выбрана: {width}x{height} px\n"
            f"📍 Координаты: ({x1},{y1}) - ({x2},{y2})\n\n"
            "▶️ Теперь нажмите 'Начать сканирование'"
        )

    def scan_pdf_with_live_progress(self, max_pages=None):
        logger.info("scan_pdf_with_live_progress запущен")

        if self.pdf_document is None:
            self.current_progress["status"] = "❌ PDF файл не загружен"
            return "❌ PDF файл не загружен", None, "Загрузите PDF файл", gr.update(value=0)

        if self.crop_rect is None:
            self.current_progress["status"] = "❌ Область не выбрана"
            return (
                "❌ Область не выбрана",
                None,
                "Выделите область с Data Matrix кодом кликом мыши",
                gr.update(value=0),
            )

        if self.scanning:
            return (
                "⚠️ Сканирование уже выполняется",
                None,
                "Дождитесь завершения текущего сканирования",
                gr.update(value=0),
            )

        self.scanning = True
        self.stop_requested = False

        def worker():
            try:
                all_codes: list[str] = []
                total_pages = len(self.pdf_document)
                if max_pages and max_pages > 0:
                    total_pages = min(total_pages, int(max_pages))

                start_time = time.time()
                self.current_progress.update(
                    {
                        "status": "🔄 Сканирование запущено...",
                        "current_page": 0,
                        "total_pages": total_pages,
                        "found_codes": 0,
                        "elapsed_time": 0,
                        "current_page_content": "Инициализация...",
                        "csv_file": None,
                    }
                )

                for page_num in range(total_pages):
                    if self.stop_requested:
                        logger.info("Сканирование остановлено на странице %d", page_num)
                        break

                    page_start = time.time()
                    page = self.pdf_document[page_num]
                    mat = fitz.Matrix(3.0, 3.0)
                    pix = page.get_pixmap(matrix=mat)
                    image = Image.open(io.BytesIO(pix.tobytes("png")))

                    scale = 3.0 / 2.0
                    x1 = int(self.crop_rect[0] * scale)
                    y1 = int(self.crop_rect[1] * scale)
                    x2 = int(self.crop_rect[2] * scale)
                    y2 = int(self.crop_rect[3] * scale)
                    width, height = image.size
                    x2 = min(x2, width)
                    y2 = min(y2, height)

                    cropped = image.crop((x1, y1, x2, y2))
                    cropped = self._optimize_for_datamatrix(cropped)

                    try:
                        decoded_objects = decode(cropped)
                    except Exception as decode_error:
                        logger.error(
                            "Ошибка декодирования на странице %d: %s",
                            page_num + 1,
                            decode_error,
                            exc_info=True,
                        )
                        decoded_objects = []

                    page_codes: list[str] = []
                    for idx, obj in enumerate(decoded_objects):
                        raw_bytes = obj.data
                        logger.debug(
                            "Raw decoded bytes (page %d, index %d): %s",
                            page_num + 1,
                            idx,
                            raw_bytes,
                        )
                        try:
                            code_data = raw_bytes.decode("utf-8")
                        except UnicodeDecodeError:
                            code_data = raw_bytes.decode("latin-1")
                        clean_code = self._normalize_code(code_data)
                        if clean_code != code_data:
                            logger.debug(
                                "Normalized code differs (page %d, index %d): '%s' -> '%s'",
                                page_num + 1,
                                idx,
                                code_data,
                                clean_code,
                            )
                        page_codes.append(clean_code)
                        all_codes.append(clean_code)

                    elapsed = time.time() - start_time
                    status = (
                        f"✅ Страница {page_num + 1}/{total_pages} - найдено"
                        f" {len(page_codes)} кодов"
                        if page_codes
                        else f"⚠️ Страница {page_num + 1}/{total_pages} - коды не найдены"
                    )
                    preview = ", ".join(page_codes[:3]) + ("..." if len(page_codes) > 3 else "")
                    self.current_progress.update(
                        {
                            "status": status,
                            "current_page": page_num + 1,
                            "found_codes": len(all_codes),
                            "elapsed_time": elapsed,
                            "current_page_content": (
                                f"Страница {page_num + 1}: {preview}"
                                if page_codes
                                else f"Страница {page_num + 1}: коды не найдены"
                            ),
                        }
                    )
                    logger.info(
                        "Страница %d обработана за %.2fс",
                        page_num + 1,
                        time.time() - page_start,
                    )

                total_time = time.time() - start_time
                if all_codes:
                    csv_file = self._generate_csv(all_codes)
                    self.current_progress.update(
                        {
                            "status": (
                                f"✅ Сканирование завершено за {total_time:.1f}с!\n"
                                f"📄 Страниц обработано: {total_pages}\n"
                                f"✅ Найдено кодов: {len(all_codes)}\n"
                                "💾 Файл готов к скачиванию"
                            ),
                            "csv_file": csv_file,
                            "current_page_content": (
                                f"Всего найдено {len(all_codes)} кодов за {total_time:.1f}с"
                            ),
                        }
                    )
                else:
                    self.current_progress.update(
                        {
                            "status": "⚠️ Коды не найдены в выделенной области",
                            "current_page_content": "Проверьте выделенную область",
                        }
                    )
            except Exception as exc:
                logger.error("Критическая ошибка сканирования: %s", exc, exc_info=True)
                self.current_progress.update(
                    {
                        "status": f"❌ Ошибка при сканировании: {exc}",
                        "current_page_content": "Ошибка",
                    }
                )
            finally:
                self.scanning = False

        threading.Thread(target=worker, daemon=True).start()
        return "🔄 Сканирование запущено в фоновом режиме", None, "Сканирование начато..."

    def get_live_progress(self):
        if self.scanning:
            stats = (
                f"Страниц: {self.current_progress['current_page']}"
                f"/{self.current_progress['total_pages']} | "
                f"Кодов: {self.current_progress['found_codes']} | "
                f"Время: {self.current_progress['elapsed_time']:.1f}с"
            )
            return (
                self.current_progress["status"],
                stats,
                self.current_progress["current_page_content"],
                self.current_progress["csv_file"],
            )
        return (
            self.current_progress["status"],
            "Ожидание запуска сканирования",
            "Готов к работе",
            self.current_progress["csv_file"],
        )

    def _optimize_for_datamatrix(self, image: Image.Image) -> Image.Image:
        try:
            if image.mode != "L":
                image = image.convert("L")
            image = ImageEnhance.Contrast(image).enhance(2.0)
            image = ImageEnhance.Sharpness(image).enhance(2.0)
            return image
        except Exception as exc:
            logger.warning("Ошибка при оптимизации изображения: %s", exc)
            return image

    def _normalize_code(self, raw: str) -> str:
        s = raw.replace("\n", "").replace("\r", "")
        translation = str.maketrans(
            {
                "\u201c": '"',
                "\u201d": '"',
                "\u201e": '"',
                "\u201f": '"',
                "\u2018": "'",
                "\u2019": "'",
                "\u201a": "'",
                "\u201b": "'",
            }
        )
        s = s.translate(translation)

        def _replace(match: re.Match[str]) -> str:
            token = match.group(1)
            mapping = {
                '"': '"',
                "'": "'",
                "\\": "\\",
                "/": "/",
                "n": "",
                "r": "",
                "t": " ",
                "b": "",
                "f": "",
            }
            if token in mapping:
                return mapping[token]
            if token.startswith("x"):
                return chr(int(token[1:], 16))
            if token.startswith(("u", "U")):
                return chr(int(token[1:], 16))
            return match.group(0)

        s = self.ESCAPE_RE.sub(_replace, s)
        if "\x1d" not in s:
            marker_index = s.find("93")
            if marker_index != -1:
                s = f"{s[:marker_index]}\x1d{s[marker_index:]}"
                logger.debug("Inserted GS separator before crypto tail: %s", s)
        s = "".join(ch for ch in s if ord(ch) >= 32 or ch == "\x1d")
        return s

    def _generate_csv(self, codes: list[str]) -> str:
        import tempfile

        temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            suffix=".csv",
            delete=False,
            encoding="utf-8",
        )
        for code in codes:
            clean_code = self._normalize_code(code)
            temp_file.write(clean_code + "\n")
        temp_file.close()
        return temp_file.name

    def stop_scan(self):
        self.stop_requested = True
        self.current_progress["status"] = "⏹ Запрос на остановку отправлен..."
        return "⏹ Запрос на остановку отправлен...", "Остановка...", "Остановка сканирования...", None


scanner = GTINScanner()
logger.info("GTIN Scanner Live приложение запущено")

with gr.Blocks(title="GTIN Scanner Live") as app:
    gr.Markdown(
        """
        # ⚡ GTIN Scanner Live
        1. Загрузите PDF файл.
        2. Дважды кликните по превью, чтобы выделить область.
        3. Нажмите "Начать сканирование" и дождитесь результата.
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            pdf_input = gr.File(label="📁 Загрузите PDF файл", file_types=[".pdf"], type="filepath")
            preview_image = gr.Image(label="", height=600, interactive=True)
            load_status = gr.Textbox(label="📝 Статус", value="Ожидание загрузки PDF...", lines=3)
        with gr.Column(scale=1):
            selection_status = gr.Textbox(
                label="Статус выделения",
                value="Кликните дважды на изображении для выделения области",
                lines=4,
            )
            max_pages_input = gr.Number(
                label="Максимум страниц (0 = все)", value=50, minimum=0, maximum=10000, step=1
            )
            scan_btn = gr.Button("⚡ Начать сканирование", variant="primary")
            stop_btn = gr.Button("⏹ Остановить", variant="stop")
            stats_display = gr.Textbox(label="Статистика", value="Готов к работе", lines=2)
            scan_status = gr.Textbox(label="Детали сканирования", value="", lines=3)
            current_page_display = gr.Textbox(label="Текущая страница", value="", lines=2)
            csv_output = gr.File(label="Скачать CSV файл", visible=True)

    pdf_input.change(fn=scanner.load_pdf_preview, inputs=[pdf_input], outputs=[preview_image, load_status])
    preview_image.select(fn=scanner.handle_image_click, outputs=[selection_status])
    scan_btn.click(
        fn=scanner.scan_pdf_with_live_progress,
        inputs=[max_pages_input],
        outputs=[scan_status, csv_output, stats_display],
    )
    stop_btn.click(
        fn=scanner.stop_scan,
        outputs=[scan_status, stats_display, current_page_display, csv_output],
    )

    timer = gr.Timer(value=2)
    timer.tick(
        fn=scanner.get_live_progress,
        outputs=[scan_status, stats_display, current_page_display, csv_output],
    )

if __name__ == "__main__":
    print("⚡ Запуск GTIN Scanner Live...")
    print("📱 Приложение откроется в браузере")
    print("📝 Логи записываются в файл gtin_scanner_live.log")
    app.launch(server_name="127.0.0.1", server_port=7860, share=False, inbrowser=True)
