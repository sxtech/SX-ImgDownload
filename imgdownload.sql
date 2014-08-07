CREATE TABLE IF NOT EXISTS "imgdownload" (
"id"  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
"timeflag"  INTEGER,
"sqlstr"  TEXT,
"path"  TEXT,
"banned"  INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS "index_banned"
ON "imgdownload" ("banned" ASC);

CREATE INDEX IF NOT EXISTS "index_timeflag"
ON "imgdownload" ("timeflag" ASC);