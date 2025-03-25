import os
import sys
import datetime
import re
import glob

def get_log_files():
    """Get all log files in the current directory and logs subdirectory"""
    log_files = []
    
    # Check current directory
    if os.path.exists('app.log'):
        log_files.append('app.log')
        
    # Check logs directory
    if os.path.exists('logs'):
        log_files.extend(glob.glob('logs/*.log'))
        
    return log_files

def parse_log_date(filename):
    """Parse date from log filename if it contains one"""
    # Try to find date in filename (format: YYYYMMDD or YYYY-MM-DD)
    date_patterns = [
        r'(\d{8})',  # YYYYMMDD
        r'(\d{4}-\d{2}-\d{2})'  # YYYY-MM-DD
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, filename)
        if match:
            date_str = match.group(1)
            try:
                if len(date_str) == 8:  # YYYYMMDD
                    return datetime.datetime.strptime(date_str, "%Y%m%d")
                else:  # YYYY-MM-DD
                    return datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue
                
    return None

def cleanup_logs(max_age_days=30, max_size_mb=100):
    """Remove old log files and rotate large ones"""
    log_files = get_log_files()
    if not log_files:
        print("Лог-файлы не найдены.")
        return
        
    removed_count = 0
    rotated_count = 0
    skipped_count = 0
    
    for log_file in log_files:
        try:
            # Get file info
            stat = os.stat(log_file)
            file_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(stat.st_mtime)
            file_size_mb = stat.st_size / (1024 * 1024)
            
            # Try to get date from filename
            file_date = parse_log_date(log_file)
            if file_date:
                file_age = datetime.datetime.now() - file_date
            
            # Check if file is too old
            if file_age.days > max_age_days:
                try:
                    os.remove(log_file)
                    print(f"✓ Удален старый файл: {log_file} (возраст: {file_age.days} дней)")
                    removed_count += 1
                except Exception as e:
                    print(f"! Ошибка при удалении {log_file}: {e}")
                    skipped_count += 1
                continue
                
            # Check if file is too large
            if file_size_mb > max_size_mb:
                try:
                    # Create backup filename with timestamp
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_name = f"{log_file}.{timestamp}"
                    
                    # Move current log to backup
                    os.rename(log_file, backup_name)
                    print(f"✓ Перемещен большой файл: {log_file} (размер: {file_size_mb:.1f} MB)")
                    rotated_count += 1
                except Exception as e:
                    print(f"! Ошибка при ротации {log_file}: {e}")
                    skipped_count += 1
            else:
                print(f"- Сохранен файл: {log_file} (размер: {file_size_mb:.1f} MB, возраст: {file_age.days} дней)")
                
        except Exception as e:
            print(f"! Ошибка при обработке {log_file}: {e}")
            skipped_count += 1
            
    print(f"\nИтоги очистки:")
    print(f"✓ Удалено: {removed_count}")
    print(f"✓ Перемещено: {rotated_count}")
    print(f"! Пропущено: {skipped_count}")
    print(f"- Сохранено: {len(log_files) - removed_count - rotated_count - skipped_count}")

def main():
    if len(sys.argv) > 2:
        try:
            max_age_days = int(sys.argv[1])
            max_size_mb = int(sys.argv[2])
            if max_age_days < 1 or max_size_mb < 1:
                print("ОШИБКА: Параметры должны быть положительными числами")
                return
        except ValueError:
            print("ОШИБКА: Параметры должны быть числами")
            return
    else:
        max_age_days = 30
        max_size_mb = 100
        
    print(f"Очистка лог-файлов:")
    print(f"- Удаление файлов старше {max_age_days} дней")
    print(f"- Ротация файлов больше {max_size_mb} MB")
    print("\nВНИМАНИЕ: Удаленные файлы нельзя восстановить!")
    print("Продолжить? (y/n)")
    if input().lower() == 'y':
        cleanup_logs(max_age_days, max_size_mb)
    else:
        print("Операция отменена.")

if __name__ == '__main__':
    main() 