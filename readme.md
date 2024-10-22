# Проект: Управление базами данных и сервисами

## Основное задание:

1. **Account URL**: [http://localhost:8081/ui-swagger](http://localhost:8081/ui-swagger)
2. **Hospital URL**: [http://localhost:8082/ui-swagger](http://localhost:8082/ui-swagger)
3. **Timetable URL**: [http://localhost:8083/ui-swagger](http://localhost:8083/ui-swagger)
4. **Document URL**: [http://localhost:8084/ui-swagger](http://localhost:8084/ui-swagger)

## Дополнительное задание (ОТсутствует):

1. **ElasticSearch URL**: [http://elasticsearch-service/](http://elasticsearch-service/)
2. **Kibana URL**: [http://kibana-service/](http://kibana-service/)

## Доступ к базам данных:

### Adminer:
Adminer предоставляет простой веб-интерфейс для работы с каждой базой данных. Для доступа используйте ссылки ниже:

- **Adminer (для всех БД)**: [http://localhost:8180](http://localhost:8180)

**Примечание**: В Adminer можно вручную выбрать базу данных для подключения из следующих вариантов:
  - `users-db` — База данных пользователей (порт 5431)
  - `hospitals-db` — База данных больниц (порт 5432)
  - `schedules-db` — База данных расписаний (порт 5433)
  - `documents-db` — База данных документов (порт 5434)

### pgAdmin:
pgAdmin — это мощный веб-интерфейс для управления PostgreSQL базами данных. При входе в pgAdmin сразу будут добавлены все четыре сервера.

- **pgAdmin**: [http://localhost:5050](http://localhost:5050)
  - **Email**: `admin@admin.com`
  - **Пароль**: `admin`

Подключенные базы данных:
- **Users DB** (хост: `users-db`, порт: 5431)
- **Hospitals DB** (хост: `hospitals-db`, порт: 5432)
- **Schedules DB** (хост: `schedules-db`, порт: 5433)
- **Documents DB** (хост: `documents-db`, порт: 5434)

## Использование Swagger UI:
При использовании Swagger UI для авторизации необходимо вводить токен в формате:

- **Bearer <токен>**


Например, если ваш токен — `abc123`, введите:

- **Bearer abc123**