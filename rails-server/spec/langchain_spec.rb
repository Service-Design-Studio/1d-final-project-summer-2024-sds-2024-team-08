# Rspec tests for the langchain API 
require 'net/http' # import to make HTTP requests 
require 'uri'
require 'json'

LANGCHAIN_API = "https://python-server-ohgaalojiq-de.a.run.app"
chat_id = 5

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

    data == nil ? "" : data["responses"]
end

describe "happy path: POST to langchain" do
    it "returns response for proper spelling of Ben Carson" do
        # rspec cannot use to_json cos ruby is dogshit 
        message = "{\"message\": \"Tell me more about Ben Carson\", \"chat_id\": #{chat_id}, \"user_id\": 3}"
        res = post_to_langchain(message)
        expect(res).to match(/.*Ben Carson.*/)
    end

    it "returns response for proper spelling of Donald Trump" do 
        message = '{"message": "Who is Donald Trump", "chat_id": 4, "user_id": 3}'
        res = post_to_langchain(message)
        expect(res).to match(/.*Donald Trump.*/)
    end 
end

describe "fuzzy find demo: POST to langchain" do
    it "returns response for lowercase of hoe biden" do
        message = "{\"message\": \"Tell me more about hoe biden\", \"chat_id\": #{chat_id}, \"user_id\": 3}"
        res = post_to_langchain(message)
        expect(res).to match(/.*[jJ]oe [bB]iden.*/)
    end

    it "returns response for lowercase of joebiden" do
        message = "{\"message\": \"Tell me more about joebiden\", \"chat_id\": #{chat_id}, \"user_id\": 3}"
        res = post_to_langchain(message)
        expect(res).to match(/.*[jJ]oe [bB]iden.*/)
    end

    it "returns response for misspelling of donal dtrump" do 
        message = "{\"message\": \"Tell me more about donal dtrump\", \"chat_id\": #{chat_id}, \"user_id\": 3}"
        res = post_to_langchain(message)
        expect(res).to match(/.*Donald Trump.*/)
    end 
end

describe "sad path demo: POST to langchain" do
    it "returns nil response for oka kurniawan" do
        message = "{\"message\": \"Tell me more about oka kurniawan\", \"chat_id\": #{chat_id}, \"user_id\": 3}"
        res = post_to_langchain(message)
        expect(res).to match(/.*I.*any.*Oka Kurniawan/)
    end
end