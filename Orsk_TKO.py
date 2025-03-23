# import tkinter as tk
# from tkinter import ttk
# import fdb
#
# # Подключение к базе данных
# def connect_to_db():
#     conn = fdb.connect(
#         dsn='STATICTRUCKSCALE.fdb',
#         user='sysdba',
#         password='masterkey'
#     )
#     return conn
#
# # Функция для получения данных из базы данных
# def fetch_data(date):
#     conn = connect_to_db()
#     cursor = conn.cursor()
#     cursor.execute(f"SELECT * FROM your_table_name WHERE Дата_проверки_брутто = '{date}'")
#     rows = cursor.fetchall()
#     conn.close()
#     return rows
#
# # Функция для обновления таблицы
# def update_table():
#     selected_date = date_entry.get()
#     for row in tree.get_children():
#         tree.delete(row)
#     rows = fetch_data(selected_date)
#     for row in rows:
#         tree.insert("", "end", values=row)
#
# # Создание основного окна
# root = tk.Tk()
# root.title("Репозильный экологический оператор")
#
# # Поле для ввода даты
# date_label = tk.Label(root, text="Дата проверки брутто:")
# date_label.grid(row=0, column=0, padx=5, pady=5)
# date_entry = tk.Entry(root)
# date_entry.grid(row=0, column=1, padx=5, pady=5)
#
# # Кнопка для обновления данных
# update_button = tk.Button(root, text="Обновить", command='weighings')
# update_button.grid(row=0, column=2, padx=5, pady=5)
#
# # Создание таблицы
# columns = ("Дата проверки брутто", "Дата проверки тары", "№ авто", "Марка авто", "Брутто", "Тара", "Нетто", "Отправитель", "ИНН", "КПП", "Род груза", "Статус отправки в РЭО", "Дата отправки в РЭО")
# tree = ttk.Treeview(root, columns=columns, show="headings")
# for col in columns:
#     tree.heading(col, text=col)
# tree.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
#
# # Запуск основного цикла
# root.mainloop()

# import tkinter as tk
# from tkinter import ttk
# import fdb
# from tkcalendar import Calendar
#
# # Подключение к базе данных
# def connect_to_db():
#     conn = fdb.connect(
#         dsn='STATICTRUCKSCALE.fdb',
#         user='sysdba',
#         password='masterkey'
#     )
#     return conn
#
# # Функция для получения данных из базы данных
# def fetch_data(date):
#     conn = connect_to_db()
#     cursor = conn.cursor()
#     cursor.execute(f"SELECT * FROM your_table_name WHERE Дата_проверки_брутто = '{date}'")
#     rows = cursor.fetchall()
#     conn.close()
#     return rows
#
# # Функция для обновления таблицы
# def update_table():
#     selected_date = cal.get_date()
#     for row in tree.get_children():
#         tree.delete(row)
#     rows = fetch_data(selected_date)
#     for row in rows:
#         tree.insert("", "end", values=row)
#
# # Создание основного окна
# root = tk.Tk()
# root.title("Репозильный экологический оператор")
#
# # Календарь для выбора даты
# cal = Calendar(root, selectmode='day', date_pattern='yyyy-mm-dd')
# cal.grid(row=0, column=0, padx=5, pady=5)
#
# # Кнопка для обновления данных
# update_button = tk.Button(root, text="Обновить", command='weighings')
# update_button.grid(row=0, column=1, padx=5, pady=5)
#
# # Создание таблицы
# columns = ("Дата проверки брутто", "Дата проверки тары", "№ авто", "Марка авто", "Брутто", "Тара", "Нетто", "Отправитель", "ИНН", "КПП", "Род груза", "Статус отправки в РЭО", "Дата отправки в РЭО")
# tree = ttk.Treeview(root, columns=columns, show="headings")
# for col in columns:
#     tree.heading(col, text=col)
#     tree.column(col, width=100)  # Устанавливаем ширину колонок
#
# tree.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
#
# # Запуск основного цикла
# root.mainloop()

import tkinter as tk
from tkinter import ttk
import fdb
from tkcalendar import Calendar

# Подключение к базе данных
def connect_to_db():
    conn = fdb.connect(
        dsn='STATICTRUCKSCALE.fdb',
        user='sysdba',
        password='masterkey'
    )
    return conn

# Функция для получения данных из базы данных
def fetch_data(date):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = """
        SELECT 
            CAR_NUMBER, 
            TRAILER_NUMBER, 
            BRUTTO, 
            TARA, 
            NETTO, 
            BRUTTO_DT, 
            TARA_DT, 
            SENDER, 
            RECEIVER, 
            CARRIER, 
            PRODUCT, 
            CAR_MARKA, 
            STATUS, 
            PRICE, 
            COST, 
            PRICE_NDS, 
            COST_NDS, 
            RUBBISH_NUMBER
        FROM 
            WEIGHINGS
        WHERE 
            DATE(BRUTTO_DT) = ?
    """
    cursor.execute(query, (date,))  # Используем параметризованный запрос
    rows = cursor.fetchall()
    conn.close()
    return rows

# Функция для обновления таблицы
def update_table():
    selected_date = cal.get_date()
    for row in tree.get_children():
        tree.delete(row)
    rows = fetch_data(selected_date)
    for row in rows:
        tree.insert("", "end", values=row)

# Создание основного окна
root = tk.Tk()
root.title("Репозильный экологический оператор")

# Календарь для выбора даты
cal = Calendar(root, selectmode='day', date_pattern='yyyy-mm-dd')
cal.grid(row=0, column=0, padx=5, pady=5)

# Кнопка для обновления данных
update_button = tk.Button(root, text="Обновить", command=update_table)
update_button.grid(row=0, column=1, padx=5, pady=5)

# Создание таблицы
columns = (
    "№ авто", "№ прицепа", "Брутто", "Тара", "Нетто",
    "Дата взвешивания брутто", "Дата взвешивания тары",
    "Отправитель", "Получатель", "Перевозчик", "Груз",
    "Марка авто", "Статус", "Цена", "Стоимость",
    "Цена с НДС", "Стоимость с НДС", "Номер мусора"
)
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)  # Устанавливаем ширину колонок

tree.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

# Запуск основного цикла
root.mainloop()