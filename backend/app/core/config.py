from databases import DatabaseURL
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")
PROJECT_NAME = "phresh"
VERSION = "1.0.0"
API_PREFIX = "/api"
SECRET_KEY = config("SECRET_KEY", cast=Secret, default="CHANGEME")
POSTGRES_USER = config("POSTGRES_USER", cast=str)
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret)
POSTGRES_SERVER = config("POSTGRES_SERVER", cast=str, default="db")
POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="5432")
POSTGRES_DB = config("POSTGRES_DB", cast=str)
DATABASE_URL = config(
    "DATABASE_URL",
    default=f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}",
)
SCHEMA_NAME = config("SCHEMA_NAME", cast=str, default='citation_network')

LOGS_DIR = config("LOGS_DIR", cast= str, default = "app/api/logs/log.txt")
LOGS_MESSAGE_FORMAT = config("LOGS__MESSAGE_FORMAT", cast=str, default="%(asctime)s %(message)s")


THREADS_LIMIT = config("THREADS_LIMIT", cast=int, default=5)