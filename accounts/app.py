from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, decode_token
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from urllib.parse import urlparse

# Инициализация приложения Flask
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)

# Настройка авторизации для Swagger
authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Вставьте токен в формате: Bearer <токен>'
    }
}

api = Api(app, 
          version='1.0', 
          title='Account Management API', 
          description='API для управления аккаунтами и аутентификацией пользователей',
          authorizations=authorizations,
          security='Bearer')

def get_db_connection():
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

# Модели для документации Swagger
signup_model = api.model('SignUp', {
    'lastName': fields.String(required=True, description='Фамилия пользователя'),
    'firstName': fields.String(required=True, description='Имя пользователя'),
    'username': fields.String(required=True, description='Имя для входа'),
    'password': fields.String(required=True, description='Пароль пользователя')
})

signin_model = api.model('SignIn', {
    'username': fields.String(required=True, description='Имя для входа'),
    'password': fields.String(required=True, description='Пароль пользователя')
})

refresh_model = api.model('Refresh', {
    'refreshToken': fields.String(required=True, description='Токен для обновления')
})

update_model = api.model('UpdateAccount', {
    'lastName': fields.String(description='Новая фамилия'),
    'firstName': fields.String(description='Новое имя'),
    'password': fields.String(description='Новый пароль')
})



def find_user_by_id(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


# Функция для добавления ролей пользователю
def add_roles_to_user(user_id, roles):
    conn = get_db_connection()
    cur = conn.cursor()
    for role in roles:
        cur.execute("SELECT id FROM roles WHERE role_name = %s", (role,))
        role_data = cur.fetchone()
        if role_data:
            role_id = role_data['id']
            cur.execute("INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)", (user_id, role_id))
    conn.commit()
    cur.close()
    conn.close()

def create_user(data):
    conn = get_db_connection()
    cur = conn.cursor()

    # Вставляем пользователя в таблицу users
    cur.execute("""
        INSERT INTO users (first_name, last_name, username, password) 
        VALUES (%s, %s, %s, %s) 
        RETURNING id
    """, (data['firstName'], data['lastName'], data['username'], data['password']))
    
    user_id = cur.fetchone()['id']
    conn.commit()
    add_roles_to_user(user_id, data.get('roles', ['User', 'Doctor']))
    cur.close()
    conn.close()

    return user_id



# Функция для получения ролей пользователя
def get_user_roles(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.role_name FROM roles r
        JOIN user_roles ur ON r.id = ur.role_id
        WHERE ur.user_id = %s
    """, (user_id,))
    roles = [row['role_name'] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return roles

# Функция для проверки наличия роли у пользователя
def has_role(user_id, required_role):
    roles = get_user_roles(user_id)
    return required_role in roles



# Функция для поиска пользователя в базе данных по имени
def find_user_by_username(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

@api.route('/api/Authentication/SignUp')
class SignUp(Resource):
    @api.expect(signup_model)
    def post(self):
        """Регистрация пользователя"""
        data = request.json
        username = data['username']

        # Проверяем, существует ли пользователь
        if find_user_by_username(username):
            return {'message': 'User already exists'}, 400

        # Создаем пользователя
        user_id = create_user(data)
        return {'message': 'Account created', 'user_id': user_id}, 201


@api.route('/api/Authentication/SignUp')
@api.doc(tags=['Authentication'])
class SignUp(Resource):
    @api.expect(signup_model)
    def post(self):
        """Регистрация нового пользователя в системе"""
        data = request.json
        username = data['username']
        if find_user_by_username(username):
            return {'message': 'Пользователь уже существует'}, 400
        user_id = create_user(data)
        return {'message': 'Аккаунт создан', 'user_id': user_id}, 201

@api.route('/api/Authentication/SignIn')
@api.doc(tags=['Authentication'])
class SignIn(Resource):
    @api.expect(signin_model)
    def post(self):
        """Вход пользователя в систему с получением токенов"""
        data = request.json
        username = data['username']
        password = data['password']
        user = find_user_by_username(username)
        if not user or user['password'] != password:
            return {'message': 'Неверные учетные данные'}, 401
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        return {'accessToken': access_token, 'refreshToken': refresh_token}, 200

@api.route('/api/Authentication/SignOut')
@api.doc(tags=['Authentication'])
class SignOut(Resource):
    @jwt_required()
    def put(self):
        """Выход пользователя из системы"""
        current_user = get_jwt_identity()
        return {'message': f'{current_user} вышел из системы'}, 200

@api.route('/api/Authentication/Validate')
@api.doc(tags=['Authentication'])
class ValidateToken(Resource):
    @api.param('accessToken', 'JWT токен для проверки')
    def get(self):
        """Проверка действительности JWT токена"""
        access_token = request.args.get('accessToken')
        try:
            decoded_token = decode_token(access_token)
            username = decoded_token['sub']
            user = find_user_by_username(username)
            if not user:
                return {"message": "Пользователь не найден"}, 404
            roles = get_user_roles(user['id'])
            return {"message": "Токен валидный", "token_data": decoded_token, "roles": roles}, 200
        except Exception as e:
            return {"message": "Невалидный токен", "error": str(e)}, 401

@api.route('/api/Authentication/Refresh')
@api.doc(tags=['Authentication'])
class RefreshToken(Resource):
    @api.expect(refresh_model)
    def post(self):
        """Обновление JWT токена по refresh токену"""
        data = request.json
        refresh_token = data['refreshToken']
        try:
            decoded_token = decode_token(refresh_token)
            new_access_token = create_access_token(identity=decoded_token['sub'])
            return {'accessToken': new_access_token}, 200
        except Exception as e:
            return {"message": "Невалидный refresh токен", "error": str(e)}, 401


# Аккаунты
@api.route('/api/Accounts/Me')
@api.doc(tags=['Accounts'])
class GetAccount(Resource):
    @jwt_required()
    def get(self):
        """Получение данных текущего пользователя"""
        current_user = get_jwt_identity()
        user = find_user_by_username(current_user)
        if user:
            return {'id': user['id'], 'firstName': user['first_name'], 'lastName': user['last_name'], 'username': user['username']}, 200
        return {'message': 'Пользователь не найден'}, 404

@api.route('/api/Accounts/Update')
@api.doc(tags=['Accounts'])
class UpdateAccount(Resource):
    @jwt_required()
    @api.expect(update_model)
    def put(self):
        """Обновление данных текущего пользователя"""
        current_user = get_jwt_identity()
        data = request.json
        user = find_user_by_username(current_user)
        if not user:
            return {'message': 'Пользователь не найден'}, 404
        conn = get_db_connection()
        cur = conn.cursor()
        if 'firstName' in data:
            cur.execute("UPDATE users SET first_name = %s WHERE username = %s", (data['firstName'], current_user))
        if 'lastName' in data:
            cur.execute("UPDATE users SET last_name = %s WHERE username = %s", (data['lastName'], current_user))
        if 'password' in data:
            hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
            cur.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_password, current_user))
        conn.commit()
        cur.close()
        conn.close()
        return {'message': 'Аккаунт успешно обновлен'}, 200

@api.route('/api/Accounts')
@api.doc(tags=['Accounts'])
class GetAllAccounts(Resource):
    @jwt_required()
    def get(self):
        """Получение списка всех пользователей (только для админов)"""
        current_user = get_jwt_identity()
        user = find_user_by_username(current_user)
        if not has_role(user['id'], 'Admin'):
            return {'message': 'Доступ запрещен'}, 403
        from_param = request.args.get('from', 0, type=int)
        count_param = request.args.get('count', 10, type=int)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users LIMIT %s OFFSET %s", (count_param, from_param))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        users = [dict(row) for row in rows]
        for row in users:
            row['created_at'] = row['created_at'].isoformat()
        return jsonify(users), 200

@api.route('/api/Accounts')
class CreateAccount(Resource):
    @jwt_required()
    @api.expect(signup_model)
    def post(self):
        current_user = get_jwt_identity()
        user = find_user_by_username(current_user)

        if not has_role(user['id'], 'Admin'):
            return {'message': 'Access denied'}, 403

        data = request.json
        user_id = create_user(data)
        return {'message': 'Account created', 'user_id': user_id}, 201


@api.route('/api/Accounts/<int:id>')
class UpdateAccountById(Resource):
    @jwt_required()
    @api.expect(signup_model)
    def put(self, id):
        current_user = get_jwt_identity()
        admin_user = find_user_by_username(current_user)

        # Проверка, является ли текущий пользователь администратором
        if not has_role(admin_user['id'], 'Admin'):
            return {'message': 'Access denied'}, 403

        # Получаем данные из запроса
        data = request.json

        # Проверка существования пользователя с указанным id
        user_to_update = find_user_by_id(id)
        if not user_to_update:
            return {'message': 'User not found'}, 404

        conn = get_db_connection()
        cur = conn.cursor()

        # Обновление имени пользователя, если передано
        if 'username' in data:
            cur.execute("UPDATE users SET username = %s WHERE id = %s", (data['username'], id))

        # Обновление имени и фамилии, если переданы
        if 'firstName' in data:
            cur.execute("UPDATE users SET first_name = %s WHERE id = %s", (data['firstName'], id))
        if 'lastName' in data:
            cur.execute("UPDATE users SET last_name = %s WHERE id = %s", (data['lastName'], id))

        # Обновление пароля, если передан
        if 'password' in data:
            hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
            cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, id))

        # Обновление ролей, если переданы
        if 'roles' in data:
            cur.execute("DELETE FROM user_roles WHERE user_id = %s", (id,))
            for role in data['roles']:
                cur.execute("INSERT INTO user_roles (user_id, role_name) VALUES (%s, %s)", (id, role))

        # Применение изменений
        conn.commit()
        cur.close()
        conn.close()

        return {'message': 'Account updated successfully'}, 200


@api.route('/api/Accounts/<int:id>')
class DeleteAccount(Resource):
    @jwt_required()
    def delete(self, id):
        current_user = get_jwt_identity()
        user = find_user_by_username(current_user)

        if not has_role(user['id'], 'Admin'):
            return {'message': 'Access denied'}, 403

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET is_deleted = TRUE WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        
        return {'message': 'Account soft deleted'}, 200

@api.route('/api/Doctors')
class GetDoctors(Resource):
    @jwt_required()
    def get(self):
        # Получаем текущего пользователя
        current_user = get_jwt_identity()

        # Проверяем, есть ли у текущего пользователя права администратора
        user = find_user_by_username(current_user)
        if not user or not has_role(user['id'], 'Admin'):
            return {'message': 'Access denied'}, 403

        # Параметры фильтрации и пагинации
        name_filter = request.args.get('nameFilter', '')
        from_param = request.args.get('from', 0, type=int)
        count_param = request.args.get('count', 10, type=int)

        # Запрос для получения пользователей с ролью Doctor
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, u.first_name, u.last_name, u.username 
            FROM users u
            JOIN user_roles ur ON u.id = ur.user_id
            JOIN roles r ON ur.role_id = r.id
            WHERE r.role_name = 'Doctor' AND (u.first_name ILIKE %s OR u.last_name ILIKE %s)
            LIMIT %s OFFSET %s
        """, (f'%{name_filter}%', f'%{name_filter}%', count_param, from_param))
        
        doctors = cur.fetchall()
        cur.close()
        conn.close()
        response = jsonify(doctors)
        response.status_code = 200
        return response


@api.route('/api/Doctors/<int:id>')
class GetDoctorById(Resource):
    @jwt_required()
    def get(self, id):
        # Получаем текущего пользователя
        current_user = get_jwt_identity()

        # Проверяем, есть ли у текущего пользователя права администратора
        user = find_user_by_username(current_user)
        if not user or not has_role(user['id'], 'Admin'):
            return {'message': 'Access denied'}, 403

        # Запрос для получения пользователя с ролью Doctor по ID
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, u.first_name, u.last_name, u.username
            FROM users u
            JOIN user_roles ur ON u.id = ur.user_id
            JOIN roles r ON ur.role_id = r.id
            WHERE r.role_name = 'Doctor' AND u.id = %s
        """, (id,))
        
        doctor = cur.fetchone()
        cur.close()
        conn.close()

        if doctor:
            response = jsonify(doctor)
            response.status_code = 200
            return response
        return {'message': 'Doctor not found'}, 404


if __name__ == "__main__":
    app.run(port=8081, host='0.0.0.0', debug=True)
