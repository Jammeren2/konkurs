-- Adminer 4.8.1 PostgreSQL 16.4 (Debian 16.4-1.pgdg120+1) dump

\connect "SCHEDULE";

DROP TABLE IF EXISTS "appointments";
DROP SEQUENCE IF EXISTS appointments_id_seq;
CREATE SEQUENCE appointments_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."appointments" (
    "id" integer DEFAULT nextval('appointments_id_seq') NOT NULL,
    "timetable_id" integer,
    "appointment_time" timestamp NOT NULL,
    "user_id" integer NOT NULL,
    CONSTRAINT "appointments_pkey" PRIMARY KEY ("id")
) WITH (oids = false);

CREATE INDEX "idx_appointments_time" ON "public"."appointments" USING btree ("appointment_time");

INSERT INTO "appointments" ("id", "timetable_id", "appointment_time", "user_id") VALUES
(9,	7,	'2024-10-03 11:00:00',	10);

DROP TABLE IF EXISTS "timetable";
DROP SEQUENCE IF EXISTS timetable_id_seq;
CREATE SEQUENCE timetable_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."timetable" (
    "id" integer DEFAULT nextval('timetable_id_seq') NOT NULL,
    "hospital_id" integer NOT NULL,
    "doctor_id" integer NOT NULL,
    "start_time" timestamp NOT NULL,
    "end_time" timestamp NOT NULL,
    "room" character varying(255) NOT NULL,
    CONSTRAINT "timetable_pkey" PRIMARY KEY ("id")
) WITH (oids = false);

CREATE INDEX "idx_timetable_doctor" ON "public"."timetable" USING btree ("doctor_id");

INSERT INTO "timetable" ("id", "hospital_id", "doctor_id", "start_time", "end_time", "room") VALUES
(7,	2,	12,	'2024-10-03 11:00:00',	'2024-10-03 13:00:00',	'string'),
(8,	2,	12,	'2024-10-03 11:00:00',	'2024-10-03 13:00:00',	'string'),
(9,	2,	12,	'2024-10-03 11:00:00',	'2024-10-03 13:00:00',	'string');

ALTER TABLE ONLY "public"."appointments" ADD CONSTRAINT "appointments_timetable_id_fkey" FOREIGN KEY (timetable_id) REFERENCES timetable(id) ON DELETE CASCADE NOT DEFERRABLE;

-- 2024-10-22 09:18:12.289368+00