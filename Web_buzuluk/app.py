from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import fdb
import json
import os
import logging
from uuid import uuid4
import requests
import base64
import hashlib
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("web_app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Проверка наличия необходимых файлов
def check_required_files():
    required_files = {
        'app_conf.json': 'Файл настроек',
        'app_data.sqlite': 'База данных',
        'license.key': 'Файл лицензии'
    }
    
    missing_files = []
    for file_name, description in required_files.items():
        if not os.path.exists(file_name):
            missing_files.append(f"{description} ({file_name})")
    
    if missing_files:
        logger.error("Отсутствуют необходимые файлы:")
        for file in missing_files:
            logger.error(f"- {file}")
        return False
    return True

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app_data.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class WeighingData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetimebrutto = db.Column(db.DateTime, nullable=False)
    datetimetara = db.Column(db.DateTime, nullable=False)
    nomer_ts = db.Column(db.String(20), nullable=False)
    marka_ts = db.Column(db.String(50), nullable=False)
    firma_pol = db.Column(db.String(100), nullable=False)
    brutto = db.Column(db.Float, nullable=False)
    tara = db.Column(db.Float, nullable=False)
    netto = db.Column(db.Float, nullable=False)
    gruz_name = db.Column(db.String(100), nullable=False)
    inn = db.Column(db.String(12))
    kpp = db.Column(db.String(9))
    status = db.Column(db.String(20))
    sent_date = db.Column(db.DateTime)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def check_license():
    try:
        secret_key = "BuzulukSecretKey2024"
        
        if not os.path.exists("license.key"):
            logger.error("License file not found")
            return False
            
        with open("license.key", "r") as f:
            encoded_key = f.read().strip()
            
        try:
            decoded_key = base64.b64decode(encoded_key.encode()).decode()
        except:
            logger.error("Invalid license format")
            return False
            
        date_str = decoded_key[:8]
        stored_hash = decoded_key[8:]
        
        data_to_hash = f"{date_str}{secret_key}"
        hash_object = hashlib.sha256(data_to_hash.encode())
        calculated_hash = hash_object.hexdigest()
        
        if stored_hash != calculated_hash:
            logger.error("License is corrupted")
            return False
            
        try:
            expiry_date = datetime.strptime(date_str, "%Y%m%d")
            current_date = datetime.now()
            
            if current_date > expiry_date:
                logger.error("License has expired")
                return False
                
            return True
            
        except ValueError:
            logger.error("Invalid date in license")
            return False
            
    except Exception as e:
        logger.error(f"License check error: {str(e)}")
        return False

def load_config():
    if os.path.exists("app_conf.json"):
        with open("app_conf.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open("app_conf.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    if not check_license():
        return render_template('license_error.html')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:  # In production, use proper password hashing
            login_user(user)
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'success': True})

def fetch_data_from_firebird(date_str):
    try:
        config = load_config()
        db_path = config.get('db_path')
        if not db_path:
            logger.error("Путь к базе данных не указан в настройках")
            return []
            
        conn = fdb.connect(
            dsn=db_path,
            user='SYSDBA',
            password='masterkey'
        )
        cursor = conn.cursor()
        
        query = """
        SELECT DATE_BRUTTO + TIME_BRUTTO AS DATETIME_BRUTTO, 
               DATE_TARA + TIME_TARA AS DATETIME_TARA, 
               NOMER_TS || REGION_TS AS NOMER_TS_FULL, 
               MARKA_TS, 
               FIRMA_POL, 
               BRUTTO, 
               TARA, 
               NETTO, 
               GRUZ_NAME,
               DATEDIFF(MINUTE, TIME_BRUTTO, TIME_TARA) AS TIME_DIFF
        FROM EVENTS
        WHERE DATE_TARA IS NOT NULL 
        AND DATE_BRUTTO = ?
        AND ENABLE = 0
        """
        
        cursor.execute(query, (date_str,))
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        logger.info(f"Успешно получены данные из базы данных за дату: {date_str}")
        return rows
    except Exception as e:
        logger.error(f"Ошибка при чтении данных из базы данных: {str(e)}")
        return []

@app.route('/api/weighing_data')
@login_required
def get_weighing_data():
    try:
        date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Получаем данные из Firebird
        firebird_data = fetch_data_from_firebird(date_str)
        
        # Получаем данные из SQLite
        sqlite_data = WeighingData.query.filter(
            db.func.date(WeighingData.datetimebrutto) == date.date()
        ).all()
        
        # Преобразуем данные из Firebird в нужный формат
        firebird_formatted = []
        for row in firebird_data:
            firebird_formatted.append({
                'datetimebrutto': row[0].strftime('%Y-%m-%d %H:%M:%S'),
                'datetimetara': row[1].strftime('%Y-%m-%d %H:%M:%S'),
                'nomer_ts': row[2],
                'marka_ts': row[3],
                'firma_pol': row[4],
                'brutto': float(row[5]),
                'tara': float(row[6]),
                'netto': float(row[7]),
                'gruz_name': row[8],
                'inn': None,  # Будет заполнено из SQLite
                'kpp': None,  # Будет заполнено из SQLite
                'status': None,  # Будет заполнено из SQLite
                'sent_date': None  # Будет заполнено из SQLite
            })
        
        # Преобразуем данные из SQLite в нужный формат
        sqlite_formatted = [{
            'datetimebrutto': item.datetimebrutto.strftime('%Y-%m-%d %H:%M:%S'),
            'datetimetara': item.datetimetara.strftime('%Y-%m-%d %H:%M:%S'),
            'nomer_ts': item.nomer_ts,
            'marka_ts': item.marka_ts,
            'firma_pol': item.firma_pol,
            'brutto': item.brutto,
            'tara': item.tara,
            'netto': item.netto,
            'gruz_name': item.gruz_name,
            'inn': item.inn,
            'kpp': item.kpp,
            'status': item.status,
            'sent_date': item.sent_date.strftime('%Y-%m-%d %H:%M:%S') if item.sent_date else None
        } for item in sqlite_data]
        
        # Объединяем данные, отдавая предпочтение данным из SQLite
        combined_data = {}
        for item in firebird_formatted:
            key = f"{item['datetimebrutto']}_{item['datetimetara']}_{item['nomer_ts']}"
            combined_data[key] = item
            
        for item in sqlite_formatted:
            key = f"{item['datetimebrutto']}_{item['datetimetara']}_{item['nomer_ts']}"
            if key in combined_data:
                # Обновляем данные из Firebird данными из SQLite
                combined_data[key].update(item)
            else:
                combined_data[key] = item
        
        return jsonify(list(combined_data.values()))
        
    except Exception as e:
        logger.error(f"Ошибка при получении данных: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/send_data', methods=['POST'])
@login_required
def send_data():
    try:
        data = request.json
        config = load_config()
        
        # Prepare data for REO
        reo_data = {
            "ObjectId": config.get("object_id1", ""),
            "AccessKey": config.get("access_key", ""),
            "WeightControls": []
        }
        
        for item in data:
            weight_control = {
                "id": str(uuid4()),
                "dateBefore": item['datetimebrutto'],
                "dateAfter": item['datetimetara'],
                "registrationNumber": item['nomer_ts'],
                "garbageTruckType": None,
                "garbageTruckBrand": item['marka_ts'],
                "garbageTruckModel": None,
                "companyName": item['firma_pol'],
                "companyInn": item['inn'],
                "companyKpp": item['kpp'],
                "weightBefore": str(item['brutto']),
                "weightAfter": str(item['tara']),
                "weightDriver": None,
                "coefficient": "1",
                "garbageWeight": str(item['netto']),
                "garbageType": item['gruz_name'],
                "codeFKKO": None,
                "nameFKKO": None
            }
            reo_data["WeightControls"].append(weight_control)
        
        # Send data to REO
        response = requests.post(config.get("object_url", ""), json=reo_data)
        
        if response.status_code == 200:
            # Update database
            for item in data:
                weighing_data = WeighingData.query.filter_by(
                    datetimebrutto=datetime.strptime(item['datetimebrutto'], '%Y-%m-%d %H:%M:%S'),
                    datetimetara=datetime.strptime(item['datetimetara'], '%Y-%m-%d %H:%M:%S'),
                    nomer_ts=item['nomer_ts']
                ).first()
                
                if weighing_data:
                    weighing_data.status = "Отправлено"
                    weighing_data.sent_date = datetime.now()
            
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': f'Error: {response.status_code}'})
            
    except Exception as e:
        logger.error(f"Error sending data: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/settings', methods=['GET'])
@login_required
def get_settings():
    try:
        with open('app_conf.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return jsonify(settings)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/settings', methods=['POST'])
@login_required
def save_settings():
    try:
        settings = request.get_json()
        with open('app_conf.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/test_db', methods=['POST'])
@login_required
def test_db():
    try:
        data = request.get_json()
        db_path = data.get('db_path')
        if not db_path:
            return jsonify({'success': False, 'message': 'Путь к базе данных не указан'})
        
        # Добавляем стандартные учетные данные Firebird
        conn = fdb.connect(
            dsn=db_path,
            user='SYSDBA',
            password='masterkey'
        )
        conn.close()
        return jsonify({'success': True, 'message': 'Подключение к базе данных успешно'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка подключения к базе данных: {str(e)}'})

@app.route('/api/test_reo', methods=['POST'])
@login_required
def test_reo():
    try:
        data = request.get_json()
        access_key = data.get('access_key')
        object_url = data.get('object_url')
        
        if not access_key or not object_url:
            return jsonify({'success': False, 'message': 'Не указаны необходимые параметры'})
        
        # Создаем тестовые данные
        test_data = {
            "ObjectId": "test",
            "AccessKey": access_key,
            "WeightControls": []
        }
        
        # Отправляем POST запрос
        response = requests.post(object_url, json=test_data)
        response.raise_for_status()
        
        return jsonify({'success': True, 'message': 'Подключение к РЭО успешно'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка подключения к РЭО: {str(e)}'})

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

if __name__ == '__main__':
    # Проверяем наличие необходимых файлов
    if not check_required_files():
        logger.error("Приложение не может быть запущено из-за отсутствия необходимых файлов")
        sys.exit(1)
        
    with app.app_context():
        db.create_all()
        # Создаем пользователя по умолчанию, если его нет
        default_user = User.query.filter_by(username='admin').first()
        if not default_user:
            default_user = User(username='admin', password='admin')
            db.session.add(default_user)
            db.session.commit()
            logger.info("Created default user: admin")
    app.run(debug=True) 