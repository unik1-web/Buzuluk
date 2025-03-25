# -*- coding: utf-8 -*-
import sys
import locale

# Установка локали
locale.setlocale(locale.LC_ALL, 'Russian_Russia.1251')

# Вывод информации о кодировках
print("Кодировка консоли:", sys.stdout.encoding)
print("Кодировка файловой системы:", sys.getfilesystemencoding())
print("Текущая локаль:", locale.getlocale())
print("Тестовая русская строка: Проверка кодировки") 