import json
import fdb
import sys

def test_connection(db_path):
    """Test connection to the database"""
    try:
        # Try to connect to the database
        conn = fdb.connect(
            host='localhost',
            database=db_path,
            user='SYSDBA',
            password='masterkey'
        )
        
        # Try to execute a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT FIRST 1 * FROM VESYEVENT")
        row = cursor.fetchone()
        
        if row:
            print("Подключение к базе данных успешно!")
            print(f"Найдена запись: {row}")
            return True
        else:
            print("Подключение успешно, но таблица VESYEVENT пуста")
            return True
            
    except fdb.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return False
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    # Check if db_path is provided as command line argument
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Try to read from app_conf.json
        try:
            with open('app_conf.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                db_path = config.get('db_path', '')
        except FileNotFoundError:
            print("ОШИБКА: Файл app_conf.json не найден")
            return
        except json.JSONDecodeError:
            print("ОШИБКА: Неверный формат файла app_conf.json")
            return

    if not db_path:
        print("ОШИБКА: Путь к базе данных не указан")
        print("Укажите путь к базе данных в app_conf.json или как аргумент командной строки")
        return

    print(f"Тестирование подключения к базе данных: {db_path}")
    test_connection(db_path)

if __name__ == '__main__':
    main() 