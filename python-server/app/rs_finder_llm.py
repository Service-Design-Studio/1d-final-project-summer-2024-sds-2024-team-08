from langchain_google_vertexai import ChatVertexAI
from langchain_core.output_parsers import JsonOutputParser

# Define a function to send a message
def llm_transformer_custom(user_query, media_text):
    model = ChatVertexAI(model="gemini-1.5-flash", max_retries=3, temperature=0.4)
    chain = model | JsonOutputParser()
    system_message = """
        ## 1. OVERVIEW
            You are a top-tier algorithm designed to identify stakeholders from a body of text and extracting relationships between these stakeholders. 
            Extracted relationships will be returned in a JSON format.
            You are the best at what you do and you are the only one who can do it.
            It is crucial that you perform well and deliver the best results.
            If you are unsure about a stakeholder or relationship, you can skip them.
            Do not output any information that cannot be found from the text.
        
        ## 2. STAKEHOLDERS
            Stakeholders are individuals, organizations, or locations that are mentioned in the text.
            Stakeholders are identified by their names and their roles in the text.
            If a stakeholder is a person, use their full name.
            If a stakeholder is an organization, use the full name of the organization.
            If a stakeholder is a location, use the full name of the location.
            If the stakeholder are the same entity, use the same name.
            Stakeholders CANNOT BE objects, resources, abstract concepts or actions. 
            Stakeholders must always be a specific and identifiable entity, such as a person, organization, or location, with a priority on individuals.
            
        ## 3. RELATIONSHIPS
            Relationships are the connections between stakeholders.
            Relationships are identified by their types and the stakeholders involved.
            For relationships, use words or phrases that describe the connection between stakeholders. Keep these words and phrases to a maximum of 2 words.
            These words or phrases should be simple and easy to understand. 
            These relationships cannot contain any punctuation or special characters.
            Keep the relationships clear, concise and uniform. To be uniform means that the relationships should be consistent in their structure. 
            Use the same words or phrases to describe the same type of relationship.
            Keep in mind that relationships are not always direct and can be inferred from the text.
            If a relationship is inferred, make sure to indicate that in the relationship type
            Predicates should be:
                - Specific: Clearly define the type of relationship, avoiding vague terms.
                - Contextual: Reflect the specific context provided in the text.
                - Consistent: Use the same predicates for similar types of relationships to maintain uniformity.
                
                Examples of appropriate predicates include "regulated by," "collaborating with," "impacted by," "utilizing," "investing in," etc. These predicates should accurately describe the interaction or connection between StakeholderA and StakeholderB.
                
        ## 4. FILTERING
            After extracting the relationships, you will THEN filter the relationships from the ones you have initially identified. You will give only the most relevant ones to the user query if it is provided: {user_query}.
            You will compare each relationship to the user_query and return only the most relevant relationships.
            Exclude the relationships that are not relevant to the user query. 
            If you are unsure about the relevance of a relationship, just include it in the output.
            Make sure that you filter only based on the relationships already extracted. So if there is a filter, your final output should be smaller than the initial output.
            

        ## 5. INPUT
            You will be given a body of text as the input.
            
            ## Example Input
                Text: The U.S.-headquartered energy giant, ExxonMobil, is making strides in pursuing a versatile emission reduction approach to leave its mark on the global decarbonization scoreboard, as there is no single solution to the energy transition conundrum . Illustration; Source: ExxonMobil Over the past few years, ExxonMobil has intensified its efforts to cut its greenhouse gas (GHG) emissions footprint. To this end, 2021 saw the U.S. oil major reveal its Scope 1 and 2 greenhouse gas emission-reduction plans for 2030 in comparison with 2016 levels, covering operated assets. Based on these plans the firm intends to achieve a 20-30% reduction in corporate-wide greenhouse gas intensity; a 40-50% reduction in GHG intensity of upstream operations; a 70-80% reduction in corporate-wide methane intensity; and a 60-70% reduction in corporate-wide flaring intensity. With this at the forefront, the U.S. energy heavyweight is set on advancing a diverse range of technologies, including low-carbon hydrogen , ammonia , and carbon capture, utilization, and storage (CCUS) , which have the potential to significantly lower emissions in hard-to-abate sectors such as manufacturing and power. The company also aims to reach net zero Scope 1 and 2 GHG emissions from its operated assets by 2050, through technological advancements and the support of what it believes should be clear and consistent government policies on this issue. Related Article long read Posted: 5 months ago ExxonMobil CEO: World in need of plan to address climate change alongside energy needs Categories: Transition Posted: 5 months ago With the political environment around the globe tending to send mixed signals on the energy transition agenda, depending on who is in power in which region and the geopolitical and other challenges the world is forced to contend with, ExxonMobil’s Low Carbon Solutions business decided to create a poll on LinkedIn, asking participants to pinpoint the primary challenge facing their company amid the energy transition. The biggest chunk, 40%, of voters identified regulatory uncertainty as the main issue, followed by financial constraints with 26%, lack of infrastructure with 21%, and technological barriers bringing up the rear with 12% of all votes. The results of the poll do not come as a surprise given the current energy policy and investment climate around the globe. While the U.S. has its regulatory hurdles to overcome, just like Australia and many other countries, the UK is high on the list of countries where political and fiscal uncertainty are believed to have wreaked havoc on energy investments, derailing the development of certain projects due to the hit investor confidence has taken. Some, such as Bureau Veritas , see the current issues as hidden opportunities that could, potentially, be turned into big gains in the energy transition journey. Related Article long read Posted: 2 months ago Premium Interview with Bureau Veritas: US LNG permitting freeze could unleash upsurge in renewables and hydrogen Categories: Market Outlooks Posted: 2 months ago The American Petroleum Institute (API) , a U.S. trade association representing the oil and gas industry, is among those that see the industry’s collaboration on energy policy as an essential element for the acceleration of energy innovation and emission reductions. The U.S. has characterized methane emission cuts as a priority for its domestic oil and natural gas industry to address the risks of climate change. In line with this, the methane footprint from oil and natural gas operations has fallen by 37% since 2015 while energy production increased by 39% in the largest U.S. basins. Mike Sommers , API’s President and CEO, highlighted: “The U.S. oil and natural gas industry is leading the world in accelerating methane detection, reduction and reporting technology and is poised to unleash low-carbon hydrogen energy at scale. To fully leverage America’s energy advantage and advance climate progress, continued collaboration between energy producers and policymakers will be essential.” Furthermore, the U.S. oil and natural gas industry is also making inroads in stepping up its hydrogen game with many, along with API, expecting it to play a significant role across the low-carbon hydrogen value chain, supporting the Biden administration ’s stated goal of producing 10 million metric tons (MMT) of hydrogen by 2030 and 50 MMT by 2050. The right set of policies is believed to be the key to putting the U.S. hydrogen economy on the path to generating 700,000 jobs and an economic benefit of $140 billion by 2030, driving down CO₂ emissions in hard-to-electrify sectors such as heavy industry, aviation, steel, and cement. Related Article Posted: 2 months ago Biden-Harris administration to back US hydrogen industry with $750 million Categories: Authorities & Government Posted: 2 months ago In light of this, ExxonMobil has upped its hydrogen ante with plans to build – what it describes as – the world’s largest low-carbon hydrogen production facility in Baytown , Texas. The U.S. player’s goal is to produce up to 1 billion cubic feet per day of low-carbon hydrogen made from natural gas at the facility, as it is convinced that scaling hydrogen solutions will help its customers meet their emission-reduction goals. Another solution the company has identified as the way to minimize carbon footprint is the maximization of carbon capture and storage (CCS) endeavors. Aside from these, ExxonMobil’s low-carbon vision also includes lithium , with plans to spearhead this solution in North America by 2030 while also playing its part in supporting the electric vehicle revolution, as pathways to leverage innovation and collaboration to accelerate society’s path to net zero. Recently, the U.S. giant inked a project framework agreement (PFA) with JERA , Japan’s largest power generation company, to jointly explore the development of a low-carbon hydrogen and ammonia production project at its Baytown facility. The duo aims to explore together JERA’s procurement of 5 MTA of ammonia and ownership participation in the Baytown low-carbon hydrogen facility. Related Article Posted: about 1 month ago ExxonMobil partners with JERA for its low-carbon hydrogen project Categories: Business Developments & Projects Posted: about 1 month ago Moreover, ExxonMobil disclosed a definitive agreement to acquire Pioneer Natural Resources in an all-stock transaction, valued at $59.5 billion, in October 2023. With the merger completed, the two players will have an estimated 16 billion barrels of oil-equivalent resources with more than 1.4 million net acres in the Delaware and Midland basins, creating a Permian Basin giant as production volume is set to more than double to 1.3 million barrels of oil equivalent per day, but that is not all. Not only does the U.S. oil major intends to achieve net-zero Scope 1 and Scope 2 greenhouse gas emissions from its Permian unconventional operations by 2030, but it also plans to leverage its Permian greenhouse gas reduction plans to accelerate Pioneer’s Scope 1 and 2 net-zero emissions goal by 15 years. In addition, the U.S. oil major will also apply its technologies for monitoring, measuring, and addressing fugitive methane emissions to slash the combined companies’ methane footprint. Darren Woods , ExxonMobil’s Chairman and CEO, emphasized: “This premier, tier-one asset is a natural fit for our Permian portfolio and gives us a greater opportunity to deploy our technology and deliver operating and capital efficiency for long-term shareholder value. “The combination of our two companies benefits this country’s energy security and economy, and also furthers society’s environmental ambitions as we move Pioneer’s 2050 net zero goal to a 2035 plan.” Recently, ExxonMobil bolstered its global hydrocarbon portfolio with a new oil discovery in Block 15 off the coast of Angola and a hydrocarbon discovery at an exploration well in the Petronas-operated Block 52 offshore Suriname. Related Article Posted: 2 days ago ExxonMobil hits oil offshore Angola and takes steps to search for more hydrocarbons Categories: Exploration & Production Posted: 2 days ago Prior to this, the U.S. giant made another oil discovery on the Stabroek block offshore Guyana.
        ## 6. OUTPUT
            Using {user_query}, you will filter the relationships already extracted and give only the most relevant ones to the user query.
            You will return the extracted stakeholders and relationships in a JSON format.
            The JSON format should be clear, concise and uniform.
            The JSON format should be easy to read and understand.
            The JSON format should be structred with output as the key and the result should be in the following format: {output: [[stakeholder1, predicate, stakeholder2], [stakeholder1, predicate, stakeholder3], ...]}. The value of the key should be a list of lists. 
            The JSON format should be consistent in its structure.
            
            ## Example Output
                If user_query is "":
                    {
                    "output": [
                        ["ExxonMobil", "regulated by", "U.S."],
                        ["ExxonMobil", "regulated by", "UK"],
                        ["ExxonMobil", "regulated by", "Australia"],
                        ["ExxonMobil", "regulated by", "Biden administration"],
                        ["ExxonMobil", "investing in", "low-carbon hydrogen"],
                        ["ExxonMobil", "investing in", "ammonia"],
                        ["ExxonMobil", "investing in", "carbon capture, utilization, and storage (CCUS)"],
                        ["ExxonMobil", "investing in", "lithium"],
                        ["ExxonMobil", "investing in", "electric vehicle revolution"],
                        ["ExxonMobil", "investing in", "Permian Basin"],
                        ["ExxonMobil", "investing in", "Block 15"],
                        ["ExxonMobil", "investing in", "Block 52"],
                        ["ExxonMobil", "investing in", "Stabroek block"],
                        ["ExxonMobil", "collaborating with", "JERA"],
                        ["ExxonMobil", "acquiring", "Pioneer Natural Resources"],
                        ["ExxonMobil", "impacted by", "regulatory uncertainty"],
                        ["ExxonMobil", "impacted by", "financial constraints"],
                        ["ExxonMobil", "impacted by", "lack of infrastructure"],
                        ["ExxonMobil", "impacted by", "technological barriers"],
                        ["ExxonMobil", "impacted by", "political and fiscal uncertainty"],
                        ["ExxonMobil", "impacted by", "hit investor confidence"],
                        ["Bureau Veritas", "seeing", "hidden opportunities"],
                        ["American Petroleum Institute (API)", "collaborating with", "energy producers"],
                        ["American Petroleum Institute (API)", "collaborating with", "policymakers"],
                        ["Mike Sommers", "leading", "U.S. oil and natural gas industry"],
                        ["Mike Sommers", "leading", "methane detection, reduction and reporting technology"],
                        ["Mike Sommers", "leading", "low-carbon hydrogen energy"],
                        ["Darren Woods", "leading", "ExxonMobil"],
                        ["JERA", "procuring", "ammonia"],
                        ["JERA", "owning", "Baytown low-carbon hydrogen facility"],
                        ["Pioneer Natural Resources", "merging with", "ExxonMobil"],
                        ["Biden administration", "producing", "hydrogen"],
                        ["Baytown", "hosting", "ExxonMobil's hydrogen facility"],
                        ["Texas", "hosting", "ExxonMobil's hydrogen facility"],
                        ["Delaware", "containing", "Pioneer Natural Resources' assets"],
                        ["Midland", "containing", "Pioneer Natural Resources' assets"],
                        ["Angola", "hosting", "ExxonMobil's oil discovery"],
                        ["Suriname", "hosting", "ExxonMobil's hydrocarbon discovery"],
                        ["Guyana", "hosting", "ExxonMobil's oil discovery"]
                        ]
                    }
                If user_query is "I only want connections of ExxonMobil":
                    {
                    "output": [
                        ["ExxonMobil", "regulated by", "U.S."],
                        ["ExxonMobil", "regulated by", "UK"],
                        ["ExxonMobil", "regulated by", "Australia"],
                        ["ExxonMobil", "regulated by", "Biden administration"],
                        ["ExxonMobil", "investing in", "low-carbon hydrogen"],
                        ["ExxonMobil", "investing in", "ammonia"],
                        ["ExxonMobil", "investing in", "carbon capture, utilization, and storage (CCUS)"],
                        ["ExxonMobil", "investing in", "lithium"],
                        ["ExxonMobil", "investing in", "electric vehicle revolution"],
                        ["ExxonMobil", "investing in", "Permian Basin"],
                        ["ExxonMobil", "investing in", "Block 15"],
                        ["ExxonMobil", "investing in", "Block 52"],
                        ["ExxonMobil", "investing in", "Stabroek block"],
                        ["ExxonMobil", "collaborating with", "JERA"],
                        ["ExxonMobil", "acquiring", "Pioneer Natural Resources"],
                        ["ExxonMobil", "impacted by", "regulatory uncertainty"],
                        ["ExxonMobil", "impacted by", "financial constraints"],
                        ["ExxonMobil", "impacted by", "lack of infrastructure"],
                        ["ExxonMobil", "impacted by", "technological barriers"],
                        ["ExxonMobil", "impacted by", "political and fiscal uncertainty"],
                        ["ExxonMobil", "impacted by", "hit investor confidence"],
                        ["Darren Woods", "leading", "ExxonMobil"],
                        ["Pioneer Natural Resources", "merging with", "ExxonMobil"],
                        ["Baytown", "hosting", "ExxonMobil's hydrogen facility"],
                        ["Texas", "hosting", "ExxonMobil's hydrogen facility"],
                        ["Angola", "hosting", "ExxonMobil's oil discovery"],
                        ["Suriname", "hosting", "ExxonMobil's hydrocarbon discovery"],
                        ["Guyana", "hosting", "ExxonMobil's oil discovery"]
                        ]
                    }
                    
                If user_query is "I only want connections of ExxonMobil with its leaders":
                    {
                    "output": [
                        ["Darren Woods", "leading", "ExxonMobil"]
                        ]
                    }
                    
        ## 7. RULES
            DO NOT return multiple relationships that are not unique. If they are the same relationship, only return it once.
            Non-compliance can also occur when stakeholders are not identified correctly or if the stakeholder does not exist.
            Non-compliance can occur when stakeholders identified are not an individual, organization, or location.
            Non-compliance can occur if abstract concepts, actions, or qualities are used as StakeholderB instead of tangible entities.
            Non-compliance is when the relationships are not clear, concise, or uniform.
            Non-compliance can occur if predicates do not accurately describe the relationship or are too vague.
            Non-compliance can also occur when relationships contain punctuation or special characters.
            Non-compliance can also occur when relationships are not consistent in their structure.
            Non-compliance can occur when your output is not in the correct format.
            Non-compliance will result in TERMINATION.
    """
    # The length of the list should be kept to a maximum of 30. If there are more than 30 relationships extracted, filter the relationships and give only the most relevant ones to the user query.
    # Non-compliance can occur when your output value has length greater than 30.
    conversation = [
        {"role": "system", "content": system_message},
        # You can add more messages here as needed
    ]
    
    conversation.append({"role": "user", "content": media_text, "user_query": user_query})
    response = chain.invoke(conversation)
    print(response)
    result = { "edges": [], "nodes": {}}
    i = 0
    for rs in response['output']:
        if rs[0] not in result['nodes']:
            result['nodes'][i] = rs[0]
            rs[0] = i
            i += 1
        if rs[2] not in result['nodes']:
            result['nodes'][i] = rs[2]
            rs[2] = i
            i += 1
        result['edges'].append(rs)
        
    return result
    

if __name__ == "__main__":
    # Example usage
    text = "Africa has considerable oil and gas resources that can help accelerate growth on the continent if used strategically. Although new resources are discovered progressively, they are not equally distributed. High and volatile oil prices are thus a challenge for all of Africa; they represent an opportunity to be pursued for exporting countries and an obstacle to be tackled for importing countries. Recent oil and gas discoveries coupled with regulatory changes and fast-growing energy demand from expanding local consumer markets offer significant opportunities across the continent Africa’s oil and gas industry holds huge potential. At the end of 2017, Africa was estimated to have 487.7 tcf of proven gas reserves (7.1% of global proven reserves), whilst Africa’s proven reserves of oil are in the region of 125 billion bbl. Africa’s downstream sector has been fairly static in recent years with total refinery throughput hovering around 2.1 million bbl/d, however as we’ll see a wealth of new refinery upgrades or new builds is set to change this. In African energy-exporting countries, oil and gas has historically been a primary driver of economic growth. Oil exports can account for more than 90% of. Yet, countries have been unable to harness these windfalls for sustainable economic development and this is an ongoing constraint to business. Players in the sector must also be mindful of disruptors likely to change the industry. These include rising global demand for liquefied natural gas; the growing prominence of renewables, which could have far reaching implications; and the potential of the ongoing United States and China trade dispute to disrupt global trade, oil markets and supply chains. Main Players in Africa: Nigeria is a mature oil-producing economy with substantial foreign direct investment (FDI), but delays in reforming the sector have deterred further investment. Governance challenges, corruption, as well as economic, security and high cost concerns also hinder investment. The country is still the region’s largest oil and gas producer overall and is expected to be the largest refiner and exporter of petroleum products in Africa by 2022. Improving economic conditions and transport sector growth could see domestic consumption increase by 31 per cent between 2017 and 2023. Investment in gas infrastructure, such as new pipelines, will boost production. Opportunities exist for players with the government intending to privatize ten power stations as part of efforts to guarantee an effective and sustainable power supply in the country. Angola is less attractive from a regulatory perspective. It also grapples with corruption, high business costs, low growth and a lack of business diversification. Yet, Angola has the second-largest oil resources and is the second-largest oil producer in sub-Saharan Africa. As a result, it is receiving increasing levels of FDI, boosted by the Angolan government passing several policies in early 2018 encouraging foreign investment. Angola also has the fourth-largest proven natural gas reserves, although the country only produces small amounts commercially. A 2018 presidential decree offers incentives for investment. Consumption is expected to more than double between 2017 and 2023, although the large distances between gas production sites and consumers and a lack of pipeline infrastructure are significant constraints. Mozambique holds the largest gas resources in the region, so has the largest untapped potential. Domestic and governance challenges aside, the country has seen the largest flow of FDI over the past eight years among its peers. Recent discoveries multiplied proven reserves and will underpin the country’s projected economic recovery. Plans for the coral floating liquefied natural gas development in the Rovuma Basin, as well as the Anadarko Petroleum project in the north are two prominent developments. Given the complexities of these projects, production is not expected until 2022. Tanzania has the fastest-growing economy among its oil and gas-producing peers in the region and the second-largest natural gas resources. While production is low, the discovery of new offshore fields has the potential to transform the economy. Its closer location to Asian markets gives Tanzania a geographical edge over peers, although exports of liquefied natural gas based on a planned onshore export facility have been delayed for at least five years. Despite positive developments, the oil & gas industry still faces numerous and persistent challenges around talent shortages, regulatory uncertainty, political instability, corruption and fraud, and a lack of infrastructure. SCA-Partner Company and the Oil & Gas Business in Europe and Africa SCA-Partner Company offers its clients various European Made Oil & Gas products and equipment: - Tank Vessels - Heat Exchangers - Air Coolers - Evaporators - Oil Towers - Reactor Equipment - Boiler Equipment - Pumps - Valve - LDPE - LLDPE - HDPE - Ethylene - Crude Oil - Refined Oil - Diesel - Fuel - LNG - LPG"
    response = llm_transformer_custom(media_text=text, user_query="I only want relationships to understand who exports what type of fuel in Africa")
    print(response)