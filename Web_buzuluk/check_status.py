import os
import json
import sys
from app import app, db, User, WeighingData

def check_license():
    """Check if license key exists and is valid"""
    try:
        if not os.path.exists('license.key'):
            print("ОШИБКА: Файл license.key не найден!")
            return False
        
        with open('license.key', 'r') as f:
            license_key = f.read().strip()
            
        if not license_key:
            print("ОШИБКА: Файл license.key пуст!")
            return False
            
        print("✓ Лицензионный ключ найден")
        return True
        
    except Exception as e:
        print(f"ОШИБКА при проверке лицензии: {e}")
        return False

def check_config():
    """Check if configuration file exists and is valid"""
    try:
        if not os.path.exists('app_conf.json'):
            print("ОШИБКА: Файл app_conf.json не найден!")
            return False
            
        with open('app_conf.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        required_fields = [
            'db_path', 'weight_format', 'date_format', 'access_key',
            'object_id1', 'object_name1', 'object_id2', 'object_name2',
            'object_url', 'font_family', 'font_size'
        ]
        
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            print(f"ОШИБКА: В файле app_conf.json отсутствуют поля: {', '.join(missing_fields)}")
            return False
            
        print("✓ Конфигурационный файл корректный")
        return True
        
    except json.JSONDecodeError:
        print("ОШИБКА: Неверный формат файла app_conf.json")
        return False
    except Exception as e:
        print(f"ОШИБКА при проверке конфигурации: {e}")
        return False

def check_database():
    """Check if database exists and is accessible"""
    try:
        if not os.path.exists('app_data.sqlite'):
            print("ОШИБКА: Файл базы данных app_data.sqlite не найден!")
            return False
            
        with app.app_context():
            # Check if tables exist
            if not User.query.first():
                print("ОШИБКА: В базе данных нет пользователей!")
                return False
                
            print("✓ База данных доступна")
            return True
            
    except Exception as e:
        print(f"ОШИБКА при проверке базы данных: {e}")
        return False

def check_dependencies():
    """Check if all required Python packages are installed"""
    try:
        import flask
        import fdb
        import requests
        import dateutil
        import flask_sqlalchemy
        import flask_login
        import flask_wtf
        
        print("✓ Все необходимые пакеты установлены")
        return True
        
    except ImportError as e:
        print(f"ОШИБКА: Отсутствует пакет {e.name}")
        print("Установите зависимости командой: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"ОШИБКА при проверке зависимостей: {e}")
        return False

def main():
    print("Проверка состояния приложения...")
    print("-" * 50)
    
    # Check all components
    components = {
        "Лицензия": check_license,
        "Конфигурация": check_config,
        "База данных": check_database,
        "Зависимости": check_dependencies
    }
    
    all_ok = True
    for name, func in components.items():
        print(f"\nПроверка {name}:")
        if not func():
            all_ok = False
            print(f"✗ {name} требует внимания")
        else:
            print(f"✓ {name} в порядке")
    
    print("\n" + "-" * 50)
    if all_ok:
        print("\nВсе компоненты в порядке! Приложение готово к работе.")
    else:
        print("\nОбнаружены проблемы. Исправьте их перед запуском приложения.")

if __name__ == '__main__':
    main() 