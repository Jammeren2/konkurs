from flask import Flask, request, jsonify, abort
from flask_restx import Api, Resource, fields, Namespace
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import requests
from urllib.parse import urlparse
import os
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
api = Api(app, version='1.0', title='Schedule API', description='API для управления расписанием', authorizations=authorizations, security='Bearer')

# Модели для Swagger
timetable_model = api.model('Timetable', {
    'hospitalId': fields.Integer(required=True, description='ID больницы'),
    'doctorId': fields.Integer(required=True, description='ID врача'),
    'from': fields.DateTime(required=True, description='Начало расписания'),
    'to': fields.DateTime(required=True, description='Конец расписания'),
    'room': fields.String(required=True, description='Кабинет')
})

appointment_model = api.model('Appointment', {
    'time': fields.DateTime(required=True, description='Время записи на приём')
})
room_schedule_params = api.parser()
room_schedule_params.add_argument('from_time', type=str, required=True, help='Начало периода в формате ISO 8601', location='args')
room_schedule_params.add_argument('to_time', type=str, required=True, help='Конец периода в формате ISO 8601', location='args')


appointment1 = Namespace('Талоны', description='GetAppointments, CreateAppointments, DeleteAppointments')
timetables = Namespace('Расписание', description='CreateTimetable, Update, DeteteTimetable, DeleteDoctor, DeleteHospital, GetByDoctor, GetByRoom')


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


@timetables.route('/')
class TimetableList(Resource):
    @jwt_required()
    @api.expect(timetable_model)
    def post(self):
        """Создание новой записи в расписании"""
        token = request.headers.get('Authorization').split()[1]
        validate_roles(token, ['Admin', 'Manager'])

        data = request.json
        
        # Проверка формата ISO8601 и преобразование в datetime
        try:
            from_time = datetime.fromisoformat(data['from'])
            to_time = datetime.fromisoformat(data['to'])
        except ValueError:
            abort(400, 'Дата должна быть в формате ISO 8601')

        # Проверка кратности 30 минут и времени
        if (from_time.minute % 30 != 0 or to_time.minute % 30 != 0 or
                from_time.second != 0 or to_time.second != 0 or
                (to_time - from_time).total_seconds() > 12 * 3600):
            abort(400, 'Время некорректно, должно быть кратно 30 минутам')

        # Проверка существования доктора по ID
        doctorId = data['doctorId']
        headers = {"Authorization": f"Bearer {token}"}
        doctor_response = requests.get(f'http://users-service:8081/api/Doctors/{doctorId}', headers=headers)
        
        if doctor_response.status_code != 200:
            abort(500, 'Ошибка при проверке доктора')

        doctor = doctor_response.json()
        if doctor['id'] != doctorId:
            abort(404, 'Доктор с таким id не найден')

        # Проверка существования больницы
        hospitalId = data['hospitalId']
        hospital_response = requests.get(f'http://hospitals-service:8082/api/Hospitals/{hospitalId}', headers=headers)
        if hospital_response.status_code != 200:
            abort(500, 'Ошибка при проверке больницы')

        hospital = hospital_response.json()
        if hospital['id'] != hospitalId or hospital['is_deleted']:
            abort(404, 'Больница с таким id не найдена или удалена')

        # Проверка существования кабинета
        room_name = data['room']
        rooms_response = requests.get(f'http://hospitals-service:8082/api/Hospitals/{hospitalId}/Rooms', headers=headers)
        if rooms_response.status_code != 200:
            abort(500, 'Ошибка при проверке кабинета')

        rooms = rooms_response.json()
        room_exists = any(room['room_name'] == room_name for room in rooms)

        if not room_exists:
            abort(404, 'Кабинет с таким названием не найден в указанной больнице')

        # Добавление записи в таблицу timetable
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO timetable (hospital_id, doctor_id, start_time, end_time, room)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        ''', (hospitalId, doctorId, from_time, to_time, data['room']))
        new_id = cur.fetchone()['id']
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'id': new_id})



# PUT /api/Timetable/{id} - обновление расписания
@timetables.route('/<int:id>')
class Timetable(Resource):
    @jwt_required()
    @api.expect(timetable_model)
    def put(self, id):
        """Обновление записи расписания"""
        token = request.headers.get('Authorization').split()[1]
        validate_roles(token, ['Admin', 'Manager'])

        data = request.json
        from_time = datetime.fromisoformat(data['from'])
        to_time = datetime.fromisoformat(data['to'])

        # Проверка корректности времени
        if (from_time.minute % 30 != 0 or to_time.minute % 30 != 0 or
                from_time.second != 0 or to_time.second != 0 or
                (to_time - from_time).total_seconds() > 12 * 3600):
            abort(400, 'Время некорректно')

        # Проверка существования доктора по ID
        doctorId = data['doctorId']
        headers = {"Authorization": f"Bearer {token}"}
        doctor_response = requests.get(f'http://users-service:8081/api/Doctors/{doctorId}', headers=headers)
        
        if doctor_response.status_code != 200:
            abort(500, 'Ошибка при проверке доктора')

        doctor = doctor_response.json()
        if doctor['id'] != doctorId:
            abort(404, 'Доктор с таким id не найден')

        # Проверка существования больницы
        hospitalId = data['hospitalId']
        hospital_response = requests.get(f'http://hospitals-service:8082/api/Hospitals/{hospitalId}', headers=headers)
        if hospital_response.status_code != 200:
            abort(500, 'Ошибка при проверке больницы')

        hospital = hospital_response.json()
        if hospital['id'] != hospitalId or hospital['is_deleted']:
            abort(404, 'Больница с таким id не найдена или удалена')


        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            UPDATE timetable SET hospital_id=%s, doctor_id=%s, start_time=%s, end_time=%s, room=%s
            WHERE id=%s
        ''', (data['hospitalId'], data['doctorId'], from_time, to_time, data['room'], id))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'message': 'Запись обновлена'})

    @jwt_required()
    def delete(self, id):
        """ Удаление записи расписания"""
        token = request.headers.get('Authorization').split()[1]
        validate_roles(token, ['Admin', 'Manager'])

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM timetable WHERE id=%s', (id,))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'message': 'Запись удалена'})


# DELETE /api/Timetable/Doctor/{id} - удаление всех записей расписания врача
@timetables.route('/Doctor/<int:doctor_id>')
class TimetableDoctor(Resource):
    @jwt_required()
    def delete(self, doctor_id):
        """Удаление записей расписания доктора"""
        token = request.headers.get('Authorization').split()[1]
        validate_roles(token, ['Admin', 'Manager'])

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM timetable WHERE doctor_id=%s', (doctor_id,))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'message': 'Записи врача удалены'})


# DELETE /api/Timetable/Hospital/{id} - удаление всех записей расписания больницы
@timetables.route('/Hospital/<int:hospital_id>')
class TimetableHospital(Resource):
    @jwt_required()
    def delete(self, hospital_id):
        """Удаление записей расписания больницы"""
        token = request.headers.get('Authorization').split()[1]
        validate_roles(token, ['Admin', 'Manager'])

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM timetable WHERE hospital_id=%s', (hospital_id,))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'message': 'Записи больницы удалены'})


# GET /api/Timetable/Hospital/{id} - получение расписания больницы
@timetables.route('/Hospital/<int:hospital_id>')
class HospitalSchedule(Resource):
    @jwt_required()
    def get(self, hospital_id):
        """Получение расписания больницы по Id"""
        token = request.headers.get('Authorization').split()[1]
        validate_roles(token, ['Admin', 'Manager', 'Doctor', 'User'])

        from_time = request.args.get('from')
        to_time = request.args.get('to')
        
        query = '''
            SELECT * FROM timetable WHERE hospital_id = %s
        '''
        params = [hospital_id]

        # Добавляем временные параметры только если они указаны
        if from_time:
            query += ' AND start_time >= %s'
            params.append(from_time)
        
        if to_time:
            query += ' AND end_time <= %s'
            params.append(to_time)
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        schedules = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(schedules)



# GET /api/Timetable/Doctor/{id} - получение расписания врача
@timetables.route('/Doctor/<int:doctor_id>')
class DoctorSchedule(Resource):
    @jwt_required()
    def get(self, doctor_id):
        """Получение расписания врача по Id"""
        identity = get_jwt_identity()

        from_time = request.args.get('from')
        to_time = request.args.get('to')

        query = '''
            SELECT * FROM timetable WHERE doctor_id = %s
        '''
        params = [doctor_id]

        # Добавляем временные параметры только если они указаны
        if from_time:
            query += ' AND start_time >= %s'
            params.append(from_time)
        
        if to_time:
            query += ' AND end_time <= %s'
            params.append(to_time)
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        schedules = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(schedules)


@timetables.route('/Hospital/<int:hospital_id>/Room/<string:room_name>')
class RoomSchedule(Resource):
    @jwt_required()
    @api.expect(room_schedule_params)
    def get(self, hospital_id, room_name):
        """Получение расписания кабинета больницы"""
        identity = get_jwt_identity()
        token = request.headers.get('Authorization').split()[1]
        validate_roles(token, ['Admin', 'Manager', 'Doctor'])

        from_time = request.args.get('from_time')
        to_time = request.args.get('to_time')

        query = '''
            SELECT * FROM timetable WHERE 
                hospital_id = %s AND
                room = %s AND
                start_time >= %s AND
                end_time <= %s
        '''
        params = [hospital_id, room_name, from_time, to_time]
        print(f"Executing query: {query} with params: {params}")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        schedules = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(schedules)


@appointment1.route('/Timetable/<int:id>/Appointments')
class AppointmentCreate(Resource):
    @jwt_required()
    @api.expect(appointment_model)
    def post(self, id):
        """Записаться на приём"""
        identity = get_jwt_identity()
        token = request.headers.get('Authorization').split()[1]
        data = request.json
        # Parse the time and convert it to UTC as a naive datetime
        appointment_time = datetime.fromisoformat(data['time'].replace('Z', '+00:00')).replace(tzinfo=None)

        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch the timetable and ensure start_time and end_time are naive
        cur.execute('SELECT * FROM timetable WHERE id=%s', (id,))
        timetable = cur.fetchone()

        if timetable is None or not (
            timetable['start_time'].replace(tzinfo=None) <= appointment_time < timetable['end_time'].replace(tzinfo=None)
        ):
            abort(400, 'Некорректное время для записи')

        # Check if there's already an appointment at that time
        cur.execute('SELECT * FROM appointments WHERE timetable_id=%s AND appointment_time=%s', (id, appointment_time))
        if cur.fetchone():
            abort(400, 'Время уже занято')


        url = f"http://users-service:8081/api/Accounts/Me"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(url, headers=headers)
        user_id = response.json().get("id")

        # Insert the new appointment
        cur.execute('''
            INSERT INTO appointments (timetable_id, appointment_time, user_id)
            VALUES (%s, %s, %s) RETURNING id
        ''', (id, appointment_time, user_id))
        new_id = cur.fetchone()['id']
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'id': new_id})

    @jwt_required()
    def get(self, id):
        """Получение свободных талонов на приём."""
        identity = get_jwt_identity()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM timetable WHERE id=%s
        ''', (id,))
        timetable = cur.fetchone()

        if timetable is None:
            abort(404, 'Запись не найдена')

        # Вычисление доступных талонов (каждые 30 минут)
        start_time = timetable['start_time']
        end_time = timetable['end_time']
        appointments = []

        # Получение всех существующих записей для данного расписания
        cur.execute('''
            SELECT appointment_time FROM appointments WHERE timetable_id=%s
        ''', (id,))
        existing_appointments = {row['appointment_time'] for row in cur.fetchall()}

        current_time = start_time
        while current_time < end_time:
            # Проверяем, занято ли время
            if current_time not in existing_appointments:
                appointments.append(current_time.isoformat())
            current_time += timedelta(minutes=30)

        cur.close()
        conn.close()

        return jsonify(appointments)


# DELETE /api/Appointment/{id} - отмена записи
@appointment1.route('/Appointment/<int:id>')
class AppointmentDelete(Resource):
    @jwt_required()
    def delete(self, id):
        """Отменить запись на приём"""
        identity = get_jwt_identity()
        token = request.headers.get('Authorization').split()[1]

        conn = get_db_connection()
        cur = conn.cursor()

        # Получение информации о пользователе по токену
        url = "http://users-service:8081/api/Accounts/Me"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        user_info = response.json()
        user_id = user_info.get("id")
        user_roles = user_info.get("roles")

        # Проверка, что запись существует
        cur.execute('SELECT * FROM appointments WHERE id=%s', (id,))
        appointment = cur.fetchone()

        if appointment is None:
            abort(404, 'Запись не найдена')

        # Проверка прав на удаление
        if user_id != appointment['user_id'] and not any(role in ['Admin', 'Manager'] for role in user_roles):
            abort(403, 'Нет прав для удаления этой записи')

        # Удаление записи
        cur.execute('DELETE FROM appointments WHERE id=%s', (id,))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'message': 'Запись отменена'})





api.add_namespace(appointment1, path='/api')
api.add_namespace(timetables, path='/api/Timetable')


# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8083)
