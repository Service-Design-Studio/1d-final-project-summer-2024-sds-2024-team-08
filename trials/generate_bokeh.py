import requests
import json
from bokeh.plotting import figure, show, output_file
from bokeh.models import Circle, ColumnDataSource, LabelSet
from bokeh.io import curdoc
import networkx as nx
from bokeh.models.graphs import from_networkx


base_url = 'https://python-server-ohgaalojiq-de.a.run.app'

def get_rs(subject):
    response_names = json.loads(requests.get(rf'{base_url}/relationships-with-names/?subject={subject}').content)
    return response_names

def generate_bokeh(subject):
    relationships = get_rs(subject)

    G = nx.Graph()

    for rs in relationships:
        subj = rs[0]
        pred = rs[1]
        obj = rs[2]
        G.add_node(subj)
        G.add_node(obj)
        G.add_edge(subj, obj, label=pred)

    plot = figure(title="Network Graph", x_range=(-1.1, 1.1), y_range=(-1.1, 1.1), tools="", toolbar_location=None)
    graph = from_networkx(G, nx.spring_layout, scale=2, center=(0, 0))

    graph.node_renderer.glyph = Circle(size=15, fill_color="skyblue", line_color="black")

    # Add a text label
    node_source = graph.node_renderer.data_source
    labels = LabelSet(x='x', y='y', text='index', source=node_source, render_mode='canvas', text_align='center', text_baseline='middle')
    plot.add_layout(labels)

    plot.renderers.append(graph)

    output_file("network_graph.html")
    show(plot)

if __name__ == '__main__':
    subject = 1
    generate_bokeh(subject)
