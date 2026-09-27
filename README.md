Caido Request Utility (CRU)
---

Turn a Caido (or Burp) export into a SQLite `requests` table, then run a
passive scanner over it to surface likely vulnerabilities.

The scanner **never sends traffic**. Every finding is a lead to confirm by hand
against a system you are authorised to test.

## Install

```bash
pip install skelmis-cru          # core
pip install "skelmis-cru[all]"   # plus defusedxml and brotli
```

The extras are optional but recommended for Burp imports:

- `defusedxml` lets an export that contains a DTD parse. Without it, the stdlib
  fallback rejects any `<!DOCTYPE>` or `<!ENTITY>`.
- `brotli` decompresses `Content-Encoding: br` bodies. Without it, those bodies
  stay unreadable to the checks.

## Usage

One command imports, scans and reports:

```bash
python -m cru export.csv -o report.html   # Caido export in, HTML report out
python -m cru export.csv                  # print findings to the terminal
python -m cru history.xml -o report.html  # Burp XML export in, HTML report out
python -m cru corpus.db -o report.html    # already-imported database
```

`.csv` is read as a Caido export, `.xml` as a Burp export, and anything else as
an existing database. Useful flags:

- `--check NAME` runs one check.
- `--skip NAME ...` drops checks from a full run.
- `--show-secrets` unredacts secret matches.
- `--no-progress` hides the progress bar.

Each step also runs on its own:

```bash
python -m cru.burp_to_sql history.xml -o corpus.db         # import Burp
python -m cru.passive_scan corpus.db --check sqli --json   # scan
python -m cru.report_html corpus.db -o report.html         # JSON + HTML report
python -m cru.idor_finder corpus.db                        # IDOR candidates
```

To import from Python:

```python
import sqlite3
from pathlib import Path

import cru.csv_to_sql

con = sqlite3.connect("test.db")
cru.csv_to_sql.create_and_populate_from_csv(con, Path("test.csv"))
```

To target another database, override `cru.sql_util.execute` and
`cru.sql_util.execute_many`.

## The report

The report is a single self-contained HTML file:

- Findings are grouped by host and check. They are not ranked by severity.
- Expanding a finding shows the request and response it came from, with the
  match highlighted.
- Base64, hex and JWT values are decoded at import and shown in a `#decoded`
  tab. Every check scans the decoded view too.
- Secrets are masked everywhere, including in the message panes.
- Each rule name links to the check's source. `cru.report_html --repo-url`
  points the links at a fork or a tag.
- All values are rendered as text, so payloads in the corpus cannot XSS the
  report.

## The checks

| Check | Catches |
|-------|---------|
| `deserialization` | Serialized objects and gadget markers — PHP, Java, .NET, Ruby, pickle, YAML tags |
| `secrets` | Vendor API keys and tokens, private keys, plus a high-entropy sweep |
| `sqli` | DBMS errors in responses, SQLi-shaped payloads, and parameter names like `sqlQuery` or `orderBy` that compose the query |
| `ssti` | Template-expression syntax in request inputs, tagged by templating style |
| `code` | Fields carrying source or shell commands in 7 languages, JNDI/Log4Shell lookups |
| `srcleak` | Server-side source, `.env`/`web.config` credentials, `.git` metadata in responses |
| `xss` | XSS payload vectors, and parameter values reflected back unencoded |
| `xxe` | External and parameter entities, stream wrappers, and file-read tells |
| `ssrf` | Cloud metadata endpoints and internal hosts in server-fetch parameters |
| `redirect` | Offsite URLs in redirect params, confirmed against a 3xx `Location` |
| `traversal` | `../` sequences and absolute-path markers, escalated when a file comes back |
| `crlf` | CR/LF and overlong-UTF8 sequences in request inputs (request-side probe only) |
| `nosqli` | MongoDB operators as JSON keys or bracketed parameters |
| `upload` | Executable, double, and markup extensions in multipart filenames |
| `security-headers` | Missing or weak CSP, HSTS, frame protection, nosniff, referrer/permissions policy |
| `cors` | Wildcard with credentials, `null` origin, credentialed origin reflection |
| `cookies` | `Set-Cookie` missing HttpOnly, Secure, or SameSite |
| `jwt` | `alg=none`, empty signatures, tokens with no expiry |
| `infoleak` | Stack traces, debug pages, directory listings, GraphQL introspection |
| `fingerprint` | Version banners and framework session-cookie names |
| `mixedcontent` | `http://` sub-resources referenced from an HTTPS page |
| `cleartext` | Credentials, cookies, or `Authorization` sent over plain HTTP |
| `csrf` | State-changing cookie-authenticated requests with no visible CSRF token |

IDOR candidates from `idor_finder` also appear in a full run under the name
`idor`.

[CHECKS.md](CHECKS.md) is the full reference: what each check reads, its
patterns, and its limits.

## Importing from Burp

The Burp importer reads a **"Save items"** XML export. It does not parse
binary `.burp` project files, so open those in Burp first.

1. Go to **Proxy → HTTP history**, or **Target → Site map**.
2. Filter to the items you want, for example with "Show only in-scope items".
3. Select them. `Ctrl-A` selects all. "Save items" only saves the selection.
4. Right-click → **Save items**, and save as `.xml`.
5. Leave base64 encoding on (the default), so binary bodies are not mangled.

Then import, scan and report in one command:

```bash
python -m cru history.xml -o report.html
```

The export has no timestamps, so `created_at` and `response_created_at` are
`0`. Messages that do not parse are skipped and counted.

## Roadmap

- A scope option to narrow what is aggregated
- Tests against a large corpus (10k+ requests)
- Make the HTML report scale to 100k requests: virtualise the list, debounce
  search, and load message panes lazily

Have an idea for what to do with raw request data? Open an issue.

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
     "query_decoded"         TEXT NULL,
     "body_decoded"          TEXT NULL,
     "cookies_decoded"       TEXT NULL,
     "headers_decoded"       TEXT NULL,
     "response_body_decoded" TEXT NULL,
     PRIMARY KEY ("id")
  )  
```

The `*_decoded` columns hold base64/hex plaintext recovered from the matching
field at import time.

Indexes:
```sql
CREATE INDEX IF NOT EXISTS request_created_at ON "requests"(created_at);
CREATE INDEX IF NOT EXISTS response_created_at ON "requests"(response_created_at);
CREATE INDEX IF NOT EXISTS request_host ON "requests"(host);
CREATE INDEX IF NOT EXISTS request_method ON "requests"(method);
CREATE INDEX IF NOT EXISTS response_status_code ON "requests"(response_status_code)  
```