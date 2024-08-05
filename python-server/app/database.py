from sqlalchemy import create_engine
from os import getenv
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from psycopg_pool import ConnectionPool

load_dotenv()

# Database connection parameters
db_params_users = {
    'dbname': 'users',
    'user': getenv('USERS_DB_USERNAME'),
    'password': getenv("USERS_DB_PASSWORD"),
    'host': getenv("USERS_DB_HOST"),
    'port': getenv("USERS_DB_PORT")
}

db_params_stakeholders = {
    'dbname': 'stakeholders',
    'user': getenv('STAKEHOLDERS_DB_USERNAME'),
    'password': getenv("STAKEHOLDERS_DB_PASSWORD"),
    'host': getenv("STAKEHOLDERS_DB_HOST"),
    'port': getenv("STAKEHOLDERS_DB_PORT")
}

db_params_media = {
    'dbname': 'media',
    'user': getenv('MEDIA_DB_USERNAME'),
    'password': getenv("MEDIA_DB_PASSWORD"),
    'host': getenv("MEDIA_DB_HOST"),
    'port': getenv("MEDIA_DB_PORT")
}

qdrant_client = QdrantClient(
    url=getenv('QDRANT_HOST'), 
    api_key=getenv('QDRANT_PASS'),
)

# Database connection URL
def get_db_url(params):
    str = (f"postgresql+psycopg2://"+\
    f"{params['user']}:"+\
    f"{params['password']}@"+\
    f"{params['host']}:"+\
    f"{params['port']}/"+\
    f"{params['dbname']}")
    return str

def get_pool_url(params):
    str = (f"postgresql://"+\
    f"{params['user']}:"+\
    f"{params['password']}@"+\
    f"{params['host']}:"+\
    f"{params['port']}/"+\
    f"{params['dbname']}?sslmode=disable")
    return str

# Create a SQLAlchemy engine
user_engine = create_engine(get_db_url(db_params_users))
stakeholder_engine = create_engine(get_db_url(db_params_stakeholders))
media_engine = create_engine(get_db_url(db_params_media))

pool = ConnectionPool(
    conninfo=get_pool_url(db_params_users),
    max_size=5
)