from dash import Dash, html
import dash_cytoscape as cyto
import requests

base_url= 'https://python-server-ohgaalojiq-de.a.run.app'

app = Dash(__name__)

def get_relationships_recr(subject, depth = 1):
    response_ids = json.loads(requests.get(rf'https://python-server-ohgaalojiq-de.a.run.app/relationships/?subject={subject}').content)
    response_names = json.loads(requests.get(rf'https://python-server-ohgaalojiq-de.a.run.app/relationships-with-names/?subject={subject}').content)
    
    relationships = {}
    for id_dict, name_ls in zip(response_ids, response_names):
        rs = {
            "subject": name_ls[0],
            "predicate": name_ls[1],
            "object": name_ls[2]
        }
        # print(rs)
        relationships[tuple(id_dict.values())] = rs
        if depth > 1:
            relationships.update(get_relationships_recr(id_dict['object'], depth=depth-1))
        # print(id_dict)
    return relationships

def get_relationships(subject, depth):
    res = get_relationships_recr(subject, depth=depth)
    return list(res.values())

def extract_after_last_slash(predicate: str):
    """Extracts the last part after the last slash."""
    return predicate.split('/')[-1]

# Define the base URL of the FastAPI
base_url = 'https://stakeholder-api-hafh6z44mq-de.a.run.app'

# Fetch stakeholders
stakeholders_response = requests.get(f'{base_url}/stakeholders/')
stakeholders = stakeholders_response.json()

# Fetch relationships
relationships_response = requests.get(f'{base_url}/relationships/')
relationships = relationships_response.json()

# Fetch relationships with names
relationships_with_names_response = requests.get(f'{base_url}/relationships-with-names/?subject=1')
relationships_with_names = relationships_with_names_response.json()

# Create elements for Cytoscape
elements = []

# Add stakeholders as nodes
for stakeholder in stakeholders:
    elements.append({'data': {'id': stakeholder["id"], 'label': stakeholder["name"]}})

# Add relationships as edges
for relationship in relationships:
    elements.append({'data': {'source': relationship["subject"], 'target': relationship["object"], 'label': relationship["predicate"]}})

# Add relationships with names as edges with additional information
for relation in relationships_with_names:
    elements.append({'data': {'source': relation[0], 'target': relation[2], 'label': relation[1]}})

# Define the layout for the Dash app
app.layout = html.Div([
    html.P("Dash Cytoscape:"),
    cyto.Cytoscape(
        id='cytoscape',
        elements=elements,
        layout={'name': 'breadthfirst'},
        style={'width': '800px', 'height': '600px'}
    )
])

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
    