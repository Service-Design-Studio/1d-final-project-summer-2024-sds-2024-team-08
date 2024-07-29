from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from sqlalchemy.orm import Session
from database import stakeholder_engine, user_engine
from pyvis.network import Network
from functools import partial
from random import randint
import crud

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
        if len(list(filter(lambda e: name in [e['sub'], e['obj']], inp['edges']))) > 2:
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
        node()

    for edge in inp['edges']:
        g.add_edge(edge['sub'], edge['obj'], label=edge['pred'], color=edge_color, smooth=False)

    g.repulsion(node_distance=250, spring_length=350)
    g.set_edge_smooth("dynamic")
    network_graph = g.generate_html()

    return network_graph

mapping_prompt = PromptTemplate.from_template(
    """
    # Instructions
    You are a highly specialised tool trained in text processing.
    You will be given a Python dictionary containing two lists A and B, each containing a list of names.
    For each name in B, find the closest name that matches in A.
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
    ["John", "", "Alice", ""]

    # Your input
    ## A
    {A}

    ## B
    {B}
    """)

def parse_list(s:str):
    return [sub.strip().strip('"') for sub in s.removeprefix("[").removesuffix("]").split(',')]

def create_agent(llm):
    def format_input(inp):
        result = RunnablePassthrough()
        if 'rs_db' in inp and 'media' in inp:
            loaded = lambda d: {
                'A': str(d['rs_db']['nodes'].values()),
                'B': str(d['media']['nodes'].values())}
            return result.assign(map = loaded | mapping_prompt | llm | parse_list) | apply_map
        else:
            return result
    return RunnableLambda(format_input) | combine_lists #| generate_graph


if __name__ == "__main__":
    def llm(inp):
        return '["", "Steve", "Bob"]'
    
    print(create_agent(llm).invoke(
        {'rs_db': {
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
    }))

