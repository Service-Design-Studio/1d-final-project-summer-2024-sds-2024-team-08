# Rspec tests for the langchain API 
require 'net/http' # import to make HTTP requests 
require 'uri'
require 'json'

LANGCHAIN_API = "https://stakeholder-api-hafh6z44mq-de.a.run.app"

def post_to_langchain(message)
    # send form contents to python side 
    langchain_endpoint = "/langchain/"
    uri = URI.parse(LANGCHAIN_API + langchain_endpoint)
    response = Net::HTTP.post(uri, message, {'content-type': 'application/json'})

    if response.is_a?(Net::HTTPSuccess)
        data = JSON.parse(response.body)
    else
        puts "Error: #{response.message}"
    end

    data["responses"]
end

describe "happy path: POST to langchain" do
    it "returns response for proper spelling of Ben Carson" do
        # rspec cannot use to_json cos ruby is dogshit 
        message = '{"message": "Tell me more about Ben Carson"}'
        res = post_to_langchain(message)
        expect(res).to match(/.*Ben Carson.*HUD Secretary.*/)
    end

    it "returns response for proper spelling of Donald Trump" do 
        message = '{"message": "Who is Donald Trump"}'
        res = post_to_langchain(message)
        expect(res).to match(/.*Donald Trump.*[pP]resident of the United States.*/)
    end 
end

describe "fuzzy find demo: POST to langchain" do
    it "returns response for lowercase of hoe biden" do
        message = '{"message": "Tell me more about hoe biden"}'
        res = post_to_langchain(message)
        expect(res).to match(/.*Which names.*[jJ]oe [bB]iden.*/)
    end

    it "returns response for lowercase of joebiden" do
        message = '{"message": "Tell me more about joebiden"}'
        res = post_to_langchain(message)
        expect(res).to match(/.*Which names.*[jJ]oe [bB]iden.*/)
    end

    it "returns response for misspelling of donal dtrump" do 
        message = '{"message": "Who is donal dtrump"}'
        res = post_to_langchain(message)
        expect(res).to match(/.*Which names.*donald trump.*/)
    end 
end

describe "sad path demo: POST to langchain" do
    it "returns nil response for oka kurniawan" do
        message = '{"message": "Tell me more about oka kurniawan"}'
        res = post_to_langchain(message)
        expect(res).to match(/.*I.*find any information.*/)
    end
end