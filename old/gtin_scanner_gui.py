#!/usr/bin/env python3
"""
GUI приложение для извлечения GTIN data matrix кодов из PDF файлов
"""

import sys
import csv
import threading
from pathlib import Path
from tkinter import Tk, filedialog, messagebox, Canvas, Button, Label, Frame, StringVar, IntVar
from tkinter.ttk import Progressbar
from PIL import Image, ImageTk, ImageDraw
import io

try:
    import fitz  # PyMuPDF
    from pylibdmtx.pylibdmtx import decode
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("\nУстановите необходимые библиотеки:")
    print("pip install PyMuPDF pylibdmtx Pillow")
    sys.exit(1)


class GTINScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GTIN Scanner - Извлечение Data Matrix кодов из PDF")
        self.root.geometry("900x700")
        
        # Переменные состояния
        self.pdf_path = None
        self.pdf_document = None
        self.crop_rect = None
        self.scanning = False
        self.stop_requested = False
        
        # Переменные для выделения области
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.preview_image = None
        self.preview_photo = None
        self.scale_factor = 1.0
        
        # Создаем интерфейс
        self.create_widgets()
        
    def create_widgets(self):
        # Верхняя панель с кнопками
        top_frame = Frame(self.root)
        top_frame.pack(pady=10, padx=10, fill='x')
        
        self.select_btn = Button(top_frame, text="📁 Выбрать PDF файл", 
                                 command=self.select_pdf, font=('Arial', 12))
        self.select_btn.pack(side='left', padx=5)
        
        self.file_label = Label(top_frame, text="Файл не выбран", 
                               font=('Arial', 10), fg='gray')
        self.file_label.pack(side='left', padx=10)
        
        # Инструкции
        instruction_frame = Frame(self.root)
        instruction_frame.pack(pady=5)
        
        self.instruction_label = Label(instruction_frame, 
                                      text="1. Выберите PDF файл\n2. Выделите область с QR кодом на превью первой страницы\n3. Нажмите 'Начать сканирование'",
                                      font=('Arial', 10), justify='left', fg='blue')
        self.instruction_label.pack()
        
        # Canvas для отображения превью и выделения области
        canvas_frame = Frame(self.root)
        canvas_frame.pack(pady=10, fill='both', expand=True)
        
        self.canvas = Canvas(canvas_frame, bg='lightgray', cursor='cross')
        self.canvas.pack(fill='both', expand=True, padx=10)
        
        # Привязываем события мыши для выделения области
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        
        # Информация о выделенной области
        self.crop_info_label = Label(self.root, text="Выделите область с QR кодом", 
                                     font=('Arial', 9), fg='darkgreen')
        self.crop_info_label.pack(pady=5)
        
        # Кнопки управления сканированием
        control_frame = Frame(self.root)
        control_frame.pack(pady=10)
        
        self.scan_btn = Button(control_frame, text="▶️ Начать сканирование", 
                              command=self.start_scanning, font=('Arial', 12),
                              state='disabled', bg='lightgreen')
        self.scan_btn.pack(side='left', padx=5)
        
        self.stop_btn = Button(control_frame, text="⏹ Остановить", 
                              command=self.stop_scanning, font=('Arial', 12),
                              state='disabled', bg='lightcoral')
        self.stop_btn.pack(side='left', padx=5)
        
        # Прогресс бар и статистика
        progress_frame = Frame(self.root)
        progress_frame.pack(pady=10, padx=10, fill='x')
        
        self.progress_label = Label(progress_frame, text="Готов к работе", 
                                   font=('Arial', 10))
        self.progress_label.pack()
        
        self.progress_bar = Progressbar(progress_frame, length=800, mode='determinate')
        self.progress_bar.pack(pady=5)
        
        self.stats_label = Label(progress_frame, 
                                text="Страниц: 0/0 | Найдено кодов: 0", 
                                font=('Arial', 10), fg='blue')
        self.stats_label.pack(pady=5)
        
    def select_pdf(self):
        """Выбор PDF файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите PDF файл",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.pdf_path = file_path
            self.file_label.config(text=Path(file_path).name, fg='black')
            self.load_preview()
            
    def load_preview(self):
        """Загрузка превью первой страницы"""
        try:
            self.pdf_document = fitz.open(self.pdf_path)
            page = self.pdf_document[0]
            
            # Рендерим первую страницу
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            
            # Конвертируем в PIL Image
            img_data = pix.tobytes("png")
            self.preview_image = Image.open(io.BytesIO(img_data))
            
            # Масштабируем для отображения в canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Если canvas еще не отрисован, используем размеры по умолчанию
            if canvas_width <= 1:
                canvas_width = 800
                canvas_height = 600
            
            img_width, img_height = self.preview_image.size
            
            # Вычисляем масштаб для вписывания в canvas
            scale_x = (canvas_width - 20) / img_width
            scale_y = (canvas_height - 20) / img_height
            self.scale_factor = min(scale_x, scale_y, 1.0)
            
            new_width = int(img_width * self.scale_factor)
            new_height = int(img_height * self.scale_factor)
            
            resized_image = self.preview_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.preview_photo = ImageTk.PhotoImage(resized_image)
            
            # Отображаем на canvas
            self.canvas.delete('all')
            self.canvas.create_image(10, 10, anchor='nw', image=self.preview_photo)
            
            self.instruction_label.config(
                text=f"PDF загружен ({len(self.pdf_document)} стр.). Выделите область с QR кодом мышью."
            )
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить PDF:\n{str(e)}")
            
    def on_mouse_down(self, event):
        """Начало выделения области"""
        if self.preview_image and not self.scanning:
            self.start_x = event.x
            self.start_y = event.y
            
    def on_mouse_drag(self, event):
        """Отрисовка прямоугольника при выделении"""
        if self.start_x and self.start_y and not self.scanning:
            # Удаляем предыдущий прямоугольник
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            
            # Рисуем новый прямоугольник
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline='red', width=2
            )
            
    def on_mouse_up(self, event):
        """Завершение выделения области"""
        if self.start_x and self.start_y and not self.scanning:
            # Сохраняем координаты выделенной области
            x1 = min(self.start_x, event.x) - 10  # -10 из-за смещения изображения
            y1 = min(self.start_y, event.y) - 10
            x2 = max(self.start_x, event.x) - 10
            y2 = max(self.start_y, event.y) - 10
            
            # Преобразуем координаты обратно к масштабу оригинального изображения
            orig_x1 = int(x1 / self.scale_factor)
            orig_y1 = int(y1 / self.scale_factor)
            orig_x2 = int(x2 / self.scale_factor)
            orig_y2 = int(y2 / self.scale_factor)
            
            # Проверяем, что область выделена корректно
            if orig_x2 > orig_x1 and orig_y2 > orig_y1:
                self.crop_rect = (orig_x1, orig_y1, orig_x2, orig_y2)
                width = orig_x2 - orig_x1
                height = orig_y2 - orig_y1
                self.crop_info_label.config(
                    text=f"Область выбрана: {width}x{height} px (на исходном изображении)"
                )
                self.scan_btn.config(state='normal')
            else:
                self.crop_rect = None
                self.crop_info_label.config(text="Выделите область с QR кодом")
                self.scan_btn.config(state='disabled')
                
    def start_scanning(self):
        """Запуск сканирования в отдельном потоке"""
        if not self.crop_rect:
            messagebox.showwarning("Предупреждение", "Сначала выделите область с QR кодом")
            return
        
        self.scanning = True
        self.stop_requested = False
        self.scan_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.select_btn.config(state='disabled')
        
        # Запускаем сканирование в отдельном потоке
        thread = threading.Thread(target=self.scan_pdf, daemon=True)
        thread.start()
        
    def stop_scanning(self):
        """Остановка сканирования"""
        self.stop_requested = True
        self.progress_label.config(text="Остановка сканирования...")
        self.stop_btn.config(state='disabled')
        
    def scan_pdf(self):
        """Сканирование PDF файла"""
        all_codes = []
        total_pages = len(self.pdf_document)
        
        try:
            for page_num in range(total_pages):
                if self.stop_requested:
                    self.root.after(0, lambda: self.progress_label.config(
                        text="Сканирование остановлено пользователем"
                    ))
                    break
                
                # Обновляем прогресс
                progress = ((page_num + 1) / total_pages) * 100
                self.root.after(0, lambda p=progress, pn=page_num+1, tp=total_pages, fc=len(all_codes): 
                    self.update_progress(p, pn, tp, fc))
                
                # Получаем страницу
                page = self.pdf_document[page_num]
                
                # Рендерим страницу
                mat = fitz.Matrix(2.5, 2.5)
                pix = page.get_pixmap(matrix=mat)
                
                # Конвертируем в PIL Image
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                
                # Обрезаем по выделенной области (с учетом масштаба)
                scale = 2.5  # Тот же масштаб, что и при рендеринге
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
            
            # Сохраняем результаты
            if not self.stop_requested:
                self.save_results(all_codes)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Ошибка", f"Ошибка при сканировании:\n{str(e)}"
            ))
        finally:
            self.scanning = False
            self.root.after(0, self.reset_ui)
            
    def update_progress(self, progress, current_page, total_pages, found_codes):
        """Обновление прогресс бара и статистики"""
        self.progress_bar['value'] = progress
        self.progress_label.config(
            text=f"Обработка страницы {current_page} из {total_pages} ({progress:.1f}%)"
        )
        self.stats_label.config(
            text=f"Страниц: {current_page}/{total_pages} | Найдено кодов: {found_codes}"
        )
        
    def save_results(self, codes):
        """Сохранение результатов в CSV"""
        if not codes:
            messagebox.showinfo("Информация", "Коды не найдены в выделенной области")
            return
        
        # Предлагаем выбрать место сохранения
        output_path = filedialog.asksaveasfilename(
            title="Сохранить результаты",
            defaultextension=".csv",
            initialfile=f"{Path(self.pdf_path).stem}_extracted.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if output_path:
            try:
                with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                    for code in codes:
                        writer.writerow([code])
                
                messagebox.showinfo(
                    "Успешно", 
                    f"Сохранено {len(codes)} кодов в файл:\n{output_path}"
                )
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
                
    def reset_ui(self):
        """Сброс UI после завершения сканирования"""
        self.scan_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.select_btn.config(state='normal')
        self.progress_bar['value'] = 0
        
        if not self.stop_requested:
            self.progress_label.config(text="Сканирование завершено")


def main():
    root = Tk()
    app = GTINScannerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

