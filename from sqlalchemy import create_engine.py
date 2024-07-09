from sqlalchemy import create_engine
# Database connection parameters
db_params = {
    'dbname': 'stakeholders',
    'user': 'dbadmin',
    'password': r"*9)0hY\&iQ'<fT9X",
    'host': '130.211.251.92',
    'port': '5432'
}

# Database connection URL
db_url = f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}" # replace w database_url

# Create a SQLAlchemy engine
engine = create_engine(db_url)


DATABASE_URL = "postgresql+psycopg2://dbadmin:SDSteam8>@35.221.170.97:5432/users"
