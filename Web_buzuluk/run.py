import os
import sys
import webbrowser
from app import app

def main():
    # Check if running in a virtual environment
    if not hasattr(sys, 'real_prefix') and not hasattr(sys, 'base_prefix'):
        print("ВНИМАНИЕ: Рекомендуется запускать приложение в виртуальном окружении.")
        print("Создайте виртуальное окружение командой:")
        print("python -m venv venv")
        print("Активируйте его командой:")
        print("venv\\Scripts\\activate  # для Windows")
        print("source venv/bin/activate  # для Linux/Mac")
        print("\nПродолжить запуск? (y/n)")
        if input().lower() != 'y':
            sys.exit(1)

    # Check if license.key exists
    if not os.path.exists('license.key'):
        print("ОШИБКА: Файл license.key не найден!")
        print("Создайте файл license.key в текущей директории с вашим лицензионным ключом.")
        sys.exit(1)

    # Check if app_conf.json exists
    if not os.path.exists('app_conf.json'):
        print("Создание файла конфигурации app_conf.json...")
        with open('app_conf.json', 'w', encoding='utf-8') as f:
            f.write('''{
    "db_path": "",
    "weight_format": "#.",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "access_key": "",
    "object_id1": "",
    "object_name1": "",
    "object_id2": "",
    "object_name2": "",
    "object_url": "",
    "font_family": "Arial",
    "font_size": "10"
}''')

    # Start the application
    print("Запуск приложения...")
    print("Открытие браузера...")
    webbrowser.open('http://localhost:5000')
    app.run(debug=True)

if __name__ == '__main__':
    main() 