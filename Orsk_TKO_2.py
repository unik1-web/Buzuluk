import tkinter as tk
from tkinter import ttk
import pyfirebirdsql

# Подключение к базе данных
def connect_to_db():
    conn = pyfirebirdsql.connect(
        host='localhost',
        database='C:/Program Files (x86)/Vescom/Database/STATICTRUCKSCALE.fdb',
        user='sysdba',
        password='masterkey'
    )
    return conn

# Функция для получения данных из базы данных
def fetch_data(date):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM your_table_name WHERE Дата_проверки_брутто = '{date}'")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Функция для обновления таблицы
def update_table():
    selected_date = date_entry.get()
    for row in tree.get_children():
        tree.delete(row)
    rows = fetch_data(selected_date)
    for row in rows:
        tree.insert("", "end", values=row)

# Создание основного окна
root = tk.Tk()
root.title("Репозильный экологический оператор")

# Поле для ввода даты
date_label = tk.Label(root, text="Дата проверки брутто:")
date_label.grid(row=0, column=0, padx=10, pady=10)
date_entry = tk.Entry(root)
date_entry.grid(row=0, column=1, padx=10, pady=10)

# Кнопка для обновления данных
update_button = tk.Button(root, text="Обновить", command='weighings')
update_button.grid(row=0, column=2, padx=10, pady=10)

# Создание таблицы
columns = ("Дата проверки брутто", "Дата проверки тары", "№ авто", "Марка авто", "Брутто", "Тара", "Нетто", "Отправитель", "ИНН", "КПП", "Род груза", "Статус отправки в РЭО", "Дата отправки в РЭО")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
tree.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

# Запуск основного цикла
root.mainloop()