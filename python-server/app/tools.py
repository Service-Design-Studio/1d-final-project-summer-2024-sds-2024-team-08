import re
import time
from typing import Optional
from functools import wraps, reduce
from sqlalchemy.orm import Session
from sqlalchemy import select
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables.config import get_executor_for_config
from langgraph.prebuilt import ToolNode
import rapidfuzz
from qdrant_media import derive_rs_from_media
from models import Stakeholder, Alias
from database import stakeholder_engine
import crud

def timing_decorator(func):
    """Decorator that logs the execution time of the function it decorates."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} executed in {end_time - start_time:.6f} seconds")
        return result
    return wrapper


@tool
def read_stakeholders(stakeholder_id: int = None, name: str = None, summary: bool = True, headline: bool = True, photo: bool = True) -> bytes:
    """Use this tool to read stakeholders from the database. You can filter by stakeholder_id or name. From the prompt, identify the stakeholder by their name or stakeholder_id. 
    If you are using stakeholder_id, ensure that it is an integer before you input it into the read_stakeholders tool. You can also specify whether to include the summary, headline, and photo.
    This tool is used to get summaries and information about stakeholders from the database.

    Always call this tool in parallel with as many stakeholders whos ids you are interested in finding out at once.

    The result returned will be in JSON format.

    Args:
        stakeholder_id (int, optional): Defaults to None.
        name (str, optional): Defaults to None.
        summary (bool, optional): Defaults to True.
        headline (bool, optional): Defaults to True.
        photo (bool, optional): Defaults to True.
        
    Returns:
        str: The description of the user. If it fails to find a user, you can still find out more information about the user from media.
    """
    if stakeholder_id is not None:
        stakeholder_id = int(float(stakeholder_id))
    with Session(stakeholder_engine) as session:
        stakeholders = crud.get_stakeholders(session, stakeholder_id, name, summary, headline, photo)

    return stakeholders
def normalize_name(name):
        """
        Normalize names by converting to lowercase, removing special characters except spaces
        """
        name = re.sub(r'[^a-z0-9\s]', '', name.lower())
        return name
    
with Session(stakeholder_engine) as session:
    aliases = session.scalars(select(Alias)).all()
    aliases_dict = {alias.id: normalize_name(alias.other_names) for alias in aliases}  # Dictionary of id : normalized name
    aliases_sid_dict = {alias.id: [alias.stakeholder_id, normalize_name(alias.other_names)] for alias in aliases}  # Dictionary of id : [stakeholder_id, normalized name]

@tool
def get_name_matches(name: str) -> list:
    """Use this tool to get the best matches for a given name. This tool will return a list of up to 5 stakeholder_ids who have names that are the best matches with the given name. 
    If the output only contains one stakeholder_id, then that is the best match. Depending on the context, if the the user wants to know more about the stakeholder, use the tool read_stakeholders tool to get the information about the identified stakeholder.
    If the user wants to draw a network graph, use the tool get_relationships to get the relationships of the identified stakeholder.

    This tool introduces latency, so always call this tool in parallel.
    For example, if you need to find the names of A, B, and C, you must call get_name_matches 3 times in parallel with A, B, C as the parameters.
    Avoid calling this tool sequentially.

    If the output contains more than one stakeholder_id, then you should ask the user to clarify which stakeholder they are referring to. Following the format :
        "Which names are you referring to?: 
        1. [name 1]
        2. [name 2]
        ..."
    If the output contains no names, then there are no matches for the given name.
    
    Args:
        name (str): The name of the stakeholder you want to find matches for.
        
    Returns:
        list: A list of up to 5 stakeholder_id who have names that are the best matches with the given name. These stakeolder_id will be integers.
    """

    normalized_input_name = normalize_name(name)
    
    if normalized_input_name  in aliases_dict.values():
        stakeholder_id = [value[0] for value in aliases_sid_dict.values() if value[1] == normalized_input_name]
        return stakeholder_id
    
    else:
        best_matches = rapidfuzz.process.extract(normalized_input_name, aliases_dict, score_cutoff=75)  # This wil return a list of tuples with the best matches, their scores and the key. (name, score, id)
        
        if (len(best_matches) == 1):
            return [aliases_sid_dict[best_matches[0][2]][0]]
        
        unique_stakeholders = set()
        result = []
        for match in best_matches:
            if aliases_sid_dict[match[2]][0] not in unique_stakeholders:
                unique_stakeholders.add(aliases_sid_dict[match[2]][0])
                result.append(match[0])
                
        return result

# @tool 
# def get_relationships_with_names(subject_id:int = None) -> bytes:
#     '''
#     Use this tool to output to the user every relationship the stakeholders have with one another in natural language. This tool should be called when the user wants the relationships of stakeholders in natural language. 
#     This tool will return in JSON format, a list where each element is a list. The format is as such: '[[subject, predicate, object], [subject, predicate, object], ...]'. Where the subject is related to object by the predicate and the subject can have multiple relationships with objects.
#     If the output is an empty list then it means that the subject has no relationships with the object.

#     Args:
#         subject_id (int): The name of the stakeholder you want to find matches for.
        
#     Returns:
#         list: A list of subjects, predicates and objects
#     '''
    
#     with Session(stakeholder_engine) as db:
#         subject_rs = crud.get_relationships(db, subject=subject_id)
#         object_rs = crud.get_relationships(db, object=subject_id)
#         relationships = subject_rs + object_rs
#         stakeholder_ids = {result.subject for result in relationships} | {result.object for result in relationships}
#         stakeholder_names = crud.get_stakeholder_names(db, list(stakeholder_ids))

#     relationships_with_names = []
#     for result in relationships:
#         subject_name = stakeholder_names.get(result.subject, "Unknown")
#         object_name = stakeholder_names.get(result.object, "Unknown")
#         predicate = result.predicate
#         extracted_info = crud.extract_after_last_slash(predicate)
#         # Remove non-alphanumeric characters
#         extracted_info = re.sub(r'[^a-zA-Z0-9\' ]', '', extracted_info)
#         relationships_with_names.append((subject_name, extracted_info, object_name))

#     return relationships_with_names

def get_relationships_build(model):
    @tool
    def get_relationships(subject_id: int = None, prompt: str = None) -> dict:
        '''
        Use this tool to get relationships the stakeholders have with one another, based on structured data.
        The data returned by this tool is not exhaustive and may be supplemented by media data.
        This tool will be used only if the user wants a network graph. This tool will return in JSON format, a list where each element is a list. The format is as such: '[[subject, predicate, object], [subject, predicate, object], ...]'. Where the subject is related to object by the predicate and the subject can have multiple relationships with objects.
        If the output is an empty list then it means that the subject has no relationships with the object.

        Args:
            subject_id (int): The name of the stakeholder you want to find matches for.
            prompt (str): The type of matches you want to filter matches for. Note that the output of this graph will NOT be directly related to this prompt.

            
        Returns:
            relationships_with_predicates (list[list[int, str, int]]): A list of subjects, predicates and objects. 
                The subject is the stakeholder_id of the subject and it is an integer. 
                The predicate is the relationship between the subject and the object. The predicate is a string. 
                The object is the stakeholder_id of the object and it is an integer.
                This output is not directly related to the prompt, and should not be interpreted as such. Each relationship should be interpreted soley based on its subject, predicate and object.
        
        Returns:
            dict: A dictionary with "edges" and "nodes". Where "edges" is a list of tuples with the format (subject, predicate, object) and "nodes" is a dictionary with the format {stakeholder_id: stakeholder_name}.
        '''
        subject_id = int(float(subject_id))
        relationships_graph = {
            "edges": [],
            "nodes": {}
        }
        
        with Session(stakeholder_engine) as session:
            relationships = crud.get_relationships(session, subject=subject_id)
            if not relationships:
                relationships = crud.get_relationships(session, object=subject_id)
            else:
                object_rs = crud.get_relationships(session, object=subject_id)
                if object_rs:
                    relationships += object_rs
        
        if not relationships:
            return relationships_graph
        
        # Collect unique stakeholder IDs
        unique_ids = set()
        
        for result in relationships:
            predicate = re.sub(r'[^a-zA-Z0-9\' ]', '', crud.extract_after_last_slash(result.predicate))
            relationships_graph["edges"].append((result.subject, predicate, result.object))
            unique_ids.update([result.subject, result.object])
        
        # Retrieve all stakeholder names in a single query
        with Session(stakeholder_engine) as session:
            stakeholder_names = crud.get_stakeholder_names(session, list(unique_ids))
        
        relationships_graph["nodes"] = stakeholder_names

        if prompt:
            edges = filter_edges(model, prompt, relationships_graph, True).invoke({})
            relevant_nodes = set()
            for sub, _, obj in edges:
                relevant_nodes.add(sub)
                relevant_nodes.add(obj)

            relationships_graph["edges"] = edges
            relationships_graph["nodes"] = dict({int(k):v for k, v in relationships_graph["nodes"].items() if k in relevant_nodes})

        relationships_graph['type'] = 'rs_db'
        
        return relationships_graph
    return get_relationships

def filter_edges(model, prompt, graph, map_names):
    filter_prompt = ChatPromptTemplate.from_messages(
    [("system", """
    # Instructions
    You are a highly specialised tool trained in text processing.
    Your goal is to select relationships most relevant to a given prompt by indicating its number.
    Scan through all the relationships and select the relationships that are directly related to the prompt. 
    Try not to select more than 2 completely irrelevant relationships.
    
    ## Inputs
    Relationships: A numbered list of relationships of the form subject -- predicate --> object. These form a network graph.
    Prompt: A string containing the context to match against. Your result does not have to match this input.

    ## Output
    A list of numbers that map to the relationship list.
    All numbers in this list should exist in the relationship list.
    No number should appear more than once.
    If the prompt tells you to return a certain number of relationships, only return that number of relationships.
    For instance, a query on the "Top 10" stakeholders should return a list that has a maximum of ten relationships.
    
    # Example
    ## Prompt
    Who are Bob's family members?

    ## Relationships
    0. Bob Jr. -- Son --> Bob.
    1. Charlie -- Employee --> Foo Inc.
    2. Bob -- Coworker --> John
    3. Bob -- Husband --> Alice
    4. Bob -- Employee --> Foo Inc.
    5. Alice -- Sister --> Charlie

    ## Your response
    [0, 3, 5]"""),
     
    ("user", """
     Given the below input, calculate the resultant list.
     Do not output anything else.
    ## Prompt
    {prompt}

    ## Relationships
    {relationships}
    """)]
    )
    def parse_relationship(id, edge):
        # Really need to refactor
        if isinstance(edge, dict):
            sub = graph['nodes'][edge['sub']] if map_names else edge['sub']
            pred = edge['pred']
            obj = graph['nodes'][edge['obj']] if map_names else edge['obj']
        else:
            sub = graph['nodes'][edge[0]] if map_names else edge[0]
            pred = edge[1]
            obj = graph['nodes'][edge[2]] if map_names else edge[1]

        return f"{id}. {sub} -- {pred} --> {obj}"
    
    edges = '\n'.join(map(parse_relationship, *zip(*enumerate(graph['edges']))))
    def print_pt(inp):
        print(inp)
        return inp
    
    result = filter_prompt.partial(prompt = prompt, relationships = edges) | \
        model | \
        parse_list | \
        (lambda l : [e for i, e in enumerate(graph['edges']) if str(i) in l])
    
    return result

def parse_list(s):
    return [sub.strip().strip('"').strip("'") for sub in s.content.split('[', 1)[1].rsplit(']', 1)[0].split(',')]


def get_photo(stakeholder_id: int) -> str:
    stakeholder_id = int(stakeholder_id)
    with Session(stakeholder_engine) as session:
        response = session.scalars(select(Stakeholder).where(Stakeholder.stakeholder_id == stakeholder_id).limit(1)).one_or_none()
        if response is not None:
            ref_pic = response.photo
            if ref_pic:
                pic_url = ref_pic.split("||")[0].strip()  # Split by "||" and take the first URL
                return pic_url
            else:
                print(f"No photo field for get_photo({stakeholder_id}): {response}")
                return None
        else:
            print(f"stakeholder {stakeholder_id} does not exist")
            return None
        
@tool
def call_graph(reason: str) -> None:
    """
    Call this tool to activate the graphing agent only once you have obtained enough information from calling other tools.
    Information gathered involves any results directly returned from get_relationships.
    If it is not evident what the connection is between this data and the user's prompt, make more queries until it is clear.

    If you have made an inference from the data, make sure to call add_unstructured_relationships first not in parallel to save inferred relationships.
    The chat history will not be passed to the grapher.
    Only results from tools will be passed to the grapher.

    Args:
        reason (str): 
            The query to filter the results with, which should be a short phrase or sentence describing the types of relationships and how many there should be. 
            If you have identified a concrete relationship, state the start and end-points explicitly, as well as all stakeholders involved in the relationship concisely.
            For example, you may say, "Start: A, End: D. A is B, B has a C, C is involved in D.
    """
    # Note: Need to manually point this in the router
    return "calling the graphing agent..."


def read_media_build(model):
    @tool
    def read_media(query: Optional[str] = None, stakeholder_id: Optional[int] = None) -> dict:
        """
        Call this tool to extract relationships from media scraped from the web. They can be used to answer questions about people, even if the question isn't very specific.
        If given a specified stakeholder_id, this tool will extract media sources involving the stakeholder.
        These media sources will be ordered by their similarity to a given query, and only relationships from the closest matches will be returned.
        This information can be used to augment information from get_relationships or read_stakeholders if they has insufficient information.

        If you need to build a graph, make sure to call add_unstructured_relationships on the information you have extracted.
        Args:
            query (str | None): A word, short phrase or sentence that filters the type of media that this tool will search for. Leave it empty for a general overview. 
            stakeholder_id (int | None): The optional id of the stakeholder you wish to search for.
        
        Returns:
            Media content based on your query and stakeholder_id.
        """
        return derive_rs_from_media(model, query, stakeholder_id)
    
    return read_media

@tool
def add_unstructured_relationships(relationships:list[list[str]]) -> dict:
    """Add a relationship to the current working memory that will be used by the Grapher tool.
    Only call this tool if you have inferred a relationship that was not directly returned by get_relationships, and the user requests a graph.

    For example, if you learn that Bob is Alice's husband, you may call add_unstructured_relationships([["Bob", "Husband", "Alice"]]) if:
    1. It is relevant to the user's query
    2. The relationship has not already been returned by get_relationships.

    If you are already aware of the stakeholder from a previous tool call, ensure that you use exactly the same name.
    Do not call this in parallel with call_graph.

    Args:
        stakeholder_id (list[list[str, str, str]]):
            A list of relationships you wish to add.
            Example input: 
                [
                ["A", //subject, cannot be empty
                "Father", //predicate, cannot be empty
                "B"] //obj, cannot be empty
                ] 
            One relationship consists of a list of 3 strings: subject, predicate, object.
            Given the relationship A -- "Has a son who works in" --> B, consider finding the relationship A -- "Father" --> C, C -- "Works in" --> B. 
            
    Returns:
        A dictionary representation of the relationships generated from your input.
    """

    nodes = set()
    edges = []
    for edge in relationships:
        if edge[0] and edge[2]:
            nodes.add(edge[0])
            nodes.add(edge[2])
    nodes = list(nodes)
    for edge in relationships:
        if edge[0] and edge[2]:
            edges.append(
                [
                    nodes.index(edge[0]),
                    edge[1],
                    nodes.index(edge[2])
                ]
            )
    nodes = {i:v for i, v in enumerate(nodes)}
    update = {"edges": edges, "nodes": nodes, "type": "media"}
    return update


def get_tools(model):
    return [read_stakeholders, get_name_matches, read_media_build(model)]

def get_all_tools(model):
    return get_tools(model) + [call_graph, get_relationships_build(model), read_media_build(model), add_unstructured_relationships]

def get_tool_node(model):
    return ToolNode(get_tools(model))

def update_graph_structured(old: dict, new:dict) -> dict:
    #idk
    if not old:
        if not new:
            return dict()
        return new
    elif not new:
        return old
    
    nodes = old.get('nodes', {}).copy()
    nodes.update(new.get('nodes', {}))

    return {
        'edges': (old.get('edges', [])) + (new.get('edges', [])),
        'nodes': nodes
    }

def update_graph_unstructured(old: dict, new:dict) -> dict:
    if not old:
        if not new:
            return dict()
        return new
    elif not new:
        return old
    
    new_node_names = list(
        set(old.get('nodes', {}).values()).union(
        set(new.get('nodes', {}).values())))
    
    new_edges = []

    for dic in (old, new):
        ids = dic.get('nodes', {})
        remap = {id_: new_node_names.index(name) for id_, name in ids.items()}
        
        for edge in dic.get('edges'):
            try:
                new_edges.append((remap[edge[0]], edge[1], remap[edge[2]]))
            except:
                pass

    return {
        'edges': new_edges,
        'nodes': {i:v for i, v in enumerate(new_node_names)}
    }

def build_mutable_tool_nodes(model):
    def _run_one(call):
        tool = tools.get(call['name'])
        res = tool.invoke(call['args'])
        
        return {
            "messages": [ToolMessage(repr(res), tool_call_id=call['id'])],
            res['type'] : res }
    
    def mutable_tool_node(state, config=None):
        last_msg = state['messages'][-1]
        
        #Ideally, use the map-reduce pattern in langgraph instead of this
        with get_executor_for_config(config=config) as executor:
            outputs = executor.map(_run_one, [c for c in last_msg.tool_calls if c['name'] in tools])
            output = reduce(lambda a, b: {'messages': a['messages'] + b['messages'],
                                 'rs_db': update_graph_structured(a.get('rs_db'), b.get('rs_db')),
                                 'media': update_graph_unstructured(a.get('media'), b.get('media'))
                                 }, outputs)
            return output

    tools = {
        "get_relationships": get_relationships_build(model),
        "add_unstructured_relationships": add_unstructured_relationships
    }

    return mutable_tool_node

if __name__ == '__main__':
      print(get_name_matches('loheesong'))
#     print(update_graph_unstructured(
#         {
#             'nodes': {
#                     1: "Steve",
#                     2: "John",
#                     3: "Bob"},
#             'edges': [
#                 [1, 'A', 2],
#                 [1, 'B', 3]
#             ]
#         },
#         {
#             'nodes': {
#                     1: "Alice",
#                     2: "Steve",
#                     3: "Bob"},
#             'edges': [
#                 [1, 'C', 2],
#                 [1, 'D', 3]
#             ]
#         }))