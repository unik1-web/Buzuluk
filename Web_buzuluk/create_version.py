import os
import json
import sys
import hashlib
import datetime

def get_file_hash(filepath):
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def create_version_file(version, description=None):
    """Create or update version.json file"""
    try:
        # Prepare version info
        version_info = {
            "version": version,
            "build_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "description": description or "Нет описания",
            "files": []
        }
        
        # Add file information
        files_to_check = [
            'app.py',
            'app_data.sqlite',
            'app_conf.json',
            'license.key'
        ]
        
        for filename in files_to_check:
            if os.path.exists(filename):
                file_hash = get_file_hash(filename)
                version_info["files"].append({
                    "filename": filename,
                    "hash": file_hash,
                    "size": os.path.getsize(filename)
                })
                
        # Save version info
        with open('version.json', 'w', encoding='utf-8') as f:
            json.dump(version_info, f, indent=4, ensure_ascii=False)
            
        print("✓ Файл version.json успешно создан!")
        print(f"Версия: {version}")
        print(f"Дата сборки: {version_info['build_date']}")
        print(f"Описание: {version_info['description']}")
        print(f"\nПроверено файлов: {len(version_info['files'])}")
        return True
        
    except Exception as e:
        print(f"ОШИБКА при создании файла версии: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python create_version.py <версия> [описание]")
        print("Пример:")
        print("  python create_version.py 1.0.0 \"Первая версия\"")
        return
        
    version = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Validate version format
    try:
        major, minor, patch = map(int, version.split('.'))
        if any(x < 0 for x in [major, minor, patch]):
            raise ValueError
    except:
        print("ОШИБКА: Неверный формат версии. Используйте формат X.Y.Z")
        return
        
    create_version_file(version, description)

if __name__ == '__main__':
    main() 