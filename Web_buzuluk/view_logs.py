import os
import sys
import datetime
import re

def get_log_file():
    """Get the path to the log file"""
    if os.path.exists('app.log'):
        return 'app.log'
    elif os.path.exists('logs/app.log'):
        return 'logs/app.log'
    else:
        return None

def parse_log_line(line):
    """Parse a log line and return its components"""
    # Log format: [YYYY-MM-DD HH:MM:SS] LEVEL: Message
    pattern = r'\[(.*?)\] (.*?): (.*)'
    match = re.match(pattern, line)
    if match:
        timestamp, level, message = match.groups()
        return timestamp, level, message
    return None, None, line

def view_logs(lines=100, level=None, search=None):
    """View application logs with optional filtering"""
    log_file = get_log_file()
    if not log_file:
        print("ОШИБКА: Файл логов не найден!")
        return
        
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            # Read all lines
            all_lines = f.readlines()
            
            # Apply filters
            filtered_lines = []
            for line in all_lines:
                timestamp, log_level, message = parse_log_line(line)
                
                # Skip if level filter is set and doesn't match
                if level and log_level and level.upper() not in log_level.upper():
                    continue
                    
                # Skip if search filter is set and doesn't match
                if search and search.lower() not in line.lower():
                    continue
                    
                filtered_lines.append(line)
            
            # Get the last N lines
            if lines > 0:
                filtered_lines = filtered_lines[-lines:]
            
            # Print the filtered lines
            if not filtered_lines:
                print("Нет записей, соответствующих указанным фильтрам.")
                return
                
            print(f"\nПоследние {len(filtered_lines)} записей лога:")
            print("-" * 80)
            for line in filtered_lines:
                print(line.rstrip())
            print("-" * 80)
            
    except Exception as e:
        print(f"ОШИБКА при чтении логов: {e}")

def get_log_stats():
    """Get statistics about the log file"""
    log_file = get_log_file()
    if not log_file:
        print("ОШИБКА: Файл логов не найден!")
        return
        
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Count lines by level
        level_counts = {}
        for line in lines:
            _, level, _ = parse_log_line(line)
            if level:
                level_counts[level] = level_counts.get(level, 0) + 1
                
        # Get file size
        size_bytes = os.path.getsize(log_file)
        size_mb = size_bytes / (1024 * 1024)
        
        # Get last modified time
        mtime = os.path.getmtime(log_file)
        last_modified = datetime.datetime.fromtimestamp(mtime)
        
        print("\nСтатистика логов:")
        print("-" * 80)
        print(f"Всего записей: {len(lines)}")
        print(f"Размер файла: {size_mb:.2f} MB")
        print(f"Последнее изменение: {last_modified}")
        print("\nЗаписей по уровням:")
        for level, count in level_counts.items():
            print(f"{level}: {count}")
        print("-" * 80)
        
    except Exception as e:
        print(f"ОШИБКА при получении статистики: {e}")

def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python view_logs.py view [количество_строк] [уровень] [поиск]  - просмотр логов")
        print("  python view_logs.py stats  - статистика логов")
        return
        
    command = sys.argv[1]
    
    if command == "view":
        # Parse arguments
        lines = 100
        level = None
        search = None
        
        if len(sys.argv) > 2:
            try:
                lines = int(sys.argv[2])
            except ValueError:
                level = sys.argv[2]
                
        if len(sys.argv) > 3:
            if level is None:
                level = sys.argv[3]
            else:
                search = sys.argv[3]
                
        if len(sys.argv) > 4:
            search = sys.argv[4]
            
        view_logs(lines, level, search)
        
    elif command == "stats":
        get_log_stats()
        
    else:
        print(f"ОШИБКА: Неизвестная команда: {command}")

if __name__ == '__main__':
    main() 