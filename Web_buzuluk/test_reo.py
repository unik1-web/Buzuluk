import json
import requests
import sys

def test_connection(url, access_key):
    """Test connection to the REO service"""
    try:
        # Prepare test data
        test_data = {
            "access_key": access_key,
            "test": True
        }
        
        # Send test request
        response = requests.post(url, json=test_data)
        
        # Check response
        if response.status_code == 200:
            print("Подключение к сервису РЭО успешно!")
            print(f"Ответ сервера: {response.text}")
            return True
        else:
            print(f"Ошибка подключения к сервису РЭО: {response.status_code}")
            print(f"Ответ сервера: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Ошибка: Не удалось подключиться к сервису РЭО")
        print("Проверьте правильность URL и доступность сервиса")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке запроса: {e}")
        return False
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return False

def main():
    # Check if url is provided as command line argument
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # Try to read from app_conf.json
        try:
            with open('app_conf.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                url = config.get('object_url', '')
                access_key = config.get('access_key', '')
        except FileNotFoundError:
            print("ОШИБКА: Файл app_conf.json не найден")
            return
        except json.JSONDecodeError:
            print("ОШИБКА: Неверный формат файла app_conf.json")
            return

    if not url:
        print("ОШИБКА: URL сервиса не указан")
        print("Укажите URL сервиса в app_conf.json или как аргумент командной строки")
        return

    if not access_key:
        print("ОШИБКА: Ключ доступа не указан")
        print("Укажите ключ доступа в app_conf.json")
        return

    print(f"Тестирование подключения к сервису РЭО: {url}")
    test_connection(url, access_key)

if __name__ == '__main__':
    main() 