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
  - **Email**: `postgres`
  - **Пароль**: `123`

- **Примечание**: В Adminer можно вручную выбрать базу данных для подключения из следующих вариантов:
  - `users-db` — База данных пользователей (порт 5432)
  - `hospitals-db` — База данных больниц (порт 5432)
  - `schedules-db` — База данных расписаний (порт 5432)
  - `documents-db` — База данных документов (порт 5432)

### pgAdmin:
- **pgAdmin**: [http://localhost:8181](http://localhost:8181)
  - **Email**: `admin@admin.com`
  - **Пароль**: `admin`

Подключенные базы данных:
- **Users DB** (хост: `users-db`, порт: 5432)
- **Hospitals DB** (хост: `hospitals-db`, порт: 5432)
- **Schedules DB** (хост: `schedules-db`, порт: 5432)
- **Documents DB** (хост: `documents-db`, порт: 5432)

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