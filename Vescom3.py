import tkinter as tk
from tkinter import ttk
import fdb
from tkcalendar import Calendar

# Подключение к базе данных
def connect_to_db():
    conn = fdb.connect(
        dsn='STATICTRUCKSCALE.fdb',
        user='sysdba',
        password='masterkey',
        charset='UTF8'  # Указываем кодировку UTF-8
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
            PRODUCT, 
            CAR_MARKA
        FROM 
            WEIGHINGS
        WHERE 
            CAST(BRUTTO_DT AS DATE) = ?  -- Используем CAST для преобразования TIMESTAMP в DATE
    """
    cursor.execute(query, (date,))  # Используем параметризованный запрос
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
        # Форматируем значения "Брутто", "Тара" и "Нетто" с двумя знаками после запятой
        formatted_row = list(row)
        formatted_row[2] = "{:.2f}".format(row[2])  # Брутто
        formatted_row[3] = "{:.2f}".format(row[3])  # Тара
        formatted_row[4] = "{:.2f}".format(row[4])  # Нетто
        tree.insert("", "end", values=formatted_row)

# Функция для открытия календаря
def open_calendar():
    def set_date():
        date_entry.delete(0, tk.END)
        date_entry.insert(0, cal.get_date())
        top.destroy()

    top = tk.Toplevel(root)
    cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
    cal.pack(padx=10, pady=10)
    tk.Button(top, text="Выбрать дату", command=set_date).pack(pady=10)

# Создание основного окна
root = tk.Tk()
root.title("Репозильный экологический оператор")
root.geometry("800x600")  # Устанавливаем начальный размер окна

# Поле для ввода даты
date_frame = tk.Frame(root)
date_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

date_label = tk.Label(date_frame, text="Дата проверки брутто:")
date_label.pack(side=tk.LEFT, padx=5, pady=5)

date_entry = tk.Entry(date_frame)
date_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

calendar_button = tk.Button(date_frame, text="Календарь", command=open_calendar)
calendar_button.pack(side=tk.LEFT, padx=5, pady=5)

# Кнопка для обновления данных
update_button = tk.Button(root, text="Обновить", command=update_table)
update_button.grid(row=0, column=1, padx=5, pady=5, sticky="e")

# Создание таблицы
columns = (
    "№ авто",
    "№ прицепа",
    "Брутто",
    "Тара",
    "Нетто",
    "Дата взвешивания брутто",
    "Дата взвешивания тары",
    "Отправитель",
    "Груз",
    "Марка авто"
)
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)  # Устанавливаем ширину колонок

tree.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

# Настройка изменения размеров окна
root.grid_rowconfigure(1, weight=1)  # Таблица будет растягиваться по вертикали
root.grid_columnconfigure(0, weight=1)  # Таблица будет растягиваться по горизонтали

# Запуск основного цикла
root.mainloop()