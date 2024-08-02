from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from sqlalchemy.orm import Session
from database import stakeholder_engine, user_engine
from pyvis.network import Network
from functools import partial
from models import Network_Graph
from random import randint
from tools import filter_edges, parse_list
import crud

def print_pt(inp):
    print(inp)
    return inp

def apply_map(inp):
    inp['media']['nodes'] = {id: name_map if name_map else name 
                                for (id, name), name_map in 
                                zip(inp['media']['nodes'].items(), inp['map'])}
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
                    edges.append({
                        "sub": source['nodes'][sub_id],
                        "pred": pred,
                        "obj": source['nodes'][obj_id]
                    })
    
    return {"imgs": imgs, "edges": edges}

def generate_graph(inp):
    subj_color="#77E4C8"
    obj_color="#3DC2EC"
    edge_color="#96C9F4"

    g = Network(height="1024px", width="100%",font_color="black")
    
    for name, img in inp["imgs"].items():
        node = partial(g.add_node, name)
        if img:
            node = partial(node, shape="image", image=img)
        num_connections = len(list(filter(lambda e: name in [e['sub'], e['obj']], inp['edges'])))
        if num_connections == 0:
            continue
        elif num_connections > 2:
            node = partial(node, 
                           color = subj_color, 
                           size = 40,
                           x = 0,
                           y = 0)
        else:
            node = partial(node, 
                           color = obj_color, 
                           size = 20,
                           x = randint(5,10),
                           y = randint(5,10))
        node() # Add the node by completing the partial fn

    for edge in inp['edges']:
        g.add_edge(edge['sub'], edge['obj'], label=edge['pred'], color=edge_color, smooth=False)

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
    Your output should be another list of names C.
    The length of C should be the same length as B.
    The order of C depends on the order of B.
    Each name in C should either be empty or appear in A.

    # Example
    ## A
    ["Alice", "Bob", "John"]
    
    ## B
    ["Johnson", "Steve", "Alice", "Daniel"]

    ## Your response
    ["John", "", "Alice", ""]"""),

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
        graph.chat_id = config["configurable"]["thread_id"]
        
        session.add(graph)
        session.commit()
        generated_id = graph.id

    return {"saved_graph_id": generated_id}

def filter_combined_graph(state, llm=None):
    initial_msg = state['messages'][0].content
    graph = state['combined_list']
    img = graph['imgs']
    return filter_edges(llm, initial_msg, graph, map_names=False) | (lambda edges: {"edges": edges, "imgs": img})



def parse_output(inp, name):
    return {"messages": AIMessage(f"Graph generated: {inp['saved_graph_id']}", name=name), **inp}

def create_agent(llm):
    def format_input(inp):
        result = RunnablePassthrough()
        if inp.get('rs_db') and inp.get('media'):
            loaded = lambda d: {
                'A': str(list(d['rs_db']['nodes'].values())),
                'B': str(list(d['media']['nodes'].values()))}
            
            return result.assign(map = (loaded | mapping_prompt | llm | parse_list)) | apply_map
        else:
            return result
    return RunnableLambda(format_input) | RunnablePassthrough.assign(combined_list=combine_lists) | RunnableLambda(filter_combined_graph).bind(llm=llm)| generate_graph | save_graph

def create_node(llm, name):
    return create_agent(llm) | RunnableLambda(parse_output).bind(name=name)

if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    from langchain_google_vertexai import ChatVertexAI
    
    print(create_node(ChatVertexAI(model="gemini-1.5-flash", max_retries=2), "Grapher").invoke(
        {
        'messages': [
            HumanMessage("Who is related to Steve?")
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
                    3: "Bob"},
            'edges': [
                [1, 'C', 2],
                [1, 'D', 3]
            ]
         }
    },
    config={"configurable": {
        "thread_id": 10
    }}))

