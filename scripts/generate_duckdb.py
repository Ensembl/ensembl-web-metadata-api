#!/usr/bin/env python3
import argparse
import os
from urllib.parse import urlparse

import duckdb


def main():
    description = "Creates a DuckDB-format file from the metadata DB"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--dbhost", help="Metadata database hostname")
    parser.add_argument("--dbport", help="Metadata database port")
    parser.add_argument("--dbuser", help="Metadata database read-only user")
    parser.add_argument("--dbpass", help="Metadata database password")
    parser.add_argument("--dbname", help="Metadata database name")
    parser.add_argument("--outfile", help="Name of DuckDB format output file")
    args = vars(parser.parse_args())

    dbhost = args.get("dbhost")
    dbport = args.get("dbport")
    dbuser = args.get("dbuser")
    dbpass = args.get("dbpass")
    dbname = args.get("dbname")
    outfile = args.get("outfile") or "duck_meta.db"

    if os.environ.get("METADATA_DB") is not None:
        db = urlparse(os.environ.get("METADATA_DB"))
        dbhost = db.hostname
        dbport = db.port
        dbuser = db.username
        dbpass = db.password
        dbname = db.path[1:]

    required = {
        "dbhost": dbhost,
        "dbport": dbport,
        "dbuser": dbuser,
        "dbname": dbname,
    }
    missing = [key for key, value in required.items() if not value]
    if missing:
        parser.error(
            "Missing DB connection settings: "
            + ", ".join(missing)
            + ". Provide --dbhost/--dbport/--dbuser/--dbname or METADATA_DB."
        )

    print(f"Starting metadata import into DuckDB file: {outfile}")

    con = duckdb.connect()

    # This operation may need much more memory than the configured limit.
    con.execute("SET memory_limit = '8GB'")
    password_part = f" password={dbpass}" if dbpass else ""
    con.execute(
        f"ATTACH 'host={dbhost} user={dbuser}{password_part} port={dbport} database={dbname}' AS metadb (TYPE mysql)"
    )
    con.execute(f"ATTACH '{outfile}' as duck_meta")
    con.execute("use metadb")

    con.execute("show tables")

    results = con.fetchall()
    for res in results:
        tbl = res[0]
        if tbl.startswith("vw_"):
            continue
        print(f"Importing from table {tbl}")
        con.execute(f"DROP TABLE IF EXISTS duck_meta.{tbl}")
        con.execute(f"CREATE TABLE duck_meta.{tbl} AS FROM metadb.{tbl}")

    print("Done")


if __name__ == "__main__":
    main()
