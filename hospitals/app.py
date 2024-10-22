from flask import Flask, request, jsonify, abort
from flask_restx import Api, Resource, fields
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
from urllib.parse import urlparse
import os
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)
api = Api(app, version='1.0', title='Hospital API', description='API для управления больницами')

# DB connection helper
def get_db_connection():
    # Получаем URL базы данных из переменной окружения
    db_url = os.getenv('DATABASE_URL')
    
    if db_url:
        result = urlparse(db_url)

        conn = psycopg2.connect(
            host=result.hostname,
            database=result.path[1:],  # Убираем начальный символ "/"
            user=result.username,
            password=result.password,
            port=result.port,
            cursor_factory=RealDictCursor
        )
        return conn
    else:
        raise ValueError("DATABASE_URL не установлена в переменных окружения")

# Helper function to validate roles
def validate_roles(token, required_role):
    try:
        params = {
            "accessToken": token
        }        
        response = requests.get('http://users-service:8081/api/Authentication/Validate', params=params)
        data = response.json()
        if required_role not in data.get("roles", []):
            abort(403, 'Недостаточно прав для выполнения этого действия')
    except Exception as e:
        abort(500, 'Ошибка при валидации токена')

# Модель данных для создания и изменения больницы
hospital_model = api.model('Hospital', {
    'name': fields.String(required=True, description='Название больницы'),
    'address': fields.String(required=True, description='Адрес больницы'),
    'contactPhone': fields.String(required=True, description='Контактный телефон'),
    'rooms': fields.List(fields.String, description='Список кабинетов')
})

# Routes
@api.route('/api/Hospitals')
class HospitalsList(Resource):
    @jwt_required()

    def get(self):
        """Получение списка больниц с пагинацией"""
        from_param = request.args.get('from', 0, type=int)
        count_param = request.args.get('count', 10, type=int)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM hospitals WHERE is_deleted = FALSE LIMIT %s OFFSET %s", (count_param, from_param))
        hospitals = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(hospitals)

    @jwt_required()
    @api.expect(hospital_model)
    def post(self):
        """Создание новой больницы (только для администраторов)"""
        token = request.headers.get('Authorization').split()[1]
        validate_roles(token, 'Admin')
        data = request.get_json()
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO hospitals (name, address, contact_phone) VALUES (%s, %s, %s) RETURNING id",
            (data['name'], data['address'], data['contactPhone'])
        )
        hospital_id = cur.fetchone()['id']
        
        for room_name in data['rooms']:
            cur.execute("INSERT INTO rooms (hospital_id, room_name) VALUES (%s, %s)", (hospital_id, room_name))
        
        conn.commit()
        cur.close()
        conn.close()
        response = jsonify({'message': 'Hospital created', 'hospital_id': hospital_id})
        response.status_code = 200
        return response

@api.route('/api/Hospitals/<int:id>')
class Hospital(Resource):
    @jwt_required()
    def get(self, id):
        """Получение информации о больнице по Id"""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM hospitals WHERE id = %s AND is_deleted = FALSE", (id,))
        hospital = cur.fetchone()
        cur.close()
        conn.close()
        
        if not hospital:
            return {'message': 'Hospital not found'}, 404
        
        return jsonify(hospital)

    @jwt_required()
    def put(self, id):
        """Изменение информации о больнице по Id (только для администраторов)"""
        token = request.headers.get('Authorization').split()[1]
        validate_roles(token, 'Admin')
        data = request.get_json()

        if 'name' not in data or 'address' not in data or 'contactPhone' not in data or 'rooms' not in data:
            return {'message': 'Missing required fields'}, 400
        
        conn = get_db_connection()
        cur = conn.cursor()

        # Обновление информации о больнице
        cur.execute(
            "UPDATE hospitals SET name = %s, address = %s, contact_phone = %s WHERE id = %s AND is_deleted = FALSE",
            (data['name'], data['address'], data['contactPhone'], id)
        )
        
        # Удаление старых кабинетов и добавление новых
        cur.execute("DELETE FROM rooms WHERE hospital_id = %s", (id,))
        conn.commit()
        for room_name in data['rooms']:
            cur.execute("INSERT INTO rooms (hospital_id, room_name) VALUES (%s, %s)", (id, room_name))
        
        conn.commit()
        cur.close()
        conn.close()

        return {'message': 'Hospital updated'}, 200

    @jwt_required()
    def delete(self, id):
        """Мягкое удаление записи о больнице (только для администраторов)"""
        token = request.headers.get('Authorization').split()[1]
        validate_roles(token, 'Admin')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE hospitals SET is_deleted = TRUE WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()

        return {'message': 'Hospital deleted'}, 200

@api.route('/api/Hospitals/<int:id>/Rooms')
class HospitalRooms(Resource):
    @jwt_required()
    def get(self, id):
        """Получение списка кабинетов больницы по Id"""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM rooms WHERE hospital_id = %s", (id,))
        rooms = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rooms)

if __name__ == '__main__':
    app.run(debug=False, port=8082, host='0.0.0.0')
