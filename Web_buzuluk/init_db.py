import os
import sys
from app import app, db

def init_database():
    """Initialize the database"""
    try:
        # Create all tables
        with app.app_context():
            db.create_all()
            print("База данных успешно инициализирована!")
            return True
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        return False

def main():
    # Check if running in a virtual environment
    if not hasattr(sys, 'real_prefix') and not hasattr(sys, 'base_prefix'):
        print("ВНИМАНИЕ: Рекомендуется запускать скрипт в виртуальном окружении.")
        print("Создайте виртуальное окружение командой:")
        print("python -m venv venv")
        print("Активируйте его командой:")
        print("venv\\Scripts\\activate  # для Windows")
        print("source venv/bin/activate  # для Linux/Mac")
        print("\nПродолжить запуск? (y/n)")
        if input().lower() != 'y':
            sys.exit(1)

    # Check if database file exists
    if os.path.exists('app_data.sqlite'):
        print("ВНИМАНИЕ: Файл базы данных app_data.sqlite уже существует!")
        print("Хотите пересоздать его? (y/n)")
        if input().lower() != 'y':
            print("Операция отменена.")
            return

    # Initialize database
    if init_database():
        print("\nТеперь вы можете создать администратора командой:")
        print("python create_admin.py")
    else:
        print("\nНе удалось инициализировать базу данных.")
        print("Проверьте права доступа к директории.")

if __name__ == '__main__':
    main() 