import os
import sys
import shutil
import zipfile
import datetime
import json

def create_distribution():
    """Create a distribution package"""
    try:
        # Create distribution directory
        dist_dir = "dist"
        if not os.path.exists(dist_dir):
            os.makedirs(dist_dir)
            
        # Generate distribution name
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dist_name = f"web_buzuluk_{timestamp}"
        dist_path = os.path.join(dist_dir, dist_name)
        
        # Create distribution directory
        os.makedirs(dist_path)
        
        # Files to include
        files_to_include = [
            'app.py',
            'requirements.txt',
            'README.md',
            'version.json',
            'app_conf.json',
            'setup.bat',
            'setup.sh',
            'run.py',
            'create_admin.py',
            'create_license.py',
            'create_version.py',
            'init_db.py',
            'test_db.py',
            'test_reo.py',
            'check_status.py',
            'backup.py',
            'cleanup_backups.py',
            'view_logs.py',
            'cleanup_logs.py',
            'check_updates.py'
        ]
        
        # Copy files
        for file in files_to_include:
            if os.path.exists(file):
                shutil.copy2(file, dist_path)
                print(f"✓ Скопирован файл: {file}")
            else:
                print(f"! Файл не найден: {file}")
                
        # Create templates directory
        templates_dir = os.path.join(dist_path, "templates")
        os.makedirs(templates_dir)
        
        # Copy templates
        if os.path.exists("templates"):
            for file in os.listdir("templates"):
                if file.endswith(".html"):
                    shutil.copy2(os.path.join("templates", file), templates_dir)
                    print(f"✓ Скопирован шаблон: {file}")
                    
        # Create distribution info file
        info = {
            "timestamp": timestamp,
            "files": files_to_include,
            "version": "1.0"
        }
        
        with open(os.path.join(dist_path, "dist_info.json"), 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=4, ensure_ascii=False)
            
        # Create ZIP archive
        zip_path = os.path.join(dist_dir, f"{dist_name}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(dist_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, dist_path)
                    zipf.write(file_path, arcname)
                    
        print(f"\n✓ Распространяемый пакет успешно создан: {zip_path}")
        return True
        
    except Exception as e:
        print(f"ОШИБКА при создании пакета: {e}")
        return False

def main():
    print("Создание распространяемого пакета...")
    print("ВНИМАНИЕ: Убедитесь, что все файлы актуальны!")
    print("Продолжить? (y/n)")
    if input().lower() == 'y':
        create_distribution()
    else:
        print("Операция отменена.")

if __name__ == '__main__':
    main() 