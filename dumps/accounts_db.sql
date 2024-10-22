-- Adminer 4.8.1 PostgreSQL 16.4 (Debian 16.4-1.pgdg120+1) dump

\connect "USERS";

DROP TABLE IF EXISTS "roles";
DROP SEQUENCE IF EXISTS roles_id_seq;
CREATE SEQUENCE roles_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."roles" (
    "id" integer DEFAULT nextval('roles_id_seq') NOT NULL,
    "role_name" character varying(50) NOT NULL,
    CONSTRAINT "roles_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "roles_role_name_key" UNIQUE ("role_name")
) WITH (oids = false);

INSERT INTO "roles" ("id", "role_name") VALUES
(1,	'Admin'),
(2,	'Manager'),
(3,	'Doctor'),
(4,	'User');

DROP TABLE IF EXISTS "user_roles";
CREATE TABLE "public"."user_roles" (
    "user_id" integer NOT NULL,
    "role_id" integer NOT NULL,
    CONSTRAINT "user_roles_pkey" PRIMARY KEY ("user_id", "role_id")
) WITH (oids = false);

INSERT INTO "user_roles" ("user_id", "role_id") VALUES
(10,	4),
(10,	1),
(12,	4),
(12,	3),
(16,	2),
(16,	4),
(15,	4);

DROP TABLE IF EXISTS "users";
DROP SEQUENCE IF EXISTS users_id_seq;
CREATE SEQUENCE users_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."users" (
    "id" integer DEFAULT nextval('users_id_seq') NOT NULL,
    "first_name" character varying(50) NOT NULL,
    "last_name" character varying(50) NOT NULL,
    "username" character varying(50) NOT NULL,
    "password" text NOT NULL,
    "is_deleted" boolean DEFAULT false,
    "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "users_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "users_username_key" UNIQUE ("username")
) WITH (oids = false);

INSERT INTO "users" ("id", "first_name", "last_name", "username", "password", "is_deleted", "created_at") VALUES
(12,	'doctor',	'doctor',	'doctor',	'doctor',	'f',	'2024-10-02 16:09:26.635374'),
(10,	'admin',	'admin',	'admin',	'admin',	'f',	'2024-10-01 12:04:31.155056'),
(15,	'user',	'user',	'user',	'user',	'f',	'2024-10-02 16:30:45.648782'),
(16,	'manager',	'manager',	'manager',	'manager',	'f',	'2024-10-03 14:21:36.325964');

ALTER TABLE ONLY "public"."user_roles" ADD CONSTRAINT "user_roles_role_id_fkey" FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE NOT DEFERRABLE;
ALTER TABLE ONLY "public"."user_roles" ADD CONSTRAINT "user_roles_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE NOT DEFERRABLE;

-- 2024-10-22 09:14:44.601183+00