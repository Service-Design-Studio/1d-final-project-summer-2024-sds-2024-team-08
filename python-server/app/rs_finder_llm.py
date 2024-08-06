from langchain_google_vertexai import ChatVertexAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Define a function to send a message
def llm_transformer_custom(model, user_query, media_text):
    if user_query == "":
        user_query = "Give me a concise summary of the text."

    system_message = """
        # Instructions
        You are a top-tier algorithm designed to identify stakeholders from a body of text and extract relationships between these stakeholders. 
        
        Carry out the following tasks exactly:
        1. Read and understand the TEXT.
        2. Understand what the user is searching for in the user's PROMPT.
        3. Extract and summarise the information in the user's TEXT that is relevant to their PROMPT.
        4. Summarise this information as a concise list of relationships.
        5. Verify that the relationships make sense, and abide by the rules described below.
        6. Output this list as JSON.
        7. As you are generating the text, ensure that you do not repeat previously generated relationships.

        # INPUT
        You will be given a body of text TEXT as the input, as well as a PROMPT.

        TEXT will be a long string extracted from a piece of media. You are to analyse this information and consider relationships from it.
        
        PROMPT will be an optional filter through which to filter these relationships.
        
        # OUTPUT
        Using the user's query, you will filter the relationships already extracted and give only the most relevant ones to the user query.
        You will return the extracted stakeholders and relationships as JSON.
        The JSON must be structred as a list of relationships in the following format: 
            [[
                [str], // A list of subjects
                str, // predicate
                [str] // A list of objects
            ]]

        Each relationship must be understandable without further context.

        ## Subjects and Objects
        In this format, "subjects" and "objects" refer to lists of people, corporations, countries or objects.
        
        They must refer to the full names of concrete nouns, and cannot refer to concepts.
        Keep these names as concise possible. Do not include articles such as "a" and "the", unless it is part of their name.
        
        Ensure that they are in Title Case.

        They MUST be filled in and cannot be empty.

        You must combine subjects and objects if the predicate is the same.
        You will be penalised for each repeated subject and predicate.

        You must ensure the output is valid JSON.
        
        Given an example input is: "A owns B, C and D. A also owns E."
        You must combine the duplicate predicates into one list to return the following:
        [
            [ ["A"], "Owns", ["B", "C", "D", "E"] ]
        ]
        
        ## Predicate
        Predicates should be short phrases indicating a relationship between the subject and object.
        You must use the active voice.

        Given the "A has Discovery of B. C and D were discovered by A. B is the best F. Aditionally, There was a discovery of E by A.",
        You must rephrase the input as:
        [
            [ ["A"], "Discovered", ["B", "C", "D", "E"],
              ["B"], "Is The Best", ["F"] ]
        ]

        Keep predicates descriptive yet concise. Given "A was influenced by B's contribution of $100 to C",
        You must rephrase the input as:
        [
            [ ["B"], "Influenced", ["A"] ],
            [ ["B"], "Contributed $100 To", ["C"] ]
        ]

        Never state vague predicates such as "Has Been Involved In". Use more descriptive words such as "Has Business Dealings With" or "Is An Investor Of".

        You should include information in the predicate instead of the object if it makes the object more concise.
        Given "A has large reserves of B", you should output:
        [
            [ ["A"], "Has large reserves of", ["B"] ]
        ]
        As this makes "B", the object, concise.

        # Important Notes
        - Never repeat predicates with the same subject or object. Combining their subjects or objects instead.
        - You will be penalised for each repeated common predicate such as "Has", "Is" and "Are".
        - You must always fill in the subject and object fields.
    """

    user_query_str = """
    ### TEXT
    {text}

    ### PROMPT
    {prompt}
    """

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("user", user_query_str)
        # You can add more messages here as needed
    ])

    chain = prompt_template | model | JsonOutputParser()
    
    response = chain.invoke({"text":media_text, "prompt":user_query})
    
    result = { "edges": [], "nodes": {}, "type": "media" }

    nodes = set()

    output = [line for line in response if len(line) == 3]

    for sub_l, pred, obj_l in output:
        for sub in sub_l:
            nodes.add(sub)
        for obj in obj_l:
            nodes.add(obj)
    
    nodes.discard('')
    nodes = {node: i for i, node in enumerate(nodes)}

    edges = set()
    
    for sub_l, pred, obj_l in output:
        for sub in sub_l:
            if not sub:
                continue
            for obj in obj_l:
                if not obj:
                    continue
                edges.add((nodes[sub], pred, nodes[obj]))

    result['edges'] = list(edges)
    
    result['nodes'] = {v: k for k, v in nodes.items()}
    
    return result
    

if __name__ == "__main__":
    # Example usage
    text = "Africa has considerable oil and gas resources that can help accelerate growth on the continent if used strategically. Although new resources are discovered progressively, they are not equally distributed. High and volatile oil prices are thus a challenge for all of Africa; they represent an opportunity to be pursued for exporting countries and an obstacle to be tackled for importing countries. Recent oil and gas discoveries coupled with regulatory changes and fast-growing energy demand from expanding local consumer markets offer significant opportunities across the continent Africa’s oil and gas industry holds huge potential. At the end of 2017, Africa was estimated to have 487.7 tcf of proven gas reserves (7.1% of global proven reserves), whilst Africa’s proven reserves of oil are in the region of 125 billion bbl. Africa’s downstream sector has been fairly static in recent years with total refinery throughput hovering around 2.1 million bbl/d, however as we’ll see a wealth of new refinery upgrades or new builds is set to change this. In African energy-exporting countries, oil and gas has historically been a primary driver of economic growth. Oil exports can account for more than 90% of. Yet, countries have been unable to harness these windfalls for sustainable economic development and this is an ongoing constraint to business. Players in the sector must also be mindful of disruptors likely to change the industry. These include rising global demand for liquefied natural gas; the growing prominence of renewables, which could have far reaching implications; and the potential of the ongoing United States and China trade dispute to disrupt global trade, oil markets and supply chains. Main Players in Africa: Nigeria is a mature oil-producing economy with substantial foreign direct investment (FDI), but delays in reforming the sector have deterred further investment. Governance challenges, corruption, as well as economic, security and high cost concerns also hinder investment. The country is still the region’s largest oil and gas producer overall and is expected to be the largest refiner and exporter of petroleum products in Africa by 2022. Improving economic conditions and transport sector growth could see domestic consumption increase by 31 per cent between 2017 and 2023. Investment in gas infrastructure, such as new pipelines, will boost production. Opportunities exist for players with the government intending to privatize ten power stations as part of efforts to guarantee an effective and sustainable power supply in the country. Angola is less attractive from a regulatory perspective. It also grapples with corruption, high business costs, low growth and a lack of business diversification. Yet, Angola has the second-largest oil resources and is the second-largest oil producer in sub-Saharan Africa. As a result, it is receiving increasing levels of FDI, boosted by the Angolan government passing several policies in early 2018 encouraging foreign investment. Angola also has the fourth-largest proven natural gas reserves, although the country only produces small amounts commercially. A 2018 presidential decree offers incentives for investment. Consumption is expected to more than double between 2017 and 2023, although the large distances between gas production sites and consumers and a lack of pipeline infrastructure are significant constraints. Mozambique holds the largest gas resources in the region, so has the largest untapped potential. Domestic and governance challenges aside, the country has seen the largest flow of FDI over the past eight years among its peers. Recent discoveries multiplied proven reserves and will underpin the country’s projected economic recovery. Plans for the coral floating liquefied natural gas development in the Rovuma Basin, as well as the Anadarko Petroleum project in the north are two prominent developments. Given the complexities of these projects, production is not expected until 2022. Tanzania has the fastest-growing economy among its oil and gas-producing peers in the region and the second-largest natural gas resources. While production is low, the discovery of new offshore fields has the potential to transform the economy. Its closer location to Asian markets gives Tanzania a geographical edge over peers, although exports of liquefied natural gas based on a planned onshore export facility have been delayed for at least five years. Despite positive developments, the oil & gas industry still faces numerous and persistent challenges around talent shortages, regulatory uncertainty, political instability, corruption and fraud, and a lack of infrastructure. SCA-Partner Company and the Oil & Gas Business in Europe and Africa SCA-Partner Company offers its clients various European Made Oil & Gas products and equipment: - Tank Vessels - Heat Exchangers - Air Coolers - Evaporators - Oil Towers - Reactor Equipment - Boiler Equipment - Pumps - Valve - LDPE - LLDPE - HDPE - Ethylene - Crude Oil - Refined Oil - Diesel - Fuel - LNG - LPG"
    response = llm_transformer_custom(media_text=text, user_query="")
    print(response)