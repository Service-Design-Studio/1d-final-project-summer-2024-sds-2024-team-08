from sqlalchemy import create_engine
from os import getenv
from dotenv import load_dotenv

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

# Database connection URL
def get_db_url(params):
    str = (f"postgresql+psycopg2://"+\
    f"{params['user']}:"+\
    f"{params['password']}@"+\
    f"{params['host']}:"+\
    f"{params['port']}/"+\
    f"{params['dbname']}")
    return str

# Create a SQLAlchemy engine
user_engine = create_engine(get_db_url(db_params_users))
stakeholder_engine = create_engine(get_db_url(db_params_stakeholders))