from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

# Database connection parameters
db_params = {
    'dbname': 'users',
    'user': 'dbadmin',
    'password': 'SDSteam8',
    'host': '35.221.170.97',
    'port': '5432'
}

# Database connection URL
db_url = f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"

# Create a SQLAlchemy engine
engine = create_engine(db_url)