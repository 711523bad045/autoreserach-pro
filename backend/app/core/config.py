from urllib.parse import quote_plus

DB_NAME = "autoresearch_pro"
DB_USER = "RAJESH"
DB_PASSWORD = "Rrajesh2004@"
DB_HOST = "localhost"
DB_PORT = "3306"

ENCODED_PASSWORD = quote_plus(DB_PASSWORD)

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{ENCODED_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
