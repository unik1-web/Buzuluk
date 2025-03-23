import fdb
import json
from uuid import uuid4
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog

# Настройки подключения к базе данных
db_path = r'C:\VESYEVENT.GDB'
user = 'SYSDBA'
password = 'masterkey'

def fetch_data(selected_date):
    """Функция для получения данных из базы данных за выбранную дату."""
    try:
        conn = fdb.connect(dsn=db_path, user=user, password=password)
        cursor = conn.cursor()

        # SQL-запрос с фильтром по дате
        query = """
        SELECT DATE_BRUTTO, DATE_TARA, AUTO_TS_NOMER, AUTO_TS_MARKA, FIRMA, BRUTTO, TARA, NETTO, GRUZ_NAME
        FROM EVENTS
        WHERE CAST(DATE_BRUTTO AS DATE) = ?
        """
        cursor.execute(query, (selected_date,))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось подключиться к базе данных: {e}")
        return []

def update_table():
    """Обновление таблицы данными за выбранную дату."""
    selected_date = date_entry.get()
    if not selected_date:
        messagebox.showwarning("Предупреждение", "Выберите дату!")
        return

    # Очистка таблицы перед обновлением
    for row in tree.get_children():
        tree.delete(row)

    # Получение данных из базы данных
    rows = fetch_data(selected_date)
    if not rows:
        messagebox.showinfo("Информация", "Данные за выбранную дату отсутствуют.")
        return

    # Заполнение таблицы данными
    for row in rows:
        tree.insert("", "end", values=row)

def save_to_json():
    """Сохранение данных в JSON-файл."""
    selected_date = date_entry.get()
    if not selected_date:
        messagebox.showwarning("Предупреждение", "Выберите дату!")
        return

    rows = fetch_data(selected_date)
    if not rows:
        messagebox.showinfo("Информация", "Нет данных для сохранения.")
        return

    # Формирование JSON-структуры
    data = {
        "ObjectId": "insert_ObjectId",
        "AccessKey": "insert_AccessKey",
        "WeightControls": []
    }

    for row in rows:
        weight_control = {
            "Id": str(uuid4()),
            "DateBefore": row[0].strftime("%Y-%m-%d %H:%M:%S+05:00") if row[0] else None,
            "DateAfter": row[1].strftime("%Y-%m-%d %H:%M:%S+05:00") if row[1] else None,
            "RegistrationNumber": row[2],
            "GarbageTruckType": None,
            "GarbageTruckBrand": row[3],
            "GarbageTruckModel": None,
            "CompanyName": row[4],
            "CompanyInn": "5612167252",  # Пример значения
            "CompanyKpp": "561101001",   # Пример значения
            "WeightBefore": row[5],
            "WeightAfter": row[6],
            "WeightDriver": 0,
            "Coefficient": 1.0,
            "GarbageWeight": row[7],
            "GarbageType": row[8]
        }
        data["WeightControls"].append(weight_control)

    # Сохранение в JSON-файл
    with open(f'data_{selected_date}.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    messagebox.showinfo("Успех", f"Данные сохранены в файл data_{selected_date}.json")

# Создание основного окна
root = tk.Tk()
root.title("Данные из базы данных")
root.geometry("1000x600")

# Поле для ввода даты
date_label = tk.Label(root, text="Выберите дату (ГГГГ-ММ-ДД):")
date_label.grid(row=0, column=0, padx=10, pady=10)
date_entry = tk.Entry(root)
date_entry.grid(row=0, column=1, padx=10, pady=10)

# Кнопка для обновления таблицы
update_button = tk.Button(root, text="Обновить таблицу", command=update_table)
update_button.grid(row=0, column=2, padx=10, pady=10)

# Кнопка для сохранения в JSON
save_button = tk.Button(root, text="Сохранить в JSON", command=save_to_json)
save_button.grid(row=0, column=3, padx=10, pady=10)

# Таблица для отображения данных
columns = (
    "DATE_BRUTTO", "DATE_TARA", "AUTO_TS_NOMER", "AUTO_TS_MARKA", "FIRMA",
    "BRUTTO", "TARA", "NETTO", "GRUZ_NAME"
)
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

# Настройка заголовков таблицы
for col in columns:
    tree.heading(col, text=col)

# Полосы прокрутки
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
scrollbar.grid(row=1, column=4, sticky="ns")
tree.configure(yscrollcommand=scrollbar.set)

# Запуск основного цикла
root.mainloop()