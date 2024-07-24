from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from langgraph.checkpoint import MemorySaver

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import(
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)

import os
import requests
import urllib

# os.environ["GOOGLE_API_KEY"] = "AIzaSyBPA6ZeKF1XlFJXS5YBPBkK3xXC942vFyw"  #bannons
os.environ["GOOGLE_API_KEY"] = "AIzaSyCtKcsZVbfUtX-QMM8qkO_L9kaH-yq7hbU"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './google-creds.json'
os.environ["GOOGLE_CLOUD_PROJECT_ID"] = "gemini-test-426508"
os.environ["OPENAI_API_KEY"]="sk-proj-qxoKlAc0Jg415kEc6EQoT3BlbkFJKkSBa1fEvBV5vkbC6aiS"
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document


# from langchain_google_genai import ChatGoogleGenerativeAI
# llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo")
llm = ChatVertexAI(model="gemini-1.5-flash") 

# llm = ChatGoogleGenerativeAI(temperature=0, model="gemini-pro")
llm_transformer = LLMGraphTransformer(llm=llm)

text = """The U.S.-headquartered energy giant, ExxonMobil, is making strides in pursuing a versatile emission reduction approach to leave its mark on the global decarbonization scoreboard, as there is no single solution to the energy transition conundrum .
Illustration; Source: ExxonMobil Over the past few years, ExxonMobil has intensified its efforts to cut its greenhouse gas (GHG) emissions footprint. To this end, 2021 saw the U.S. oil major reveal its Scope 1 and 2 greenhouse gas emission-reduction plans for 2030 in comparison with 2016 levels, covering operated assets. Based on these plans the firm intends to achieve a 20-30% reduction in corporate-wide greenhouse gas intensity; a 40-50% reduction in GHG intensity of upstream operations; a 70-80% reduction in corporate-wide methane intensity; and a 60-70% reduction in corporate-wide flaring intensity.
With this at the forefront, the U.S. energy heavyweight is set on advancing a diverse range of technologies, including low-carbon hydrogen , ammonia , and carbon capture, utilization, and storage (CCUS) , which have the potential to significantly lower emissions in hard-to-abate sectors such as manufacturing and power. The company also aims to reach net zero Scope 1 and 2 GHG emissions from its operated assets by 2050, through technological advancements and the support of what it believes should be clear and consistent government policies on this issue.
Related Article long read Posted: 5 months ago ExxonMobil CEO: World in need of plan to address climate change alongside energy needs Categories: Transition Posted: 5 months ago With the political environment around the globe tending to send mixed signals on the energy transition agenda, depending on who is in power in which region and the geopolitical and other challenges the world is forced to contend with, ExxonMobil’s Low Carbon Solutions business decided to create a poll on LinkedIn, asking participants to pinpoint the primary challenge facing their company amid the energy transition.
The biggest chunk, 40%, of voters identified regulatory uncertainty as the main issue, followed by financial constraints with 26%, lack of infrastructure with 21%, and technological barriers bringing up the rear with 12% of all votes. The results of the poll do not come as a surprise given the current energy policy and investment climate around the globe.
While the U.S. has its regulatory hurdles to overcome, just like Australia and many other countries, the UK is high on the list of countries where political and fiscal uncertainty are believed to have wreaked havoc on energy investments, derailing the development of certain projects due to the hit investor confidence has taken. Some, such as Bureau Veritas , see the current issues as hidden opportunities that could, potentially, be turned into big gains in the energy transition journey.
Related Article long read Posted: 2 months ago Premium Interview with Bureau Veritas: US LNG permitting freeze could unleash upsurge in renewables and hydrogen Categories: Market Outlooks Posted: 2 months ago The American Petroleum Institute (API) , a U.S. trade association representing the oil and gas industry, is among those that see the industry’s collaboration on energy policy as an essential element for the acceleration of energy innovation and emission reductions. The U.S. has characterized methane emission cuts as a priority for its domestic oil and natural gas industry to address the risks of climate change. In line with this, the methane footprint from oil and natural gas operations has fallen by 37% since 2015 while energy production increased by 39% in the largest U.S. basins.
Mike Sommers , API’s President and CEO, highlighted: “The U.S. oil and natural gas industry is leading the world in accelerating methane detection, reduction and reporting technology and is poised to unleash low-carbon hydrogen energy at scale. To fully leverage America’s energy advantage and advance climate progress, continued collaboration between energy producers and policymakers will be essential. Furthermore, the U.S. oil and natural gas industry is also making inroads in stepping up its hydrogen game with many, along with API, expecting it to play a significant role across the low-carbon hydrogen value chain, supporting the Biden administration ’s stated goal of producing 10 million metric tons (MMT) of hydrogen by 2030 and 50 MMT by 2050. The right set of policies is believed to be the key to putting the U.S. hydrogen economy on the path to generating 700,000 jobs and an economic benefit of $140 billion by 2030, driving down CO₂ emissions in hard-to-electrify sectors such as heavy industry, aviation, steel, and cement.
Related Article Posted: 2 months ago Biden-Harris administration to back US hydrogen industry with $750 million Categories: Authorities & Government Posted: 2 months ago In light of this, ExxonMobil has upped its hydrogen ante with plans to build – what it describes as – the world’s largest low-carbon hydrogen production facility in Baytown , Texas. The U.S. player’s goal is to produce up to 1 billion cubic feet per day of low-carbon hydrogen made from natural gas at the facility, as it is convinced that scaling hydrogen solutions will help its customers meet their emission-reduction goals. Another solution the company has identified as the way to minimize carbon footprint is the maximization of carbon capture and storage (CCS) endeavors.
Aside from these, ExxonMobil’s low-carbon vision also includes lithium , with plans to spearhead this solution in North America by 2030 while also playing its part in supporting the electric vehicle revolution, as pathways to leverage innovation and collaboration to accelerate society’s path to net zero. Recently, the U.S. giant inked a project framework agreement (PFA) with JERA , Japan’s largest power generation company, to jointly explore the development of a low-carbon hydrogen and ammonia production project at its Baytown facility. The duo aims to explore together JERA’s procurement of 5 MTA of ammonia and ownership participation in the Baytown low-carbon hydrogen facility.
Related Article Posted: about 1 month ago ExxonMobil partners with JERA for its low-carbon hydrogen project Categories: Business Developments & Projects Posted: about 1 month ago Moreover, ExxonMobil disclosed a definitive agreement to acquire Pioneer Natural Resources in an all-stock transaction, valued at $59.5 billion, in October 2023. With the merger completed, the two players will have an estimated 16 billion barrels of oil-equivalent resources with more than 1.4 million net acres in the Delaware and Midland basins, creating a Permian Basin giant as production volume is set to more than double to 1.3 million barrels of oil equivalent per day, but that is not all.
Not only does the U.S. oil major intends to achieve net-zero Scope 1 and Scope 2 greenhouse gas emissions from its Permian unconventional operations by 2030, but it also plans to leverage its Permian greenhouse gas reduction plans to accelerate Pioneer’s Scope 1 and 2 net-zero emissions goal by 15 years. In addition, the U.S. oil major will also apply its technologies for monitoring, measuring, and addressing fugitive methane emissions to slash the combined companies’ methane footprint.
Darren Woods , ExxonMobil’s Chairman and CEO, emphasized: “This premier, tier-one asset is a natural fit for our Permian portfolio and gives us a greater opportunity to deploy our technology and deliver operating and capital efficiency for long-term shareholder value.
“The combination of our two companies benefits this country’s energy security and economy, and also furthers society’s environmental ambitions as we move Pioneer’s 2050 net zero goal to a 2035 plan.”
Recently, ExxonMobil bolstered its global hydrocarbon portfolio with a new oil discovery in Block 15 off the coast of Angola and a hydrocarbon discovery at an exploration well in the Petronas-operated Block 52 offshore Suriname.Related Article Posted: 2 days ago ExxonMobil hits oil offshore Angola and takes steps to search for more hydrocarbons Categories: Exploration & Production Posted: 2 days ago Prior to this, the U.S. giant made another oil discovery on the Stabroek block offshore Guyana."""

# text = """In an era characterized by rapid technological advancements, shifting global dynamics, and growing environmental concerns, the future of the oil and gas industry stands at a critical crossroads. As the world's primary energy source for decades, oil and gas have fueled economies, powered industries, and shaped geopolitical landscapes. However, the industry now faces unprecedented challenges and uncertainties that demand a re-evaluation of its trajectory. In this exploration of the future of the oil and gas industry, we delve into the emerging trends, disruptive innovations, and formidable challenges that will define its evolution in the coming years. From the rise of renewable energy sources to the impact of digitalization and the imperative of sustainable practices, the industry is undergoing a profound transformation. 1. Shifting Energy Landscape: With increasing concerns about climate change and the push for sustainable energy sources, the oil and gas industry is experiencing a shift in the energy landscape. Renewable energy sources such as solar, wind, and hydroelectric power are gaining momentum, challenging the dominance of traditional fossil fuels. As governments worldwide implement stricter regulations and incentives to promote renewable energy adoption, the oil and gas industry faces mounting pressure to diversify its energy portfolio and reduce its carbon footprint. This transition presents both challenges and opportunities, requiring the industry to innovate, invest in cleaner technologies, and adapt to a rapidly changing market driven by sustainability imperatives. 2. Technological Innovations: The future of the oil and gas industry is intertwined with technological innovations aimed at improving efficiency, reducing costs, and minimizing environmental impact. Advanced drilling techniques, robotics, artificial intelligence, and data analytics are revolutionizing exploration, production, and distribution processes. Furthermore, advancements in carbon capture and storage technologies offer promising solutions to mitigate greenhouse gas emissions associated with oil and gas operations, enhancing the industry's environmental credentials. Embracing these technological innovations not only enhances the industry's competitiveness but also underscores its commitment to sustainable practices in a rapidly evolving energy landscape. 3. Focus on Sustainability: In response to growing environmental awareness, the industry is placing a greater emphasis on sustainability. Companies are investing in cleaner technologies, carbon capture and storage (CCS) initiatives, and renewable energy projects to reduce carbon emissions and mitigate environmental impact. Moreover, partnerships between oil and gas companies and renewable energy developers are becoming more prevalent, signaling a shift towards a more integrated and diversified energy sector. By prioritizing sustainability and embracing collaboration, the oil and gas industry is positioning itself to play a crucial role in the global transition to a low-carbon future. 4. Rise of Digitalization: Digitalization is reshaping every aspect of the oil and gas industry, from exploration and production to refining and distribution. The adoption of digital technologies such as IoT sensors, automation, and predictive analytics is optimizing operations, enhancing safety, and maximizing asset performance. Additionally, digitalization enables real-time monitoring and data-driven decision-making, empowering oil and gas companies to improve efficiency and reduce downtime. As the industry continues to embrace digital transformation, the potential for innovation and optimization across the value chain becomes increasingly evident, driving sustainable growth and competitiveness in a rapidly evolving market. 5. Geopolitical Uncertainty: The oil and gas rig industry operates within a complex geopolitical landscape characterized by shifting alliances, trade tensions, and geopolitical conflicts. Uncertainty surrounding supply chains, trade agreements, and political instability in key producing"""

from test_graphing import LLMGraphTransformer

if __name__ == '__main__':
    documents = [Document(page_content=text)]
    graph_documents = llm_transformer.convert_to_graph_documents(documents)
    #* returns nodes(a list) and relationships(a list) from the graph_documents
    print(f"Nodes:{graph_documents[0].nodes}")
    print(f"Relationships:{graph_documents[0].relationships}")
    print(type(graph_documents[0].nodes))
        
        
    