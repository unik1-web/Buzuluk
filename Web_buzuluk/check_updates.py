import os
import sys
import json
import requests
import hashlib
import datetime
from packaging import version

def get_current_version():
    """Get the current version of the application"""
    try:
        with open('version.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('version', '0.0.0')
    except:
        return '0.0.0'

def get_file_hash(filepath):
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def check_updates(current_version, update_url):
    """Check for available updates"""
    try:
        # Get update information from server
        response = requests.get(update_url)
        if response.status_code != 200:
            print(f"ОШИБКА: Не удалось получить информацию об обновлениях (код: {response.status_code})")
            return None
            
        update_info = response.json()
        latest_version = update_info.get('version')
        
        if not latest_version:
            print("ОШИБКА: Неверный формат информации об обновлении")
            return None
            
        # Compare versions
        if version.parse(latest_version) > version.parse(current_version):
            return update_info
        else:
            print("У вас установлена последняя версия программы.")
            return None
            
    except requests.exceptions.ConnectionError:
        print("ОШИБКА: Не удалось подключиться к серверу обновлений")
        return None
    except Exception as e:
        print(f"ОШИБКА при проверке обновлений: {e}")
        return None

def download_update(update_info, download_dir='updates'):
    """Download update files"""
    try:
        # Create download directory
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            
        # Download files
        downloaded_files = []
        for file_info in update_info.get('files', []):
            url = file_info.get('url')
            filename = file_info.get('filename')
            expected_hash = file_info.get('hash')
            
            if not all([url, filename, expected_hash]):
                print(f"! Пропущен файл {filename}: неполная информация")
                continue
                
            filepath = os.path.join(download_dir, filename)
            
            # Download file
            print(f"Загрузка {filename}...")
            response = requests.get(url, stream=True)
            if response.status_code != 200:
                print(f"! Ошибка загрузки {filename}")
                continue
                
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            # Verify hash
            actual_hash = get_file_hash(filepath)
            if actual_hash != expected_hash:
                print(f"! Ошибка проверки {filename}")
                os.remove(filepath)
                continue
                
            downloaded_files.append(filepath)
            print(f"✓ Загружен файл: {filename}")
            
        return downloaded_files
        
    except Exception as e:
        print(f"ОШИБКА при загрузке обновления: {e}")
        return []

def apply_update(files, backup=True):
    """Apply downloaded updates"""
    try:
        # Create backup if requested
        if backup:
            print("\nСоздание резервной копии...")
            backup_dir = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir)
            
            for filepath in files:
                filename = os.path.basename(filepath)
                if os.path.exists(filename):
                    shutil.copy2(filename, os.path.join(backup_dir, filename))
                    print(f"✓ Сохранен файл: {filename}")
                    
        # Apply updates
        print("\nПрименение обновлений...")
        for filepath in files:
            filename = os.path.basename(filepath)
            shutil.copy2(filepath, filename)
            print(f"✓ Обновлен файл: {filename}")
            
        return True
        
    except Exception as e:
        print(f"ОШИБКА при применении обновления: {e}")
        return False

def main():
    # Get current version
    current_version = get_current_version()
    print(f"Текущая версия: {current_version}")
    
    # Get update URL from config
    try:
        with open('app_conf.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            update_url = config.get('update_url')
    except:
        update_url = None
        
    if not update_url:
        print("ОШИБКА: URL сервера обновлений не указан в конфигурации")
        return
        
    # Check for updates
    print("\nПроверка обновлений...")
    update_info = check_updates(current_version, update_url)
    
    if update_info:
        print(f"\nДоступно обновление до версии {update_info['version']}")
        print(f"Изменения: {update_info.get('description', 'Нет описания')}")
        print("\nПродолжить обновление? (y/n)")
        if input().lower() != 'y':
            print("Обновление отменено.")
            return
            
        # Download update
        print("\nЗагрузка обновления...")
        files = download_update(update_info)
        
        if not files:
            print("ОШИБКА: Не удалось загрузить файлы обновления")
            return
            
        # Apply update
        if apply_update(files):
            print("\nОбновление успешно завершено!")
            print("Перезапустите приложение для применения изменений.")
        else:
            print("\nОШИБКА: Не удалось применить обновление")
            print("Проверьте резервную копию в директории backup_*")
    else:
        print("\nОбновления не требуются.")

if __name__ == '__main__':
    main() 