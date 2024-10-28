# Проект: Управление базами данных и сервисами

## Основное задание:

1. **Account URL**: [http://localhost:8081/ui-swagger](http://localhost:8081/ui-swagger)
2. **Hospital URL**: [http://localhost:8082/ui-swagger](http://localhost:8082/ui-swagger)
3. **Timetable URL**: [http://localhost:8083/ui-swagger](http://localhost:8083/ui-swagger)
4. **Document URL**: [http://localhost:8084/ui-swagger](http://localhost:8084/ui-swagger)


## Доступ к базам данных:

### Adminer:
Adminer предоставляет простой веб-интерфейс для работы с каждой базой данных. Для доступа используйте ссылки ниже:

 - **Adminer**: [http://localhost:8180](http://localhost:8180)
  - **Login**: `postgres`
  - **Pass**: `123`

- **Примечание**: В Adminer можно вручную выбрать базу данных для подключения из следующих вариантов:
  - `users-db` — База данных пользователей
  - `hospitals-db` — База данных больниц
  - `schedules-db` — База данных расписаний
  - `documents-db` — База данных документов

### pgAdmin:
- **pgAdmin**: [http://localhost:8181](http://localhost:8181)
  - **Email**: `admin@admin.com`
  - **Пароль**: `admin`

Подключенные базы данных:
- **Login**: `postgres`
- **Pass**: `123`
- **Users DB** (хост: `users-db`)
- **Hospitals DB** (хост: `hospitals-db`)
- **Schedules DB** (хост: `schedules-db`)
- **Documents DB** (хост: `documents-db`)

## Использование Swagger UI:
При использовании Swagger UI для авторизации необходимо вводить токен в формате:

- **Bearer <токен>**


Например, если ваш токен — `abc123`, введите:

- **Bearer abc123**

## requirements:
- docker
- git


## How to install:

- **git clone https://github.com/Jammeren2/konkurs**
- **cd konkurs**
- **docker compose up -d**