# Data loading and transformation

This directory has SQL files that prepare data in DuckDB for usage by the API.

To run:

    duckdb -bail -f <file>.sql ../data/duck_meta.db
