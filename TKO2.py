import fdb
import json
from uuid import uuid4
from datetime import datetime

# Настройки подключения к базе данных
db_path = r'C:\VESYEVENT.GDB'
user = 'SYSDBA'
password = 'masterkey'

# Подключение к базе данных
conn = fdb.connect(dsn=db_path, user=user, password=password)
cursor = conn.cursor()

# Выполнение SQL-запроса для выборки данных
query = """
SELECT DATE_BRUTTO, DATE_TARA, AUTO_TS_NOMER, AUTO_TS_MARKA, FIRMA, BRUTTO, TARA, NETTO, GRUZ_NAME
FROM EVENTS
"""
cursor.execute(query)

# Создание структуры JSON
data = {
    "ObjectId": "insert_ObjectId",
    "AccessKey": "insert_AccessKey",
    "WeightControls": []
}

# Обработка данных из базы данных
for row in cursor:
    weight_control = {
        "Id": str(uuid4()),
        "DateBefore": row[0].strftime("%Y-%m-%d %H:%M:%S+05:00") if row[0] else None,
        "DateAfter": row[1].strftime("%Y-%m-%d %H:%M:%S+05:00") if row[1] else None,
        "RegistrationNumber": row[2],
        "GarbageTruckType": None,
        "GarbageTruckBrand": row[3],
        "GarbageTruckModel": None,
        "CompanyName": row[4],
        "CompanyInn": "5612167252",  # Пример значения, замените на реальное
        "CompanyKpp": "561101001",   # Пример значения, замените на реальное
        "WeightBefore": row[5],
        "WeightAfter": row[6],
        "WeightDriver": 0,
        "Coefficient": 1.0,
        "GarbageWeight": row[7],
        "GarbageType": row[8]
    }
    data["WeightControls"].append(weight_control)

# Закрытие соединения с базой данных
cursor.close()
conn.close()

# Запись данных в JSON-файл
with open('output.json', 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)

print("Данные успешно экспортированы в output.json")