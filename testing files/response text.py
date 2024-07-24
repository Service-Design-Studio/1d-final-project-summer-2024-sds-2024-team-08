from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
import os
import requests
import urllib
from langchain_core.messages import AIMessage , ToolMessage


response = [{'agent': {'messages': [AIMessage(content='', additional_kwargs={'function_call': {'name': 'read_stakeholders', 'arguments': '{"summary": true, "name": "Ben Carson"}'}}, 
                                              
    response_metadata={'is_blocked': False, 'safety_ratings': [{'category': 'HARM_CATEGORY_HATE_SPEECH', 'probability_label': 'NEGLIGIBLE', 'blocked': False, 'severity': 'HARM_SEVERITY_NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'probability_label': 'NEGLIGIBLE', 'blocked': False, 'severity': 'HARM_SEVERITY_LOW'}, {'category': 'HARM_CATEGORY_HARASSMENT', 'probability_label': 'NEGLIGIBLE', 'blocked': False, 'severity': 'HARM_SEVERITY_NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'probability_label': 'NEGLIGIBLE', 'blocked': False, 'severity': 'HARM_SEVERITY_NEGLIGIBLE'}], 'usage_metadata': {'prompt_token_count': 208, 'candidates_token_count': 8, 'total_token_count': 216}}, id='run-59192db1-46aa-49a8-b6ad-93a5b1137bab-0', tool_calls=[{'name': 'read_stakeholders', 'args': {'summary': True, 'name': 'Ben Carson'}, 'id': '9653c284-85f2-4a82-8d3f-ffeb33ab9a9e'}], 
    
    
    usage_metadata={'input_tokens': 208, 'output_tokens': 8, 'total_tokens': 216})]}}, {'tools': {'messages': [ToolMessage(content='b\'[{"name":"Ben Carson","headline":"HUD Secretary|| American neurosurgeon and politician (born 1951)","summary":"BENJAMIN CARSON. Dr. Carson has served as a Kellogg Director since 1997. He is Professor and Director of Pediatric Neurosurgery, The Johns Hopkins Medical Institutions, a position he has held since 1984, as well as Professor of Oncology, Plastic Surgery, Pediatrics and Neurosurgery at The Johns Hopkins Medical Institutions. Dr. Carson is also a director of Costco Wholesale Corporation.","photo":"https://commons.wikimedia.org/wiki/Special:FilePath/Ben Carson official portrait.jpg","source":"littlesis|| wikidata","source_id":"1524|| Q816459","series":6,"stakeholder_id":1}]\'', name='read_stakeholders', id='af8aa1d0-673b-48c5-bac0-90e9384755b3', tool_call_id='9653c284-85f2-4a82-8d3f-ffeb33ab9a9e')]}}, 
           
           
            {'agent': {'messages': [AIMessage(content='Ben Carson is a American neurosurgeon and politician (born 1951). He served as a Kellogg Director since 1997. He is Professor and Director of Pediatric Neurosurgery, The Johns Hopkins Medical Institutions, a position he has held since 1984, as well as Professor of Oncology, Plastic Surgery, Pediatrics and Neurosurgery at The Johns Hopkins Medical Institutions. Dr. Carson is also a director of Costco Wholesale Corporation. \n', 
                                              
    response_metadata={'is_blocked': False, 'safety_ratings': [{'category': 'HARM_CATEGORY_HATE_SPEECH', 'probability_label': 'NEGLIGIBLE', 'blocked': False, 'severity': 'HARM_SEVERITY_NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'probability_label': 'NEGLIGIBLE', 'blocked': False, 'severity': 'HARM_SEVERITY_NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_HARASSMENT', 'probability_label': 'NEGLIGIBLE', 'blocked': False, 'severity': 'HARM_SEVERITY_NEGLIGIBLE'}, {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'probability_label': 'NEGLIGIBLE', 'blocked': False, 'severity': 'HARM_SEVERITY_NEGLIGIBLE'}], 'citation_metadata': {'citations': [{'start_index': 98, 'end_index': 238, 'uri': '', 'title': '', 'license_': ''}]}, 'usage_metadata': {'prompt_token_count': 394, 'candidates_token_count': 93, 'total_token_count': 487}}, id='run-665ddf6f-4bfd-414d-96cc-fa51d5da5379-0', 
    
    usage_metadata={'input_tokens': 394, 'output_tokens': 93, 'total_tokens': 487})]}}]

# print(response[-1]['agent']['messages'][-1].content)
print(response[-1])