import os
import sys
from app import app, db, User
from werkzeug.security import generate_password_hash

def create_admin_user(username, password):
    """Create a new admin user"""
    try:
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"Пользователь {username} уже существует!")
            print("Хотите изменить пароль? (y/n)")
            if input().lower() != 'y':
                print("Операция отменена.")
                return False
            
            # Update password
            existing_user.password_hash = generate_password_hash(password)
            db.session.commit()
            print(f"Пароль для пользователя {username} успешно обновлен!")
            return True
        
        # Create new user
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            is_admin=True
        )
        db.session.add(new_user)
        db.session.commit()
        print(f"Администратор {username} успешно создан!")
        return True
        
    except Exception as e:
        print(f"Ошибка при создании пользователя: {e}")
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

    # Get username and password
    username = input("Введите имя пользователя: ").strip()
    if not username:
        print("ОШИБКА: Имя пользователя не может быть пустым")
        return

    password = input("Введите пароль: ").strip()
    if not password:
        print("ОШИБКА: Пароль не может быть пустым")
        return

    confirm_password = input("Подтвердите пароль: ").strip()
    if password != confirm_password:
        print("ОШИБКА: Пароли не совпадают")
        return

    # Create admin user
    with app.app_context():
        create_admin_user(username, password)

if __name__ == '__main__':
    main() 