import os
import shutil
import datetime
import json
import sys

def get_backup_age(backup_path):
    """Get the age of a backup in days"""
    info_file = os.path.join(backup_path, "backup_info.json")
    if not os.path.exists(info_file):
        return None
        
    try:
        with open(info_file, 'r', encoding='utf-8') as f:
            info = json.load(f)
            timestamp = datetime.datetime.strptime(info["timestamp"], "%Y%m%d_%H%M%S")
            age = datetime.datetime.now() - timestamp
            return age.days
    except:
        return None

def cleanup_backups(max_age_days=30):
    """Remove backups older than max_age_days"""
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        print("Директория резервных копий не найдена.")
        return
        
    removed_count = 0
    skipped_count = 0
    
    for backup_name in os.listdir(backup_dir):
        backup_path = os.path.join(backup_dir, backup_name)
        if not os.path.isdir(backup_path):
            continue
            
        age = get_backup_age(backup_path)
        if age is None:
            print(f"! Пропущена копия {backup_name} (не удалось определить возраст)")
            skipped_count += 1
            continue
            
        if age > max_age_days:
            try:
                shutil.rmtree(backup_path)
                print(f"✓ Удалена копия {backup_name} (возраст: {age} дней)")
                removed_count += 1
            except Exception as e:
                print(f"! Ошибка при удалении {backup_name}: {e}")
                skipped_count += 1
        else:
            print(f"- Сохранена копия {backup_name} (возраст: {age} дней)")
            
    print(f"\nИтоги очистки:")
    print(f"✓ Удалено: {removed_count}")
    print(f"! Пропущено: {skipped_count}")
    print(f"- Сохранено: {len(os.listdir(backup_dir)) - removed_count - skipped_count}")

def main():
    if len(sys.argv) > 1:
        try:
            max_age_days = int(sys.argv[1])
            if max_age_days < 1:
                print("ОШИБКА: Возраст должен быть положительным числом")
                return
        except ValueError:
            print("ОШИБКА: Возраст должен быть числом")
            return
    else:
        max_age_days = 30
        
    print(f"Очистка резервных копий старше {max_age_days} дней...")
    print("ВНИМАНИЕ: Удаленные копии нельзя восстановить!")
    print("Продолжить? (y/n)")
    if input().lower() == 'y':
        cleanup_backups(max_age_days)
    else:
        print("Операция отменена.")

if __name__ == '__main__':
    main() 