import tkinter as tk
from tkinter import ttk, messagebox
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
    # Автоматически настроить ширину колонок
    auto_resize_columns(tree)

# Функция для автоматической настройки ширины колонок
def auto_resize_columns(tree):
    for col in tree["columns"]:
        tree.column(col, width=tk.font.Font().measure(col) + 20)  # Ширина по заголовку
    for row in tree.get_children():
        for i, item in enumerate(tree.item(row)["values"]):
            col_width = tk.font.Font().measure(str(item)) + 20
            if tree.column(tree["columns"][i], width=None) < col_width:
                tree.column(tree["columns"][i], width=col_width)

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

# Функции для меню
def open_settings():
    messagebox.showinfo("Настройки", "Здесь будут настройки приложения.")

def send_data_to_reo():
    messagebox.showinfo("Отправка данных в РЭО", "Данные успешно отправлены в РЭО.")

# Глобальный список для хранения отправителей
senders_list = []

def manage_senders():
    # Окно для управления отправителями
    senders_window = tk.Toplevel(root)
    senders_window.title("Управление отправителями")
    senders_window.geometry("800x400")

    # Таблица отправителей
    columns = ("Наименование отправителя", "ИНН", "КПП", "Отправка в РЭО")
    senders_tree = ttk.Treeview(senders_window, columns=columns, show="headings")
    for col in columns:
        senders_tree.heading(col, text=col)
        senders_tree.column(col, width=150)  # Начальная ширина колонок
    senders_tree.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

    # Поля для ввода данных
    tk.Label(senders_window, text="Наименование:").grid(row=1, column=0, padx=5, pady=5)
    name_entry = tk.Entry(senders_window)
    name_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(senders_window, text="ИНН:").grid(row=2, column=0, padx=5, pady=5)
    inn_entry = tk.Entry(senders_window)
    inn_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(senders_window, text="КПП:").grid(row=3, column=0, padx=5, pady=5)
    kpp_entry = tk.Entry(senders_window)
    kpp_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(senders_window, text="Отправка в РЭО:").grid(row=4, column=0, padx=5, pady=5)
    send_flag = tk.BooleanVar()
    tk.Checkbutton(senders_window, variable=send_flag).grid(row=4, column=1, padx=5, pady=5)

    # Функция для добавления отправителя
    def add_sender():
        name = name_entry.get()
        inn = inn_entry.get()
        kpp = kpp_entry.get()
        flag = send_flag.get()
        if name and inn and kpp:
            senders_list.append((name, inn, kpp, flag))
            senders_tree.insert("", "end", values=(name, inn, kpp, "Да" if flag else "Нет"))
            name_entry.delete(0, tk.END)
            inn_entry.delete(0, tk.END)
            kpp_entry.delete(0, tk.END)
            send_flag.set(False)
            auto_resize_columns(senders_tree)
        else:
            messagebox.showwarning("Ошибка", "Заполните все поля!")

    # Кнопка для добавления отправителя
    tk.Button(senders_window, text="Добавить", command=add_sender).grid(row=5, column=0, columnspan=2, pady=10)

    # Загрузка существующих отправителей в таблицу
    for sender in senders_list:
        senders_tree.insert("", "end", values=sender)

    # Автоматическая настройка ширины колонок
    auto_resize_columns(senders_tree)

# Создание основного окна
root = tk.Tk()
root.title("Региональный экологический оператор")
root.geometry("800x600")  # Устанавливаем начальный размер окна

# Создание меню
menu_bar = tk.Menu(root)

# Меню "Файл"
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Настройки", command=open_settings)
file_menu.add_separator()
file_menu.add_command(label="Выход", command=root.quit)
menu_bar.add_cascade(label="Файл", menu=file_menu)

# Меню "Данные"
data_menu = tk.Menu(menu_bar, tearoff=0)
data_menu.add_command(label="Отправка данных в РЭО", command=send_data_to_reo)
menu_bar.add_cascade(label="Данные", menu=data_menu)

# Меню "Списки"
lists_menu = tk.Menu(menu_bar, tearoff=0)
lists_menu.add_command(label="Отправители", command=manage_senders)
menu_bar.add_cascade(label="Списки", menu=lists_menu)

# Добавление меню в окно
root.config(menu=menu_bar)

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
    tree.column(col, width=100)  # Начальная ширина колонок

tree.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

# Настройка изменения размеров окна
root.grid_rowconfigure(1, weight=1)  # Таблица будет растягиваться по вертикали
root.grid_columnconfigure(0, weight=1)  # Таблица будет растягиваться по горизонтали

# Запуск основного цикла
root.mainloop()