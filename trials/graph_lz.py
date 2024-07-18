# import requests
# import json
# import networkx as nx
# import matplotlib.pyplot as plt
from pyvis.network import Network

# # Retrieval of individual 
# def get_relationships_recr(subject, depth = 1):
#     response_ids = json.loads(requests.get(rf'https://python-server-ohgaalojiq-de.a.run.app/relationships/?subject={subject}').content)
#     response_names = json.loads(requests.get(rf'https://python-server-ohgaalojiq-de.a.run.app/relationships-with-names/?subject={subject}').content)

#     relationships = {}
#     for id_dict, name_ls in zip(response_ids, response_names):
#         rs = {
#             "subject": name_ls[0],
#             "predicate": name_ls[1],
#             "object": name_ls[2]
#         }
#         # print(rs)
#         relationships[tuple(id_dict.values())] = rs
#         if depth > 1:
#             relationships.update(get_relationships_recr(id_dict['object'], depth=depth-1))
#         # print(id_dict)
#     return relationships


# Step 1: Create a Pyvis network
net = Network(notebook=True)
net = Network(notebook=True, cdn_resources='in_line')

# Step 2: Add nodes and edges
net.add_node("Marie Curie", label="Marie Curie", title="Person", color="lightgreen")
net.add_node("Pierre Curie", label="Pierre Curie", title="Person", color="lightgreen")
net.add_node("University Of Paris", label="University Of Paris", title="Organization", color="lightcoral")
net.add_node("Poland", label="Poland", title="Country", color="lightblue")
net.add_node("France", label="France", title="Country", color="lightblue")

net.add_edge("Marie Curie", "Pierre Curie", title="SPOUSE")
net.add_edge("Marie Curie", "University Of Paris", title="WORKED_AT")
net.add_edge("Marie Curie", "Poland", title="NATIONALITY")
net.add_edge("Marie Curie", "France", title="NATIONALITY")

# Step 3: Visualize the network



# Step 3: Visualize the network and save it to an HTML file
net_html = net.generate_html()  # Generate the HTML content

# Write the HTML content to a file with UTF-8 encoding
with open("marie_curie_graph.html", 'w', encoding='utf-8') as file:
    file.write(net_html)

# Optionally, you can open the HTML file in the default web browser
import webbrowser
webbrowser.open("marie_curie_graph.html")

# net.show("marie_curie_graph.html", )
# with open("marie_curie_graph.html", 'w') as file:
#     file.write(net.show("marie_curie_graph.html"))

# if __name__ == '__main__':
#   relationships = get_relationships_recr(1, 2)
#   print(relationships)
