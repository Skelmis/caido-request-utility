import sqlite3
from pathlib import Path

import cru.csv_to_sql


def main():
    con: sqlite3.Connection = sqlite3.connect("test.db")
    cru.csv_to_sql.create_and_populate_from_csv(con, Path("test.csv"))


if __name__ == "__main__":
    main()
