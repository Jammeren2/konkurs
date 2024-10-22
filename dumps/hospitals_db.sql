-- Adminer 4.8.1 PostgreSQL 16.4 (Debian 16.4-1.pgdg120+1) dump

\connect "HOSPITALS";

DROP TABLE IF EXISTS "hospitals";
DROP SEQUENCE IF EXISTS hospitals_id_seq;
CREATE SEQUENCE hospitals_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."hospitals" (
    "id" integer DEFAULT nextval('hospitals_id_seq') NOT NULL,
    "name" character varying(255) NOT NULL,
    "address" character varying(255),
    "contact_phone" character varying(50),
    "is_deleted" boolean DEFAULT false,
    CONSTRAINT "hospitals_pkey" PRIMARY KEY ("id")
) WITH (oids = false);

INSERT INTO "hospitals" ("id", "name", "address", "contact_phone", "is_deleted") VALUES
(1,	'ГБ №1',	'г. Новосибирск, ул. Говновозная, д. Петушар',	'+77777777777',	't'),
(2,	'ГБ №22',	'г. Новосибирск, ул. Такая-какая-есть, д. такой-же',	'+78005553535',	'f');

DROP TABLE IF EXISTS "rooms";
DROP SEQUENCE IF EXISTS rooms_id_seq;
CREATE SEQUENCE rooms_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."rooms" (
    "id" integer DEFAULT nextval('rooms_id_seq') NOT NULL,
    "hospital_id" integer,
    "room_name" character varying(255) NOT NULL,
    CONSTRAINT "rooms_pkey" PRIMARY KEY ("id")
) WITH (oids = false);

INSERT INTO "rooms" ("id", "hospital_id", "room_name") VALUES
-- (1,	1,	'1'),
-- (2,	1,	'2'),
-- (3,	1,	'3'),
(355,	2,	'1'),
(356,	2,	'2'),
(357,	2,	'3'),
(358,	2,	'4');

ALTER TABLE ONLY "public"."rooms" ADD CONSTRAINT "rooms_hospital_id_fkey" FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE NOT DEFERRABLE;

-- 2024-10-22 09:18:03.496602+00