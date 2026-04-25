import tkinter as tk
from tkinter import ttk, messagebox
import json
import re
from datetime import datetime

# --- Настройки ---
DATA_FILE = "data.json"
DATE_FORMAT = "%d.%m.%Y"
DATE_REGEX = r"^\d{2}\.\d{2}\.\d{4}$"  # Формат ДД.ММ.ГГГГ

class TrainingPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x500")

        # Загрузка данных из JSON
        self.data = self.load_data()

        # --- Виджеты ---
        # Поля ввода
        ttk.Label(root, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.date_entry = ttk.Entry(root, width=15)
        self.date_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(root, text="Тип тренировки:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.type_entry = ttk.Entry(root, width=15)
        self.type_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(root, text="Длительность (мин):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.duration_entry = ttk.Entry(root, width=15)
        self.duration_entry.grid(row=2, column=1, padx=10, pady=5)

        # Кнопка добавления
        self.add_btn = ttk.Button(root, text="Добавить тренировку", command=self.add_training)
        self.add_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # Таблица для отображения тренировок
        self.columns = ("date", "type", "duration")
        self.tree = ttk.Treeview(root, columns=self.columns, show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип")
        self.tree.heading("duration", text="Длительность (мин)")
        
        self.tree.column("date", width=120)
        self.tree.column("type", width=200)
        self.tree.column("duration", width=120)
        
        self.tree.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

        # Фильтрация по типу
        ttk.Label(root, text="Фильтр по типу:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        
        # Получаем уникальные типы из данных + пустое значение для сброса фильтра
        types = sorted({item["type"] for item in self.data})
        types.insert(0, "") 
        
        self.filter_type_var = tk.StringVar()
        self.filter_type_combo = ttk.Combobox(root, values=types,
                                              textvariable=self.filter_type_var,
                                              state="readonly", width=15)
        self.filter_type_combo.current(0)  # Выбираем первый (пустой)
        self.filter_type_combo.grid(row=5, column=1, padx=10, pady=5)

        # Фильтрация по дате
        ttk.Label(root, text="Фильтр по дате:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        
        self.filter_date_entry = ttk.Entry(root, width=15)
        self.filter_date_entry.grid(row=6, column=1, padx=10, pady=5)

        self.filter_date_btn = ttk.Button(root, text="Фильтровать", command=self.apply_filters)
        self.filter_date_btn.grid(row=6, column=2, padx=5)

        # Кнопка сброса фильтров
        self.reset_btn = ttk.Button(root, text="Сбросить фильтры", command=self.reset_filters)
        self.reset_btn.grid(row=7, column=0, columnspan=3)

        # Настройка сетки для растягивания таблицы
        root.grid_rowconfigure(4, weight=1)
        root.grid_columnconfigure(2, weight=1)

    def load_data(self):
         """Загрузка данных из файла JSON."""
         try:
             with open(DATA_FILE, "r", encoding="utf-8") as f:
                 return json.load(f)
         except (FileNotFoundError, json.JSONDecodeError):
             return []

    def save_data(self):
         """Сохранение данных в файл JSON."""
         with open(DATA_FILE, "w", encoding="utf-8") as f:
             json.dump(self.data, f, ensure_ascii=False, indent=4)

    def update_treeview(self):
         """Обновление содержимого таблицы."""
         for i in self.tree.get_children():
             self.tree.delete(i)
         for item in self.data:
             self.tree.insert("", "end", values=(item["date"], item["type"], item["duration"]))

    def validate_input(self):
         """Проверка корректности введённых данных."""
         date = self.date_entry.get().strip()
         tr_type = self.type_entry.get().strip()
         duration = self.duration_entry.get().strip()

         if not date or not tr_type or not duration:
             messagebox.showerror("Ошибка", "Все поля должны быть заполнены.")
             return False

         if not re.match(DATE_REGEX, date):
             messagebox.showerror("Ошибка", "Дата должна быть в формате ДД.ММ.ГГГГ.")
             return False

         try:
             datetime.strptime(date, DATE_FORMAT)  # Проверка на реальную дату (например 32.13.2026)
         except ValueError:
             messagebox.showerror("Ошибка", "Введена некорректная дата.")
             return False

         if not duration.isdigit() or int(duration) <= 0:
             messagebox.showerror("Ошибка", "Длительность должна быть положительным целым числом.")
             return False

         return True

    def add_training(self):
         """Обработчик кнопки 'Добавить тренировку'."""
         if not self.validate_input():
             return

         new_item = {
             "date": self.date_entry.get().strip(),
             "type": self.type_entry.get().strip(),
             "duration": int(self.duration_entry.get().strip())
         }

         self.data.append(new_item)
         self.save_data()
         self.update_treeview()

         # Очистка полей после добавления
         self.date_entry.delete(0, tk.END)
         self.type_entry.delete(0, tk.END)
         self.duration_entry.delete(0, tk.END)

    def apply_filters(self):
         """Применение фильтров по типу и дате."""
         filtered_data = self.data.copy()

         # Фильтр по типу
         filter_type = self.filter_type_var.get()
         if filter_type:
             filtered_data = [item for item in filtered_data if item["type"] == filter_type]

         # Фильтр по дате
         filter_date = self.filter_date_entry.get().strip()
         if filter_date:
             if not re.match(DATE_REGEX, filter_date):
                 messagebox.showerror("Ошибка", "Дата для фильтра должна быть в формате ДД.ММ.ГГГГ.")
                 return
             filtered_data = [item for item in filtered_data if item["date"] == filter_date]

         # Временно заменяем данные для отображения и обновляем таблицу
         temp_data = self.data
         self.data = filtered_data
         self.update_treeview()
         
    def reset_filters(self):
         """Сброс фильтров и отображение всех данных."""
         self.filter_type_var.set("")
         self.filter_date_entry.delete(0, tk.END)
         
          # Восстанавливаем исходный список данных и обновляем таблицу
          self.data = self.load_data()
          self.update_treeview()


if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlannerApp(root)
    app.update_treeview()  # Загрузка данных при старте приложения
    root.mainloop()
