import sqlite3
import re
import os

data_dir = os.path.join('.', 'data')

def get_stakeholders(stakeholder_id: int = None, name: str = None, summary: bool = True, headline: bool = True, photo: bool = True):
    """_summary_

    Args:
        stakeholder_id (int, optional): _description_. Defaults to None.
        name (str, optional): _description_. Defaults to None.
        summary (bool, optional): _description_. Defaults to True.
        headline (bool, optional): _description_. Defaults to True.
        photo (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    db_file = os.path.join(data_dir, 'stakeholders.db')
    conn = sqlite3.connect(db_file)  # Connect to the SQLite database // REMEMBER TO CHANGE THIS TO THE PATH OF THE DATABASE FILE
    cursor = conn.cursor()  # Create a cursor object using the connection

    # Base query
    query = "SELECT stakeholder_id, name"
    
    # Add additional columns based on boolean flags
    if summary:
        query += ", summary"
    if headline:
        query += ", headline"
    if photo:
        query += ", photo"
        
    query += " FROM stakeholders WHERE 1=1"
    params = []

    # Add conditions based on provided parameters
    if stakeholder_id is not None:
        query += " AND stakeholder_id = ?"
        params.append(stakeholder_id)
    
    if name is not None:
        query += " AND name = ?"
        params.append(name)

    # Execute query
    cursor.execute(query, params)  # executes the sql query with the given parameters
    results = cursor.fetchall()  # Fetch all rows from the resulting table of a query execution.
    
    # Get headers
    headers = [description[0] for description in cursor.description]
    
    conn.close()  # Close the connection
    
    if not results:
        return 'No results found.'
    
    # Format the results as a list of dictionaries
    formatted_results = [dict(zip(headers, row)) for row in results]  # headers = ['stakeholder_id', 'name', 'summary', 'headline', 'photo'] and row = (stakeholder_id, name, summary, headline, photo). the code matches the i-th element of headers with the i-th element of row and creates a dictionary from them.
    
    return formatted_results


def get_relationships(subject: int = None, predicate: str = None, object: int = None):
    """_summary_

    Args:
        subject (int, optional): _description_. Defaults to None.
        predicate (str, optional): _description_. Defaults to None.
        object (int, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    db_file = os.path.join(data_dir, 'stakeholders.db')
    conn = sqlite3.connect(db_file)  # Connect to the SQLite database // REMEMBER TO CHANGE THIS TO THE PATH OF THE DATABASE FILE
    cursor = conn.cursor()  # Create a cursor object using the connection

    query = "SELECT subject, predicate, object FROM relationships WHERE 1=1"
    params = []

    if subject is not None:
        query += " AND subject = ?"
        params.append(subject)
    
    if predicate is not None:
        query += " AND predicate = ?"
        params.append(predicate)
    
    if object is not None:
        query += " AND object = ?"
        params.append(object)

    cursor.execute(query, params)  # executes the sql query with the given parameters
    results = cursor.fetchall()  # Fetch all rows from the resulting table of a query execution.
    conn.close()  # Close the connection
    return results

def get_stakeholder_name(stakeholder_id: int) -> str:
    """_summary_

    Args:
        stakeholder_id (int): _description_

    Returns:
        str: _description_
    """
    db_file = os.path.join(data_dir, 'stakeholders.db')
    conn = sqlite3.connect(db_file)  # Connect to the SQLite database // REMEMBER TO CHANGE THIS TO THE PATH OF THE DATABASE FILE
    cursor = conn.cursor()  # Create a cursor object using the connection

    query = "SELECT name FROM stakeholders WHERE stakeholder_id = ?"
    cursor.execute(query, (stakeholder_id,))  # executes the sql query with the given parameters
    result = cursor.fetchone()  # Fetches the next row of a query result set, returning a single sequence, or None when no more data is available.
    conn.close()

    if result:
        return result[0]
    else:
        return None
    
def extract_after_last_slash(text: str) -> str:
    match = re.search(r'[^/]+$', text)  # the regex matches one or more characters that are not a slash and starts from the end of the string backwards until it finds a slash
    if match:
        return match.group(0)  # returns the matched string
    return None

def get_relationships_with_names(subject: int = None, predicate: str = None, object: int = None):
    """_summary_

    Args:
        subject (int, optional): _description_. Defaults to None.
        predicate (str, optional): _description_. Defaults to None.
        object (int, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    relationships = get_relationships(subject, predicate, object)  # gets the relationships from the database // REMEMBER TO CHANGE THIS TO THE PATH OF THE DATABASE FILE
    relationships_with_names = []  # initializes an empty list to store the relationships with names
    for result in relationships:
        subject_name = get_stakeholder_name(result[0])  # gets the name of the subject
        object_name = get_stakeholder_name(result[2])  # gets the name of the object
        predicate = result[1]
        extracted_info = extract_after_last_slash(predicate)  # extracts the information after the last slash in the predicate
        extracted_info = re.sub(r'[^a-zA-Z0-9\' ]', '', extracted_info)  # removes any special characters from the extracted information
        relationships_with_names.append((subject_name, extracted_info, object_name))
    
    if relationships_with_names == []:
        return 'No results found.'
    return relationships_with_names

def get_chats_from_user(user_id: int) -> list:
    """_summary_
    
    Args: 
        user_id (int): _description_
        
    Returns:
        List[int]: _description_
            
    """
    db_file = os.path.join(data_dir, 'users.db')
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT chat_id
    FROM chats
    WHERE user_id = ?
    ''', (user_id,))

    chat_ids = [row[0] for row in cursor.fetchall()]

    conn.close()
    return chat_ids

def get_messages_from_chat(chat_id: int) -> list:
    """_summary_
    
    Args: 
        chat_id (int): _description_
        
    Returns:
        List[Dict[str, Union[int, str]]]: _description_
        
    """
    db_file = os.path.join(data_dir, 'users.db')
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, role, content
    FROM messages
    WHERE chat_id = ?
    ORDER BY id
    ''', (chat_id,))

    messages = [{'id': row[0], 'role': row[1], 'content': row[2]} for row in cursor.fetchall()]

    conn.close()
    return messages