from sqlalchemy import create_engine, Table, MetaData, text
# Database connection parameters
db_params = {
    'dbname': 'users',
    'user': '[INSERT USER NAME]',
    'password': '[INSERT DB PW]',
    'host': '[INSERT PUBLIC IP ADDRESS]',
    'port': '5432'
}

# Database connection URL
db_url = f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"

# Sample data
users_data = [
    {'user_id': 1, 'name': 'Genie'},
    {'user_id': 2, 'name': 'John Tan'},
    {'user_id': 3, 'name': 'Amanda Fergusen'},
    {'user_id': 4, 'name': 'Shawn Pierre'},
]

chats_data = [
    {'chat_id': 1, 'user_id': 2},
    {'chat_id': 2, 'user_id': 3},
    {'chat_id': 3, 'user_id': 3},
    {'chat_id': 4, 'user_id': 3},
    {'chat_id': 5, 'user_id': 3},
    {'chat_id': 6, 'user_id': 3},
    {'chat_id': 7, 'user_id': 3},
    {'chat_id': 8, 'user_id': 3},
    {'chat_id': 9, 'user_id': 3},
    {'chat_id': 10, 'user_id': 3},
    {'chat_id': 11, 'user_id': 3},
    {'chat_id': 12, 'user_id': 3},
    {'chat_id': 13, 'user_id': 3},
    {'chat_id': 15, 'user_id': 3},
    {'chat_id': 16, 'user_id': 3},
    {'chat_id': 17, 'user_id': 3},
    {'chat_id': 18, 'user_id': 3},
    {'chat_id': 19, 'user_id': 3},
    {'chat_id': 20, 'user_id': 3},
    {'chat_id': 21, 'user_id': 3},
    {'chat_id': 22, 'user_id': 3}
]

messages_data = [
    {'message_id': 1, 'chat_id': 1, 'sender_id': 2, 'role': 'user', 'content': 'Tell me examples on text placeholders '},
    {'message_id': 2, 'chat_id': 1, 'sender_id': 1, 'role': 'assistant', 'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'},
    {'message_id': 3, 'chat_id': 2, 'sender_id': 3, 'role': 'user', 'content': 'Tell me examples on text placeholders '},
    {'message_id': 4, 'chat_id': 2, 'sender_id': 1, 'role': 'assistant', 'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'},
    {'message_id': 5, 'chat_id': 2, 'sender_id': 3, 'role': 'user', 'content': 'Give me more!'},
    {'message_id': 6, 'chat_id': 2, 'sender_id': 1, 'role': 'assistant', 'content': 'Purus non enim praesent elementum facilisis leo vel. Id cursus metus aliquam eleifend. Gravida in fermentum et sollicitudin ac orci phasellus. Sit amet nisl suscipit adipiscing. Sagittis aliquam malesuada bibendum arcu vitae elementum. Integer eget aliquet nibh praesent tristique magna sit amet. Est placerat in egestas erat imperdiet. Vitae aliquet nec ullamcorper sit amet. Nulla pharetra diam sit amet. Viverra maecenas accumsan lacus vel facilisis volutpat est velit egestas. Orci phasellus egestas tellus rutrum tellus. Neque sodales ut etiam sit. Ut ornare lectus sit amet est placerat in egestas. Cursus metus aliquam eleifend mi.'},
    {'message_id': 7, 'chat_id': 3, 'sender_id': 1, 'role': 'assistant', 'content': 'What do you want to learn about today?'}
]  

def insert_data(engine, table_name, data):
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)
    try:
        with engine.connect() as connection:
            trans = connection.begin()
            connection.execute(table.insert(), data)
            trans.commit()
            print('Data inserted successfully!')
    except Exception as e:
        trans.rollback()
        print(f"An error occurred: {e}")

def clear_tables(engine):
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM messages;"))
        connection.execute(text("DELETE FROM chats;"))
        connection.execute(text("DELETE FROM users;"))

def main():
    engine = create_engine(db_url)
    clear_tables(engine)
    # Ensure users are inserted first
    insert_data(engine, 'users', users_data)
    # Ensure that inserts into 'chats' happens after 'users'
    insert_data(engine, 'chats', chats_data)
    # Ensure that inserts into 'messages' happens after 'chats'
    insert_data(engine, 'messages', messages_data)

if __name__ == '__main__':
    main()