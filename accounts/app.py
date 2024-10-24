from flask import Flask, request, jsonify
# from flask_restx import Api, Resource, fields, Namespace
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, decode_token
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from urllib.parse import urlparse
import os
from flasgger import Swagger


# Инициализация приложения Flask
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['SWAGGER'] = {
    'title': 'Account API',
    'uiversion': 3
}
swagger = Swagger(app, template_file='model.yaml')
jwt = JWTManager(app)
# authorizations = {
#     'Bearer': {
#         'type': 'apiKey',
#         'in': 'header',
#         'name': 'Authorization',
#         'description': 'Вставьте токен в формате: Bearer токен'
#     }
# }

# api = Api(app, 
#           version='1337.0', 
#           title='Account API', 
#           description='API для управления аккаунтами',
#           authorizations=authorizations,
#           security='Bearer')

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


# auth_ns = Namespace('Authorization', description='SignIn, SignUp, SignOut, Validate, Refresh')
# api.add_namespace(auth_ns, path='/Authentication')

# Swagger модели
# signup_model = auth_ns.model('SignUp', {
#     'lastName': fields.String(required=True, description='Фамилия пользователя'),
#     'firstName': fields.String(required=True, description='Имя пользователя'),
#     'username': fields.String(required=True, description='Имя для входа'),
#     'password': fields.String(required=True, description='Пароль пользователя')
# })

# signin_model = auth_ns.model('SignIn', {
#     'username': fields.String(required=True, description='Имя для входа'),
#     'password': fields.String(required=True, description='Пароль пользователя')
# })

# refresh_model = auth_ns.model('Refresh', {
#     'refreshToken': fields.String(required=True, description='Токен для обновления')
# })

# update_model = api.model('UpdateAccount', {
#     'lastName': fields.String(description='Новая фамилия'),
#     'firstName': fields.String(description='Новое имя'),
#     'password': fields.String(description='Новый пароль')
# })


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

@app.route('/api/Authentication/SignUp', methods=['POST'])
def sign_up():
    data = request.json
    username = data['username']

    # Проверяем, существует ли пользователь
    if find_user_by_username(username):
        return jsonify({'message': 'User already exists'}), 400

    # Создаем пользователя
    user_id = create_user(data)
    return jsonify({'message': 'Account created', 'user_id': user_id}), 201



@app.route('/api/Authentication/SignIn', methods=['POST'])
def sign_in():
    data = request.json
    username = data['username']
    password = data['password']

    user = find_user_by_username(username)
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    return jsonify({'accessToken': access_token, 'refreshToken': refresh_token}), 200



@app.route('/api/Authentication/SignOut', methods=['PUT'])
@jwt_required()
def sign_out():
    current_user = get_jwt_identity()
    return jsonify({'message': f'{current_user} signed out successfully'}), 200



@app.route('/api/Authentication/Validate', methods=['GET'])
def validate_token():
    access_token = request.args.get('accessToken')
    try:
        # Расшифровка токена
        decoded_token = decode_token(access_token)
        username = decoded_token['sub']
        
        # Находим пользователя по имени
        user = find_user_by_username(username)
        if not user:
            return {"message": "User not found"}, 404
        
        # Получаем роли пользователя
        roles = get_user_roles(user['id'])
        response_data = {
            "message": "Token is valid",
            "token_data": decoded_token,
            "roles": roles
        }
        response = jsonify(response_data)
        response.status_code = 200
        return response
    except Exception as e:
        return {"message": "Invalid token", "error": str(e)}, 401


@app.route('/api/Authentication/Refresh', methods=['POST'])
def refresh_token():
    data = request.json
    refresh_token = data['refreshToken']
    try:
        decoded_token = decode_token(refresh_token)
        new_access_token = create_access_token(identity=decoded_token['sub'])
        return jsonify({'accessToken': new_access_token}), 200
    except Exception as e:
        return jsonify({"message": "Invalid refresh token", "error": str(e)}), 401



@app.route('/api/Accounts/Me', methods=['GET'])
@jwt_required()
def get_account():
    current_user = get_jwt_identity()
    user = find_user_by_username(current_user)
    
    if user:
        return jsonify({
            'id': user['id'],
            'firstName': user['first_name'],
            'lastName': user['last_name'],
            'username': user['username']
        }), 200
    return jsonify({'message': 'User not found'}), 404



@app.route('/api/Accounts/Update', methods=['PUT'])
@jwt_required()
def update_account11():
    current_user = get_jwt_identity()
    data = request.json
    user = find_user_by_username(current_user)

    if not user:
        return jsonify({'message': 'User not found'}), 404

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

    return jsonify({'message': 'Account updated successfully'}), 200



@app.route('/api/Accounts', methods=['GET'])
@jwt_required()
def get_all_accounts():
    current_user = get_jwt_identity()
    user = find_user_by_username(current_user)

    if not has_role(user['id'], 'Admin'):
        return {'message': 'Access denied'}, 403

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

    response = jsonify(users)
    response.status_code = 200 
    return response


@app.route('/api/Accounts', methods=['POST'])
@jwt_required()
def create_account():
    current_user = get_jwt_identity()
    user = find_user_by_username(current_user)

    if not has_role(user['id'], 'Admin'):
        return {'message': 'Access denied'}, 403

    data = request.json
    user_id = create_user(data)
    return {'message': 'Account created', 'user_id': user_id}, 201


@app.route('/api/Accounts/<int:id>', methods=['PUT'])
@jwt_required()
def update_account(id):
    current_user = get_jwt_identity()
    admin_user = find_user_by_username(current_user)

    if not has_role(admin_user['id'], 'Admin'):
        return {'message': 'Access denied'}, 403

    data = request.json
    user_to_update = find_user_by_id(id)
    if not user_to_update:
        return {'message': 'User not found'}, 404

    conn = get_db_connection()
    cur = conn.cursor()

    if 'username' in data:
        cur.execute("UPDATE users SET username = %s WHERE id = %s", (data['username'], id))

    if 'firstName' in data:
        cur.execute("UPDATE users SET first_name = %s WHERE id = %s", (data['firstName'], id))
    if 'lastName' in data:
        cur.execute("UPDATE users SET last_name = %s WHERE id = %s", (data['lastName'], id))

    if 'password' in data:
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
        cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, id))

    if 'roles' in data:
        cur.execute("DELETE FROM user_roles WHERE user_id = %s", (id,))
        for role in data['roles']:
            cur.execute("INSERT INTO user_roles (user_id, role_name) VALUES (%s, %s)", (id, role))

    conn.commit()
    cur.close()
    conn.close()

    return {'message': 'Account updated successfully'}, 200



@app.route('/api/Accounts/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_account(id):
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


@app.route('/api/Doctors', methods=['GET'])
@jwt_required()
def get_doctors():
    current_user = get_jwt_identity()
    user = find_user_by_username(current_user)

    if not has_role(user['id'], 'Admin'):
        return {'message': 'Access denied'}, 403

    name_filter = request.args.get('nameFilter', '')
    from_param = request.args.get('from', 0, type=int)
    count_param = request.args.get('count', 10, type=int)

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


@app.route('/api/Doctors/<int:id>', methods=['GET'])
@jwt_required()
def get_doctor_by_id(id):
    current_user = get_jwt_identity()
    user = find_user_by_username(current_user)

    if not has_role(user['id'], 'Admin'):
        return {'message': 'Access denied'}, 403

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
