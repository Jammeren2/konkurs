from flask import Flask, request, jsonify, abort
from flask_restx import Api, Resource, fields
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import requests

BASE_URL_HOSPITALS = "http://127.0.0.1:8082"

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)
api = Api(app)

def get_db_connection():
    conn = psycopg2.connect(
        host='localhost',
        database='DOCUMENTS',
        user='postgres',
        password='123',
        cursor_factory=RealDictCursor
    )
    return conn

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
        response = requests.get('http://localhost:8081/api/Authentication/Validate', params=params)
        data = response.json()

        # Проверяем наличие хотя бы одной из требуемых ролей
        if not any(role in data.get("roles", []) for role in required_roles):
            abort(403, 'Недостаточно прав для выполнения этого действия')
    except Exception as e:
        abort(500, 'Ошибка при валидации токена')

history_ns = api.namespace('api/History', description='History Management')

history_model = api.model('History', {
    'date': fields.String(required=True, description='The date of the visit in ISO8601 format'),
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
        token = request.headers.get('Authorization').split()[1]
        validate_roles(token, ['Admin', 'Doctor'])

        data = request.json
        hospital_id = data['hospitalId']
        room = data['room']

        get_hospitals_by_id(token, hospital_id)

        get_rooms_by_id(token, hospital_id, room)
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO history (date, pacientId, hospitalId, doctorId, room, data) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (data['date'], data['pacientId'], hospital_id, data['doctorId'], room, data['data'])
            )
            history_id = cursor.fetchone()['id']
            conn.commit()
        conn.close()

        response = jsonify({'message': 'History created successfully', 'id': history_id})
        response.status_code = 201
        return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8084)
