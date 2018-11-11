import os

DB = os.getenv("DB_NAME", "postgres")
PSQL_HOST = os.getenv("PSQL_HOST", "0.0.0.0")
PSQL_PORT = os.getenv("PSQL_PORT", 5431)
PSQL_PWD = os.getenv("PSQL_PWD", "")
PSQL_USER = os.getenv("PSQL_USER", "postgres")


DATA_DIR = os.getenv("DATA_DIR", "./data")
