from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_google_vertexai import ChatVertexAI
from langchain_core.documents import Document

inp = '''Africa has considerable oil and gas resources that can help accelerate growth on the continent if used strategically. Although new resources are discovered progressively, they are not equally distributed. High and volatile oil prices are thus a challenge for all of Africa; they represent an opportunity to be pursued for exporting countries and an obstacle to be tackled for importing countries. Recent oil and gas discoveries coupled with regulatory changes and fast-growing energy demand from expanding local consumer markets offer significant opportunities across the continent Africa’s oil and gas industry holds huge potential. At the end of 2017, Africa was estimated to have 487.7 tcf of proven gas reserves (7.1% of global proven reserves), whilst Africa’s proven reserves of oil are in the region of 125 billion bbl. Africa’s downstream sector has been fairly static in recent years with total refinery throughput hovering around 2.1 million bbl/d, however as we’ll see a wealth of new refinery upgrades or new builds is set to change this. In African energy-exporting countries, oil and gas has historically been a primary driver of economic growth. Oil exports can account for more than 90% of. Yet, countries have been unable to harness these windfalls for sustainable economic development and this is an ongoing constraint to business. Players in the sector must also be mindful of disruptors likely to change the industry. These include rising global demand for liquefied natural gas; the growing prominence of renewables, which could have far reaching implications; and the potential of the ongoing United States and China trade dispute to disrupt global trade, oil markets and supply chains. Main Players in Africa: Nigeria is a mature oil-producing economy with substantial foreign direct investment (FDI), but delays in reforming the sector have deterred further investment. Governance challenges, corruption, as well as economic, security and high cost concerns also hinder investment. The country is still the region’s largest oil and gas producer overall and is expected to be the largest refiner and exporter of petroleum products in Africa by 2022. Improving economic conditions and transport sector growth could see domestic consumption increase by 31 per cent between 2017 and 2023. Investment in gas infrastructure, such as new pipelines, will boost production. Opportunities exist for players with the government intending to privatize ten power stations as part of efforts to guarantee an effective and sustainable power supply in the country. Angola is less attractive from a regulatory perspective. It also grapples with corruption, high business costs, low growth and a lack of business diversification. Yet, Angola has the second-largest oil resources and is the second-largest oil producer in sub-Saharan Africa. As a result, it is receiving increasing levels of FDI, boosted by the Angolan government passing several policies in early 2018 encouraging foreign investment. Angola also has the fourth-largest proven natural gas reserves, although the country only produces small amounts commercially. A 2018 presidential decree offers incentives for investment. Consumption is expected to more than double between 2017 and 2023, although the large distances between gas production sites and consumers and a lack of pipeline infrastructure are significant constraints. Mozambique holds the largest gas resources in the region, so has the largest untapped potential. Domestic and governance challenges aside, the country has seen the largest flow of FDI over the past eight years among its peers. Recent discoveries multiplied proven reserves and will underpin the country’s projected economic recovery. Plans for the coral floating liquefied natural gas development in the Rovuma Basin, as well as the Anadarko Petroleum project in the north are two prominent developments. Given the complexities of these projects, production is not expected until 2022. Tanzania has the fastest-growing economy among its oil and gas-producing peers in the region and the second-largest natural gas resources. While production is low, the discovery of new offshore fields has the potential to transform the economy. Its closer location to Asian markets gives Tanzania a geographical edge over peers, although exports of liquefied natural gas based on a planned onshore export facility have been delayed for at least five years. Despite positive developments, the oil & gas industry still faces numerous and persistent challenges around talent shortages, regulatory uncertainty, political instability, corruption and fraud, and a lack of infrastructure. SCA-Partner Company and the Oil & Gas Business in Europe and Africa SCA-Partner Company offers its clients various European Made Oil & Gas products and equipment: - Tank Vessels - Heat Exchangers - Air Coolers - Evaporators - Oil Towers - Reactor Equipment - Boiler Equipment - Pumps - Valve - LDPE - LLDPE - HDPE - Ethylene - Crude Oil - Refined Oil - Diesel - Fuel - LNG - LPG'''

prompt = 'give me a network graph of how different countries are related to one another in the oil and gas industry'

llm_transformer = LLMGraphTransformer(ChatVertexAI(model="gemini-1.5-flash", max_retries=2))

documents = [Document(page_content=inp)]

# Derive relationships from filtered media ids
graph_documents = llm_transformer.convert_to_graph_documents(documents)
nodes = graph_documents[0].nodes
rs = graph_documents[0].relationships

nodes_map = {node.id: i for i, node in enumerate(nodes)}

media_rs = []
for relation in rs:
    source_id = nodes_map.get(relation.source.id)
    target_id = nodes_map.get(relation.target.id)

    if source_id and target_id:
        media_rs.append([source_id, relation.type, target_id])
    else:
        # Either source_id or target_id does not appear in the nodes
        continue
    
result = {'nodes': {i: name for name, i in nodes_map.items()}, 'edges': media_rs, 'type': 'media'}
print(result)