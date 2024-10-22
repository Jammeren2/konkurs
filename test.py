import requests
from termcolor import colored
import os
BASE_URL_ACCOUNTS = "http://127.0.0.1:8081"
BASE_URL_HOSPITALS = "http://127.0.0.1:8082"
BASE_URL_SCHEDULE = "http://127.0.0.1:8083"
BASE_URL_HISTORY = "http://127.0.0.1:8084"
os.system('color')
def sign_up():
    url = f"{BASE_URL_ACCOUNTS}/api/Authentication/SignUp"
    data = {
        "lastName": "Doe1",
        "firstName": "John1",
        "username": "johndoe1",
        "password": "admin"
    }
    response = requests.post(url, json=data)
    
    try:
        response_json = response.json()
    except requests.exceptions.JSONDecodeError:
        print(colored('Sign Up:', 'black', 'on_white'),f" {response.status_code}, Response is not in JSON format: {response.text}")
        return
    
    print(f"Sign Up: {response.status_code}, {response_json}")

def sign_in():
    url = f"{BASE_URL_ACCOUNTS}/api/Authentication/SignIn"
    data = {
        "username": "admin",
        "password": "admin"
    }
    response = requests.post(url, json=data)
    tokens = response.json()
    print(colored('Sign In:', 'black', 'on_white'),f" {response.status_code}, {tokens}")
    return tokens.get("accessToken"), tokens.get("refreshToken")

def sign_out(access_token):
    url = f"{BASE_URL_ACCOUNTS}/api/Authentication/SignOut"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.put(url, headers=headers)
    print(colored('Sign Out:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")

def get_account_data(access_token):
    url = f"{BASE_URL_ACCOUNTS}/api/Accounts/Me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    print(colored('Get Account Data:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")

def update_account(access_token):
    url = f"{BASE_URL_ACCOUNTS}/api/Accounts/Update"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "lastName": "DoeUpdated",
        "firstName": "JohnUpdated",
        "password": "newpassword123"
    }
    response = requests.put(url, json=data, headers=headers)
    print(colored('Update Account:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")

def refresh_token(refresh_token):
    url = f"{BASE_URL_ACCOUNTS}/api/Authentication/Refresh"
    data = {
        "refreshToken": refresh_token
    }
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        new_access_token = response.json().get("accessToken")
        print(colored('Refresh Token:', 'black', 'on_white'),f" {response.status_code}, New Access Token: {new_access_token}")
        return new_access_token
    else:
        print(colored('Refresh Token:', 'black', 'on_white'),f" {response.status_code}, {response.text}")
        return None

def validate_token(access_token):
    url = f"{BASE_URL_ACCOUNTS}/api/Authentication/Validate"
    params = {
        "accessToken": access_token
    }
    response = requests.get(url, params=params)
    print(colored('Validate Token:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")

def get_all_accounts(access_token):
    url = f"{BASE_URL_ACCOUNTS}/api/Accounts"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "from": 0,  # Начало выборки
        "count": 10  # Размер выборки
    }
    response = requests.get(url, headers=headers, params=params)
    print(colored('Get All Accounts:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")

def create_admin_account(access_token):
    url = f"{BASE_URL_ACCOUNTS}/api/Accounts"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "lastName": "manager",
        "firstName": "manager",
        "username": "manager",
        "password": "manager",
        "roles": ["Manager"]
    }
    response = requests.post(url, json=data, headers=headers)
    print(colored('Create Admin Account:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")

def get_doctors(access_token):
    url = f"{BASE_URL_ACCOUNTS}/api/Doctors"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "nameFilter": "doctor",  # Фильтр по имени
        "from": 0,            # Начало выборки
        "count": 10           # Размер выборки
    }
    response = requests.get(url, headers=headers, params=params)
    print(colored('Get Doctors:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")

def get_doctor(access_token, id):
    url = f"{BASE_URL_ACCOUNTS}/api/Doctors/{id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    print(colored('Get Doctor by ID:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")









def get_hospitals(access_token):
    url = f"{BASE_URL_HOSPITALS}/api/Hospitals"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    print(colored('Get Hospitals:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")


def create_hospital(access_token):
    url = f"{BASE_URL_HOSPITALS}/api/Hospitals"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "name": "ГБ №3",
        "address": "г. Новосибирск",
        "contactPhone": "+77777773333",
        "rooms": ["1", "2", "3", "4"],
    }
    response = requests.post(url, json=data, headers=headers)
    print(colored('Create Hospital:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")

def delete_hospital(access_token):
    url = f"{BASE_URL_HOSPITALS}/api/Hospitals"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.delete(url, headers=headers)
    print(colored('Delete Hospital:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")

def delete_hospital(access_token, hospital_id):
    url = f"{BASE_URL_HOSPITALS}/api/Hospitals/{hospital_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.delete(url, headers=headers)
    print(colored('Delete Hospital:', 'black', 'on_white'), f" {response.status_code}, {response.json()}")

def get_hospitals_by_id(access_token, hospital_id):
    url = f"{BASE_URL_HOSPITALS}/api/Hospitals/{hospital_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    print(colored('Get Hospital by id:', 'black', 'on_white'), f" {response.status_code}, {response.json()}")


def get_rooms_by_id(access_token, hospital_id):
    url = f"{BASE_URL_HOSPITALS}/api/Hospitals/{hospital_id}/Rooms"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    print(colored('Get rooms by id:', 'black', 'on_white'), f" {response.status_code}, {response.json()}")

def correct_hospitals_by_id(access_token, hospital_id):
    url = f"{BASE_URL_HOSPITALS}/api/Hospitals/{hospital_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "name": "ГБ №22",
        "address": "г. Новосибирск, ул. Такая-какая-есть, д. такой-же",
        "contactPhone": "+78005553535",
        "rooms": ["1", "2", "3", "4"],
    }
    response = requests.put(url, json=data, headers=headers)
    print(colored('Correct Hospital:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")









def new_timetable(access_token):
    url = f"{BASE_URL_SCHEDULE}/api/Timetable"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "hospitalId": 2,
        "doctorId": 12,
        "from": "2024-10-03T11:00:00",
        "to": "2024-10-03T13:00:00",
        "room": "string"
    }
    response = requests.post(url, json=data, headers=headers)
    print(colored('New Timetable:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")

def edit_timetable(access_token, id):
    url = f"{BASE_URL_SCHEDULE}/api/Timetable/{id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "hospitalId": 2,
        "doctorId": 12,
        "from": "2024-10-03T11:00:00",
        "to": "2024-10-03T13:00:00",
        "room": "no_string"
    }
    response = requests.put(url, json=data, headers=headers)
    print(colored('Edit Timetable:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")

def delete_timetable(access_token, id):
    url = f"{BASE_URL_SCHEDULE}/api/Timetable/{id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.delete(url, headers=headers)
    print(colored('Delete timetable:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")

def delete_timetable_by_doctor(access_token, id):
    url = f"{BASE_URL_SCHEDULE}/api/Timetable/Doctor/{id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.delete(url, headers=headers)
    print(colored('Delete timetable by doctor:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")

def delete_timetable_by_hospital(access_token, id):
    url = f"{BASE_URL_SCHEDULE}/api/Timetable/Hospital/{id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.delete(url, headers=headers)
    print(colored('Delete timetable by hospital:', 'black', 'on_white'),f" {response.status_code}, {response.json()}")

def get_timetable_by_hospital(access_token, id):
    url = f"{BASE_URL_SCHEDULE}/api/Timetable/Hospital/{id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    print(colored('Get timetable by hospital', 'black', 'on_white'), f" {response.status_code}, {response.json()}")

def get_timetable_by_doctor(access_token, id):
    url = f"{BASE_URL_SCHEDULE}/api/Timetable/Doctor/{id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    print(colored('Get timetable by doctor', 'black', 'on_white'), f" {response.status_code}, {response.json()}")

def get_timetable_by_room(access_token, hospital_id, room_id):
    url = f"{BASE_URL_SCHEDULE}/api/Timetable/Hospital/{hospital_id}/Room/{room_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    print(colored('Get timetable by room', 'black', 'on_white'), f" {response.status_code}, {response.json()}")


def get_Appointments(access_token, id):
    url = f"{BASE_URL_SCHEDULE}/api/Timetable/{id}/Appointments"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    print(colored('Get Appointments', 'black', 'on_white'), f" {response.status_code}, {response.json()}")

def add_Appointments(access_token, id):
    url = f"{BASE_URL_SCHEDULE}/api/Timetable/{id}/Appointments"
    headers = {
        "Authorization": f"Bearer {access_token}",
        'Content-Type': 'application/json'
    }
    data = {
    'time': '2024-10-03T11:00:00Z'
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        print(colored('Запись на приём успешно создана', 'black', 'on_white'), f" {response.status_code}, {response.json()}")
        return response.json().get("id")


def delete_Appointments(access_token, id):
    url = f"{BASE_URL_SCHEDULE}/api/Appointment/{id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.delete(url, headers=headers)
    print(colored('удаление записи', 'black', 'on_white'), f" {response.status_code}, {response.json()}")






def get_AccountHistory(access_token, id):
    url = f"{BASE_URL_HISTORY}/api/History/Account/{id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(colored('История аккаунта успешно получена', 'black', 'on_white'), f" {response.status_code}, {response.json()}")
    else:
        print(colored('Ошибка при получении истории аккаунта', 'red'), f" {response.status_code}, {response.json()}")

def get_History(access_token, id):
    url = f"{BASE_URL_HISTORY}/api/History/{id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(colored('Подробная история успешно получена', 'black', 'on_white'), f" {response.status_code}, {response.json()}")
    else:
        print(colored('Ошибка при получении подробной истории', 'red'), f" {response.status_code}, {response.json()}")

def add_History(access_token):
    url = f"{BASE_URL_HISTORY}/api/History"
    headers = {
        "Authorization": f"Bearer {access_token}",
        'Content-Type': 'application/json'
    }
    data = {
        "date": "2024-10-21T10:00:00Z",
        "pacientId": 10,
        "hospitalId": 2,
        "doctorId": 12,
        "room": "2",
        "data": "Routine check-up"
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print(colored('История успешно создана', 'black', 'on_white'), f" {response.status_code}, {response.json()}")
        return response.json().get("id")
    else:
        print(colored('Ошибка при создании истории', 'red'), f" {response.status_code}, {response.json()}")

def update_History(access_token, id):
    url = f"{BASE_URL_HISTORY}/api/History/{id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        'Content-Type': 'application/json'
    }
    data = {
        "date": "2024-10-22T10:00:00Z",
        "pacientId": 10,
        "hospitalId": 2,
        "doctorId": 12,
        "room": "2",
        "data": "Follow-up check-up"
    }
    response = requests.put(url, json=data, headers=headers)
    if response.status_code == 200:
        print(colored('История успешно обновлена', 'black', 'on_white'), f" {response.status_code}, {response.json()}")
    else:
        print(colored('Ошибка при обновлении истории', 'red'), f" {response.status_code}, {response.json()}")

def delete_History(access_token, id):
    url = f"{BASE_URL_HISTORY}/api/History/{id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        print(colored('История успешно удалена', 'black', 'on_white'), f" {response.status_code}")
    else:
        print(colored('Ошибка при удалении истории', 'red'), f" {response.status_code}, {response.json()}")


if __name__ == "__main__":
    # 1. Регистрация нового пользователя
    # sign_up()

    # 2. Вход в систему (получение токенов)
    access_token, refresh_token_value = sign_in()
    if access_token:
        print('\n')
        get_account_data(access_token)
        print('\n')

        #update_account(access_token)

        validate_token(access_token)
        print('\n')

        if refresh_token_value:
            new_access_token = refresh_token(refresh_token_value)
            if new_access_token:
                get_account_data(new_access_token)
                print('\n')

        get_all_accounts(access_token)
        print('\n')

        #create_admin_account(access_token)
        print('\n')

        get_doctors(access_token)

        get_doctor(access_token, 12)
        print('\n')

        print(colored('API HOSPITAL', 'black', 'on_green'))
        print('\n')


        #create_hospital(access_token)
        # print('\n')

        get_hospitals(access_token)
        print('\n')


        #delete_hospital(access_token, 1)

        get_hospitals_by_id(access_token, 2)
        print('\n')

        get_rooms_by_id(access_token, 2)
        print('\n')

        correct_hospitals_by_id(access_token, 2)
        print('\n')


        print(colored('API SCHEDULE', 'black', 'on_green'))
        print('\n')

        #new_timetable(access_token)

        edit_timetable(access_token, 2)
        print('\n')

        #delete_timetable(access_token, 1)

        #delete_timetable_by_doctor(access_token, 12)

        #delete_timetable_by_hospital(access_token, 2)

        get_timetable_by_hospital(access_token, 2)
        print('\n')

        get_timetable_by_doctor(access_token, 12)
        print('\n')

        get_Appointments(access_token, 7)
        print('\n')

        Appointments_id = add_Appointments(access_token, 7)

        #delete_Appointments(access_token, Appointments_id)

        print(colored('API DOCUMENTS', 'black', 'on_green'))
        print('\n')

        get_AccountHistory(access_token, 10)
        print('\n')

        # add_History(access_token)
        # print('\n')

        update_History(access_token, 3)
        print('\n')

        get_History(access_token, 10)





        print('\n')
        sign_out(access_token)
