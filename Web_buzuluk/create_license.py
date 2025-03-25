import os
import hashlib
import datetime

def generate_license_key():
    """Generate a license key based on current date and time"""
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # Create a hash of the current time
    hash_object = hashlib.sha256(current_time.encode())
    return hash_object.hexdigest()[:32]

def main():
    # Check if license.key already exists
    if os.path.exists('license.key'):
        print("ВНИМАНИЕ: Файл license.key уже существует!")
        print("Хотите перезаписать его? (y/n)")
        if input().lower() != 'y':
            print("Операция отменена.")
            return

    # Generate and save license key
    license_key = generate_license_key()
    with open('license.key', 'w') as f:
        f.write(license_key)

    print("Лицензионный ключ успешно создан!")
    print(f"Ключ: {license_key}")
    print("\nВНИМАНИЕ: Сохраните этот ключ в надежном месте!")
    print("Он потребуется для активации программы на других компьютерах.")

if __name__ == '__main__':
    main() 