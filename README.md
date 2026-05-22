Caido Request Utility (CRU)
---

This tool lets you take a Caido export and turn it into a SQL database for ease of tooling interactions.

## Usage

This is a basic script to import and load data to SQLite
```python
import sqlite3
from pathlib import Path

import cru.csv_to_sql


def main():
    con: sqlite3.Connection = sqlite3.connect("test.db")
    cru.csv_to_sql.create_and_populate_from_csv(con, Path("test.csv"))


if __name__ == "__main__":
    main()
```

Technically this is SQL agnostic, just override `cru.sql_util.execute` to use your DB specific execution logic.

## Idea Roadmap

- Output an HTML page with statistics such as hosts hit, unique routes, etc
- Support for providing a scope for narrowing data aggregation
- Generic insights such as security headers or extracting all observed content security policies to see if they are consistent

*P.s. You should contribute ideas! If you have an idea of what to do with raw request data, open an issue.*

## Reference

Table: `raw_requests`

Description: Raw data that matches the Caido export.

Definition:
```sql
 CREATE TABLE IF NOT EXISTS "raw_requests"
  (
     "id"                   INTEGER NOT NULL,
     "caido_request_id"     INTEGER NOT NULL,
     "host"                 TEXT NOT NULL,
     "method"               TEXT NOT NULL,
     "path"                 TEXT NOT NULL,
     "length"               INTEGER NOT NULL,
     "port"                 INTEGER NOT NULL,
     "raw"                  BLOB NOT NULL,
     "is_tls"               BOOLEAN NOT NULL,
     "query"                TEXT NULL,
     "file_extension"       TEXT NULL,
     "caido_source"         TEXT NULL,
     "alteration"           TEXT NULL,
     "edited"               BOOLEAN NOT NULL,
     "parent_id"            TEXT NULL,
     "created_at"           INTEGER NOT NULL,
     "caido_response_id"    INTEGER NULL,
     "response_status_code" INTEGER NULL,
     "response_raw"         BLOB NULL,
     "response_length"      INTEGER NULL,
     "response_alteration"  TEXT NULL,
     "response_edited"      BOOLEAN NULL,
     "response_parent_id"   TEXT NULL,
     "response_created_at"  INTEGER NULL,
     PRIMARY KEY ("id")
  )  
```

Table: `requests`

Description: Beautified data ready for use in tooling.

Definition:
```sql
 CREATE TABLE IF NOT EXISTS "requests"
  (
     "id"                   INTEGER NOT NULL,
     "host"                 TEXT NOT NULL,
     "method"               TEXT NOT NULL,
     "path"                 TEXT NOT NULL,
     "length"               INTEGER NOT NULL,
     "port"                 INTEGER NOT NULL,
     "cookies"              TEXT NOT NULL,
     "headers"              TEXT NOT NULL,
     "body"                 TEXT NOT NULL,
     "is_tls"               BOOLEAN NOT NULL,
     "query"                TEXT NULL,
     "created_at"           INTEGER NOT NULL,
     "response_status_code" INTEGER NULL,
     "response_headers"     TEXT NULL,
     "response_body"        TEXT NULL,
     "response_length"      INTEGER NULL,
     "response_created_at"  INTEGER NULL,
     PRIMARY KEY ("id")
  )  
```
Indexes:
```sql
CREATE INDEX IF NOT EXISTS request_created_at ON "requests"(created_at);
CREATE INDEX IF NOT EXISTS response_created_at ON "requests"(response_created_at);
CREATE INDEX IF NOT EXISTS request_host ON "requests"(host);
CREATE INDEX IF NOT EXISTS request_method ON "requests"(method);
CREATE INDEX IF NOT EXISTS response_status_code ON "requests"(response_status_code)  
```