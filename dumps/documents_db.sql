-- Adminer 4.8.1 PostgreSQL 16.4 (Debian 16.4-1.pgdg120+1) dump

\connect "DOCUMENTS";

DROP TABLE IF EXISTS "history";
DROP SEQUENCE IF EXISTS history_id_seq;
CREATE SEQUENCE history_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE "public"."history" (
    "id" integer DEFAULT nextval('history_id_seq') NOT NULL,
    "date" timestamp NOT NULL,
    "pacientid" integer NOT NULL,
    "hospitalid" integer NOT NULL,
    "doctorid" integer NOT NULL,
    "room" character varying(255) NOT NULL,
    "data" text NOT NULL,
    CONSTRAINT "history_pkey" PRIMARY KEY ("id")
) WITH (oids = false);

INSERT INTO "history" ("id", "date", "pacientid", "hospitalid", "doctorid", "room", "data") VALUES
(4,	'2024-10-21 10:00:00',	10,	2,	12,	'2',	'Routine check-up'),
(5,	'2024-10-21 10:00:00',	10,	2,	12,	'2',	'Routine check-up'),
(6,	'2024-10-21 10:00:00',	10,	2,	12,	'2',	'Routine check-up'),
(7,	'2024-10-21 10:00:00',	10,	2,	12,	'2',	'Routine check-up'),
(3,	'2024-10-22 10:00:00',	10,	2,	12,	'2',	'Follow-up check-up');

-- 2024-10-22 09:17:51.772504+00