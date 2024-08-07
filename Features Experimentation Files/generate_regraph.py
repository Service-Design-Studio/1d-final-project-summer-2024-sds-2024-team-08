import sqlite3
import os
import networkx as nx
import matplotlib.pyplot as plt

## File paths
data_dir = os.path.join(os.path.dirname(__file__), 'data')
csv_dir = os.path.join(data_dir, 'csv')
db_file = os.path.join(data_dir, 'stakeholders.db')
media_db_file = os.path.join(data_dir, 'media.db')

file1_path = os.path.join(os.path.dirname(__file__),"build_database.py")
file2_path = os.path.join(os.path.dirname(__file__), "database_query_function.py")

with open(file1_path, "r") as file1, open(file2_path, "r") as file2:
    build_database_content = file1.read()
    database_query_function_content = file2.read()

from database_query_function import get_relationships_with_names 
from database_query_function import extract_after_last_slash 

def get_data(query, params=None):
    """handle database queries and return results."""
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            results = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
    return results

def get_relationships_with_names_by_name(stakeholder_name: str):
    """Fetches relationships from the database and returns them with names for a given stakeholder."""
    query = '''
    WITH RECURSIVE
        StakeholderConnections(level, subject, predicate, object) AS (
        SELECT 1, s1.name, r.predicate, s2.name
        FROM relationships r
        JOIN stakeholders s1 ON s1.stakeholder_id = r.subject
        JOIN stakeholders s2 ON s2.stakeholder_id = r.object
        WHERE s1.name = ? OR s2.name = ?
        UNION ALL
        SELECT sc.level + 1, s1.name, r.predicate, s2.name
        FROM StakeholderConnections sc
        JOIN relationships r ON r.subject = (SELECT stakeholder_id FROM stakeholders WHERE name = sc.object)
        JOIN stakeholders s1 ON s1.stakeholder_id = r.subject
        JOIN stakeholders s2 ON s2.stakeholder_id = r.object
        WHERE sc.level < 3
    )
    SELECT subject, predicate, object
    FROM StakeholderConnections
    '''
    params = (stakeholder_name, stakeholder_name)
    return get_data(query, params)

def generate_network_graph(stakeholder_name):
    # Fetch connections up to a depth of 3 for a given stakeholder
    relationships = get_relationships_with_names_by_name(stakeholder_name)

    G = nx.MultiDiGraph()  # Directed graph
    for subject_name, predicate, object_name in relationships:
        extracted_info = extract_after_last_slash(predicate)
        G.add_edge(subject_name, object_name, label=extracted_info)

    pos = nx.spectral_layout(G)  # positions for all nodes
    nx.draw(G, pos, with_labels=True, node_size=4000, node_color="skyblue", font_size=8, font_weight="normal")
    edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.title(f"Connections up to Depth 3 for {stakeholder_name}")
    plt.show()

if __name__ == "__main__":
    stakeholder_name = "Ben Carson"  # Specify the stakeholder name here
    generate_network_graph(stakeholder_name)