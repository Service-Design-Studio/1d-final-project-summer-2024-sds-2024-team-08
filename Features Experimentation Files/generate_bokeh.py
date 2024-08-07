import sqlite3
import os
import networkx as nx
from bokeh.io import show, output_file
from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, BoxSelectTool, NodesAndLinkedEdges
from bokeh.plotting import from_networkx
from bokeh.palettes import Spectral4

base_url= 'https://python-server-ohgaalojiq-de.a.run.app'

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

    plot = Plot(width=800, height=800,
                x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))
    
    graph_renderer = from_networkx(G, nx.spring_layout, scale=2, center=(0, 0))
    
    graph_renderer.node_renderer.glyph = Circle(radius=0.1, fill_color=Spectral4[0])
    graph_renderer.edge_renderer.glyph = MultiLine(line_color="black", line_alpha=0.8, line_width=1)
    
    plot.renderers.append(graph_renderer)
    
    node_hover_tool = HoverTool(tooltips=[("name", "@index")])
    plot.add_tools(node_hover_tool, TapTool(), BoxSelectTool())
    
    graph_renderer.selection_policy = NodesAndLinkedEdges()
    graph_renderer.inspection_policy = NodesAndLinkedEdges()
    
    output_dir = os.path.join(os.path.dirname(__file__), 'graphs')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file_path = os.path.join(output_dir, f"{stakeholder_name}_network.html")
    output_file(output_file_path)
    show(plot)


if __name__ == "__main__":
    stakeholder_name = "Ben Carson"  # Specify the stakeholder name here
    generate_network_graph(stakeholder_name)