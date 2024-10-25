from flask import Flask, request, jsonify, abort
from flask_restx import Api, Resource, fields, Namespace
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import requests
from urllib.parse import urlparse
import os
BASE_URL_HOSPITALS = "http://hospitals-service:8082"

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)
authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Вставте токен в формате: Bearer токен'
    }
}
api = Api(app, version='1.0', title='Documents API', description='API для управления документами', authorizations=authorizations, security='Bearer')


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
def get_hospitals_by_id(access_token, hospital_id):
    url = f"{BASE_URL_HOSPITALS}/api/Hospitals/{hospital_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if not data.get('is_deleted', True):  # Check that the hospital is not marked as deleted
            return True
    abort(404, 'Hospital not found or is deleted')

def get_rooms_by_id(access_token, hospital_id, room):
    url = f"{BASE_URL_HOSPITALS}/api/Hospitals/{hospital_id}/Rooms"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        rooms = response.json()
        if any(r['room_name'] == room for r in rooms):
            return True
    abort(404, 'Room not found in the specified hospital')

def validate_roles(token, required_roles):
    try:
        params = {
            "accessToken": token
        }
        response = requests.get('http://users-service:8081/api/Authentication/Validate', params=params)
        data = response.json()

        # Проверяем наличие хотя бы одной из требуемых ролей
        if not any(role in data.get("roles", []) for role in required_roles):
            abort(403, 'Недостаточно прав для выполнения этого действия')
    except Exception as e:
        abort(500, 'Ошибка при валидации токена')

def get_doctor_by_id(token, doctor_id):
    url = f"http://users-service:8081/api/Doctors/{doctor_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Доктор существует
    abort(404, {'message': 'Doctor not found'})  # Если доктора нет

history_ns = Namespace('Документы', description='Create, Update, GetByAccount, GetByHistory')

history_model = api.model('History', {
    'date': fields.DateTime(required=True, description='Дата ISO8601 формате'),
    'pacientId': fields.Integer(required=True, description='The patient ID'),
    'hospitalId': fields.Integer(required=True, description='The hospital ID'),
    'doctorId': fields.Integer(required=True, description='The doctor ID'),
    'room': fields.String(required=True, description='The room number or name'),
    'data': fields.String(required=True, description='Additional data about the visit')
})

@history_ns.route('/Account/<int:id>')
class AccountHistoryResource(Resource):
    @jwt_required()
    def get(self, id):
        """Получение истории посещений и назначений аккаунта"""
        token = request.headers.get('Authorization').split()[1]
        validate_roles(token, ['Doctor', 'Admin'])

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM history WHERE pacientId = %s",
                (id,)
            )
            history = cursor.fetchall()
        conn.close()
        return jsonify(history)

@history_ns.route('/<int:id>')
class HistoryResource(Resource):
    @jwt_required()
    def get(self, id):
        """Получение подробной информации о посещении и назначениях"""
        token = request.headers.get('Authorization').split()[1]
        validate_roles(token, ['Doctor', 'Admin'])

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM history WHERE pacientId = %s",
                (id,)
            )
            history = cursor.fetchall()
        conn.close()
        return jsonify(history)

    @jwt_required()
    @api.expect(history_model)
    def put(self, id):
        """Обновление истории посещения и назначения"""
        token = request.headers.get('Authorization').split()[1]
        validate_roles(token, ['Admin', 'Doctor'])

        data = request.json
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE history SET date = %s, pacientId = %s, hospitalId = %s, doctorId = %s, room = %s, data = %s WHERE id = %s",
                (data['date'], data['pacientId'], data['hospitalId'], data['doctorId'], data['room'], data['data'], id)
            )
            conn.commit()
        conn.close()
        return jsonify({'message': 'History updated successfully'})


@history_ns.route('/')
class HistoryCreateResource(Resource):
    @jwt_required()
    @api.expect(history_model)
    def post(self):
        """Создание истории посещения и назначения"""
        token = request.headers.get('Authorization').split()[1]
        validate_roles(token, ['Admin', 'Doctor'])

        data = request.json
        hospital_id = data['hospitalId']
        room = data['room']
        doctor_id = data['doctorId']

        get_hospitals_by_id(token, hospital_id)
        get_rooms_by_id(token, hospital_id, room)
        get_doctor_by_id(token, doctor_id)
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO history (date, pacientId, hospitalId, doctorId, room, data) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (data['date'], data['pacientId'], hospital_id, doctor_id, room, data['data'])
            )
            history_id = cursor.fetchone()['id']
            conn.commit()
        conn.close()

        response = jsonify({'message': 'History created successfully', 'id': history_id})
        response.status_code = 201
        return response


api.add_namespace(history_ns, path='/api/History')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8084)
