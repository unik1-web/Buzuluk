import os
import shutil
import datetime
import json
import sys

def create_backup():
    """Create a backup of application data"""
    try:
        # Create backup directory
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        # Generate backup filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        # Create backup directory
        os.makedirs(backup_path)
        
        # Files to backup
        files_to_backup = [
            'app_data.sqlite',
            'app_conf.json',
            'license.key'
        ]
        
        # Copy files
        for file in files_to_backup:
            if os.path.exists(file):
                shutil.copy2(file, backup_path)
                print(f"✓ Скопирован файл: {file}")
            else:
                print(f"! Файл не найден: {file}")
        
        # Create backup info file
        info = {
            "timestamp": timestamp,
            "files": files_to_backup,
            "version": "1.0"
        }
        
        with open(os.path.join(backup_path, "backup_info.json"), 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=4, ensure_ascii=False)
            
        print(f"\n✓ Резервная копия успешно создана: {backup_name}")
        return True
        
    except Exception as e:
        print(f"ОШИБКА при создании резервной копии: {e}")
        return False

def restore_backup(backup_name):
    """Restore application data from backup"""
    try:
        backup_dir = "backups"
        backup_path = os.path.join(backup_dir, backup_name)
        
        if not os.path.exists(backup_path):
            print(f"ОШИБКА: Резервная копия {backup_name} не найдена!")
            return False
            
        # Files to restore
        files_to_restore = [
            'app_data.sqlite',
            'app_conf.json',
            'license.key'
        ]
        
        # Restore files
        for file in files_to_restore:
            backup_file = os.path.join(backup_path, file)
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, file)
                print(f"✓ Восстановлен файл: {file}")
            else:
                print(f"! Файл не найден в резервной копии: {file}")
                
        print(f"\n✓ Резервная копия {backup_name} успешно восстановлена!")
        return True
        
    except Exception as e:
        print(f"ОШИБКА при восстановлении резервной копии: {e}")
        return False

def list_backups():
    """List all available backups"""
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        print("Резервные копии не найдены.")
        return
        
    backups = []
    for backup_name in os.listdir(backup_dir):
        backup_path = os.path.join(backup_dir, backup_name)
        if os.path.isdir(backup_path):
            info_file = os.path.join(backup_path, "backup_info.json")
            if os.path.exists(info_file):
                with open(info_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    backups.append((backup_name, info["timestamp"]))
                    
    if not backups:
        print("Резервные копии не найдены.")
        return
        
    print("\nДоступные резервные копии:")
    print("-" * 50)
    for backup_name, timestamp in sorted(backups, key=lambda x: x[1], reverse=True):
        print(f"{backup_name} ({timestamp})")
    print("-" * 50)

def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python backup.py create  - создать резервную копию")
        print("  python backup.py list    - показать список резервных копий")
        print("  python backup.py restore <имя_копии>  - восстановить резервную копию")
        return
        
    command = sys.argv[1]
    
    if command == "create":
        create_backup()
    elif command == "list":
        list_backups()
    elif command == "restore":
        if len(sys.argv) < 3:
            print("ОШИБКА: Укажите имя резервной копии")
            return
        backup_name = sys.argv[2]
        print(f"Восстановление резервной копии {backup_name}...")
        print("ВНИМАНИЕ: Текущие данные будут заменены!")
        print("Продолжить? (y/n)")
        if input().lower() == 'y':
            restore_backup(backup_name)
    else:
        print(f"ОШИБКА: Неизвестная команда: {command}")

if __name__ == '__main__':
    main() 