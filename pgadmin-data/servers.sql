INSERT INTO public.server (user_id, servergroup_id, name, host, port, maintenance_db, username, password, ssl_mode)
VALUES
    (1, 1, 'Users Database', 'users-db', 5432, 'USERS', 'postgres', '123', 'prefer'),
    (1, 1, 'Hospitals Database', 'hospitals-db', 5432, 'HOSPITALS', 'postgres', '123', 'prefer'),
    (1, 1, 'Schedules Database', 'schedules-db', 5432, 'SCHEDULE', 'postgres', '123', 'prefer'),
    (1, 1, 'Documents Database', 'documents-db', 5432, 'DOCUMENTS', 'postgres', '123', 'prefer');
