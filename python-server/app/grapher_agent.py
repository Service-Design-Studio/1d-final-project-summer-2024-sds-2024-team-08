from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from sqlalchemy.orm import Session
from database import stakeholder_engine, user_engine
from pyvis.network import Network
import networkx as nx
from functools import partial
from models import Network_Graph
from langchain_core.output_parsers.json import JsonOutputParser
from random import randint
from tools import filter_edges, parse_list
import crud

def print_pt(inp):
    print(inp)
    return inp

def apply_map(inp):
    for id, node in inp['media']['nodes'].items():
        if node in inp['map']:
            inp['media']['nodes'][id] = inp['map'][node]
    del inp['map']
    return inp

def combine_lists(inp):
    rs_db = inp.get('rs_db')
    media = inp.get('media')

    imgs = dict()
    edges = []

    with Session(stakeholder_engine) as db:
        for s_name, source in {"rs_db": rs_db, "media": media}.items():
            if source:
                for id, name in source['nodes'].items():
                    if name not in imgs:
                        imgs[name] = None if s_name == 'media' else crud.get_photo(db, id)
                for sub_id, pred, obj_id in source['edges']:
                    #idk why some of the keys became strings but
                    if isinstance(next(iter(source['nodes'])), str):
                        sub_id = str(sub_id)
                        obj_id = str(obj_id)
                    try:
                        edges.append({
                            "sub": source['nodes'][sub_id],
                            "pred": pred,
                            "obj": source['nodes'][obj_id]
                        })
                    except KeyError:
                        print('Unable to find key', sub_id, obj_id)
    
    return {"imgs": imgs, "edges": edges}

def generate_graph(inp):
    subj_colour="#77E4C8"
    obj_colour="#3DC2EC"
    edge_colour="#96C9F4"
    alt_edge_colour="#FF2020"

    g = Network(height="1024px", width="100%",font_color="black")
    
    filtered_graph = inp['filtered']

    for name, img in filtered_graph["imgs"].items():
        node = partial(g.add_node, name)
        if img:
            node = partial(node, shape="image", image=img)
        num_connections = len(list(filter(lambda e: name in [e['sub'], e['obj']], filtered_graph["edges"]))) #don't ask
        if num_connections == 0:
            continue
        elif num_connections > 2:
            node = partial(node, 
                           color = subj_colour, 
                           size = 40,
                           x = 0,
                           y = 0)
        else:
            node = partial(node, 
                           color = obj_colour, 
                           size = 20,
                           x = randint(5,10),
                           y = randint(5,10))
        node() # Add the node by completing the partial fn

    
    spm = inp.get('spm')
    spm_nodes = set(a for a in spm for a in a) if spm else {}
    
    for edge in filtered_graph['edges']:
        if edge['sub'] in spm_nodes and edge['obj'] in spm_nodes:
            color = alt_edge_colour
        else:
            color = edge_colour

        g.add_edge(edge['sub'], edge['obj'], label=edge['pred'], color=color, smooth=False)

    g.repulsion(node_distance=250, spring_length=350)
    g.set_edge_smooth("dynamic")
    network_graph = g.generate_html()

    return network_graph

mapping_prompt = ChatPromptTemplate.from_messages(
    [("system",
    """
    # Instructions
    You are a highly specialised tool trained in text processing.
    You will be given a Python dictionary containing two lists A and B, each containing a list of names.
    For each name in B, find the closest name that matches in A. 
    Be careful not to combine names that might not refer to the same person, such as "Bob" and "Bob Jr."
    If you find a suitable match, yield that match. Otherwise, yield an empty string.

    # Output
    Your output should be a JSON object which describes which names in B map to names in A.
    Each key in the output should exist in B. It is case sensitive.
    Each value in the output should exist in A. It is case sensitive.

    # Example
    ## A
    ["Alice", "Bob", "John"]
    
    ## B
    ["Johnson", "Steve", "Alice", "Daniel"]

    ## Your response
    {{"Johnson": "John", "Alice": "Alice"}}"""),

    ("user", """
    Given the below input, please calculate the output list C as described in the system message.
    Do not output anything except for the result.
    
    ## A
    {A}

    ## B
    {B}
    """)])



def save_graph(graph_str, config=None):
    with Session(user_engine) as session:
        graph = Network_Graph()
        graph.content = graph_str
        
        chat_id = config["configurable"]["thread_id"]
        # Langgraph may mutate the thread_id without telling; for instance 10 could become 10-Grapher
        graph.chat_id = int(str(chat_id).split('-')[0])
        
        session.add(graph)
        session.commit()
        generated_id = graph.id

    return {"saved_graph_id": generated_id}

def filter_combined_graph(state, llm=None):
    if __name__ == '__main__':
        initial_msg = state['messages'][0].content
    else:
        initial_msg = state['messages'][-2].tool_calls[0]['args']['reason']
    graph = state['combined_list']
    img = graph['imgs']
    return filter_edges(llm, initial_msg, graph, map_names=False) | (lambda edges: {"edges": edges, "imgs": img})



def parse_output(inp, name):
    output = {"messages": AIMessage(f"The network graph has been created!: {inp['saved_graph_id']}", name=name), **inp}

    return output

def identify_short_path(state, llm):
    prompt_template = ChatPromptTemplate.from_messages([(
        "system", """# Instructions
        You are a highly specialised text parsing tool.
        Given a prompt and a list of nodes,
        1. If your task is draw a relationship between two nodes, identify only the start and end nodes. Try to identify only the start and end nodes as much as possible. Otherwise, identify all the primary names involved.
        2. Output a list of ids, indicating the nodes identified.
        3. Ensure that your output appears exactly as it does as in the input. It is case sensitive.

        # Example
        ## Nodes
        ["A", "B", "C", "D"]

        ## Prompt
        "Identify the relationships between A and C. A is related to B and B is related to C."

        ## Your response
        ["A", "C"]
        """), 
        ("user", """
        ## Nodes
        {nodes}
                
        ## Prompt
        {prompt}""")])
    
    if __name__ == '__main__':
        initial_msg = state['messages'][0].content
    else:
        initial_msg = state['messages'][-2].tool_calls[0]['args']['reason']

    graph = state['combined_list']

    chain = prompt_template | llm | parse_list
    
    node_ids = list(graph['imgs'].keys())

    choose = chain.invoke({
        "prompt":initial_msg,
        "nodes":node_ids
    })
    path = None
    if len(choose) == 2:
        print(graph['edges'])
        G = nx.Graph()
        G.add_nodes_from(node_ids)
        G.add_edges_from((edge['sub'], edge['obj']) for edge in graph['edges'])
        try: 
            paths = nx.all_shortest_paths(G, choose[0], choose[1]) 
            path = list(paths)
        except:
            print("Unable to parse edge: ", choose[0], choose[1])
    return path

def create_agent(llm):
    def format_input(inp):
        result = RunnablePassthrough()
        if inp.get('rs_db') and inp.get('media'):
            loaded = lambda d: {
                'A': str(list(d['rs_db']['nodes'].values())),
                'B': str(list(d['media']['nodes'].values()))}
            
            return result.assign(map = (loaded | mapping_prompt | llm | JsonOutputParser())) | apply_map
        else:
            return result
    return RunnableLambda(format_input) | RunnablePassthrough.assign(combined_list=combine_lists) | RunnableParallel(
        filtered=RunnableLambda(filter_combined_graph).bind(llm=llm),
        spm     =RunnableLambda(identify_short_path).bind(llm=llm),
        ) | generate_graph | save_graph

def create_node(llm, name):
    return create_agent(llm) | RunnableLambda(parse_output).bind(name=name)

if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    from langchain_google_vertexai import ChatVertexAI
    
    print(create_node(ChatVertexAI(model="gemini-1.5-flash", max_retries=2), "Grapher").invoke(
        {
        'messages': [
            HumanMessage("Steve is related to David through Alice")
        ],
         'rs_db': {
            'nodes': {
                    1: "Steve",
                    2: "John",
                    3: "Bob"},
            'edges': [
                [1, 'A', 2],
                [1, 'B', 3]
            ]
        },
         'media': {
            'nodes': {
                    1: "Alice",
                    2: "Steven",
                    3: "Bob",
                    4: "David",
            },
            'edges': [
                [1, 'C', 2],
                [1, 'D', 3],
                [1, 'E', 4]
            ]
         }
    },
    config={"configurable": {
        "thread_id": 10
    }}))

