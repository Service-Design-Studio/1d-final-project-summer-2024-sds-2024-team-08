# import sqlite3
# import pandas as pd
# import os

# # Define file paths
# data_dir = os.path.join('.', 'data')
# csv_dir = os.path.join(data_dir, 'csv')
# stakeholders_csv = os.path.join(csv_dir, 'stakeholders.csv')
# relationships_csv = os.path.join(csv_dir, 'relationships_cleaned.csv')
# db_file = os.path.join(data_dir, 'stakeholders.db')

# # Function to create and/or connect to the database, create tables, and clear existing data
# def setup_database(db_path):
#     # Connect to SQLite database (or create it if it doesn't exist)
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()

#     # Create the stakeholders table
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS stakeholders (
#         stakeholder_id INTEGER PRIMARY KEY,
#         name TEXT,
#         headline TEXT,
#         summary TEXT,
#         photo TEXT,
#         source TEXT,
#         source_id TEXT,
#         series INTEGER
#     )
#     ''')

#     # Create the relationships table
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS relationships (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         subject INTEGER,
#         predicate TEXT,
#         object INTEGER,
#         FOREIGN KEY (subject) REFERENCES stakeholders(stakeholder_id),
#         FOREIGN KEY (object) REFERENCES stakeholders(stakeholder_id)
#     )
#     ''')

#     # Clear existing data in the tables
#     cursor.execute('DELETE FROM stakeholders')
#     cursor.execute('DELETE FROM relationships')

#     # Commit changes and return connection and cursor
#     conn.commit()
#     return conn, cursor

# # Function to insert data into the stakeholders table
# def insert_stakeholder(cursor, data):
#     cursor.execute('''
#     INSERT OR IGNORE INTO stakeholders (stakeholder_id, name, headline, summary, photo, source, source_id, series)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#     ''', (data['stakeholder_id'], data['name'], data['headline'], data['summary'], data['photo'], data['source'], data['source_id'], data['series']))

# # Function to insert data into the relationships table
# def insert_relationship(cursor, data):
#     cursor.execute('''
#     INSERT INTO relationships (subject, predicate, object)
#     VALUES (?, ?, ?)
#     ''', (data['subject'], data['predicate'], data['object']))

# # Function to load CSV data into the SQLite database
# def load_csv_to_db(db_path, stakeholders_csv, relationships_csv):
#     # Set up the database and clear existing data
#     conn, cursor = setup_database(db_path)

#     # Load stakeholders data
#     stakeholders_df = pd.read_csv(stakeholders_csv)
#     for _, row in stakeholders_df.iterrows():
#         insert_stakeholder(cursor, row)
    
#     # Load relationships data
#     relationships_df = pd.read_csv(relationships_csv)
#     for _, row in relationships_df.iterrows():
#         insert_relationship(cursor, row)
    
#     # Commit changes and close the connection
#     conn.commit()
#     conn.close()

# # Call the function with your CSV file paths
# load_csv_to_db(db_file, stakeholders_csv, relationships_csv)
# print("Data has been loaded into the database")
# print("stakeholders.db has been created in the data directory")

import sqlite3
import pandas as pd
import os

# Define file paths using os.path
data_dir = os.path.join('.', 'data')
csv_dir = os.path.join(data_dir, 'csv')
stakeholders_csv = os.path.join(csv_dir, 'stakeholders.csv')
relationships_csv = os.path.join(csv_dir, 'relationships_cleaned.csv')
cluster_data_csv = os.path.join(csv_dir, 'media_cleaned.csv')
db_file = os.path.join(data_dir, 'stakeholders.db')
media_db_file = os.path.join(data_dir, 'media.db')

# Function to create and/or connect to the database, create tables, and clear existing data
def setup_database(db_path):
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the stakeholders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stakeholders (
        stakeholder_id INTEGER PRIMARY KEY,
        name TEXT,
        headline TEXT,
        summary TEXT,
        photo TEXT,
        source TEXT,
        source_id TEXT,
        series INTEGER
    )
    ''')

    # Create the relationships table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject INTEGER,
        predicate TEXT,
        object INTEGER,
        FOREIGN KEY (subject) REFERENCES stakeholders(stakeholder_id),
        FOREIGN KEY (object) REFERENCES stakeholders(stakeholder_id)
    )
    ''')

    # Clear existing data in the tables
    cursor.execute('DELETE FROM stakeholders')
    cursor.execute('DELETE FROM relationships')

    # Commit changes and return connection and cursor
    conn.commit()
    return conn, cursor

# Function to insert data into the stakeholders table
def insert_stakeholder(cursor, data):
    cursor.execute('''
    INSERT OR IGNORE INTO stakeholders (stakeholder_id, name, headline, summary, photo, source, source_id, series)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['stakeholder_id'], data['name'], data['headline'], data['summary'], data['photo'], data['source'], data['source_id'], data['series']))

# Function to insert data into the relationships table
def insert_relationship(cursor, data):
    cursor.execute('''
    INSERT INTO relationships (subject, predicate, object)
    VALUES (?, ?, ?)
    ''', (data['subject'], data['predicate'], data['object']))

# Function to load CSV data into the SQLite database
def load_csv_to_db(db_path, stakeholders_csv, relationships_csv):
    # Set up the database and clear existing data
    conn, cursor = setup_database(db_path)

    # Load stakeholders data
    stakeholders_df = pd.read_csv(stakeholders_csv)
    for _, row in stakeholders_df.iterrows():
        insert_stakeholder(cursor, row)
    
    # Load relationships data
    relationships_df = pd.read_csv(relationships_csv)
    for _, row in relationships_df.iterrows():
        insert_relationship(cursor, row)
    
    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Function to get common columns from CSV files
def get_common_columns(csv_files):
    all_columns = set()
    for csv_file in csv_files:
        df = pd.read_csv(csv_file, nrows=0)  # Read only the header
        all_columns.update(df.columns)
    return list(all_columns)

# Function to read and standardize CSV files
def read_and_standardize_csv(csv_file, columns):
    df = pd.read_csv(csv_file)
    # Ensure the DataFrame has all required columns
    for col in columns:
        if col not in df.columns:
            df[col] = None  # Add missing columns with None values
    return df[columns]

# Function to load cluster data CSV into the media database
def load_cluster_data_to_db(csv_file, db_path):
    # Automatically determine the common columns for the CSV file
    common_columns = get_common_columns([csv_file])
    
    # Read and standardize the CSV file into a DataFrame
    df = read_and_standardize_csv(csv_file, common_columns)
    
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    
    # Insert the DataFrame into a single table
    df.to_sql('media', conn, if_exists='replace', index=False)
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

# Main function to orchestrate the database setup
def main():
    # Load stakeholders and relationships data into stakeholders.db
    load_csv_to_db(db_file, stakeholders_csv, relationships_csv)
    print("Stakeholders and relationships data loaded into stakeholders.db")
    
    # Load cluster data into media.db
    load_cluster_data_to_db(cluster_data_csv, media_db_file)
    print("Cluster data loaded into media.db")

# Call the main function
if __name__ == "__main__":
    main()
