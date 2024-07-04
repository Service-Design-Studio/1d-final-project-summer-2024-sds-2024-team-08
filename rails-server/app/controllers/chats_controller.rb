require 'net/http' # import to make HTTP requests 
require 'uri'
require 'json'

# constants here 
LANGCHAIN_API = "https://stakeholder-api-hafh6z44mq-de.a.run.app"

class ChatsController < ApplicationController
    before_action :set_chat_ids
    before_action :authorize_chat_access, only: [:get_chat_with_id]

    #shifted USER to application controller
    
    def index # Rails auto look for action_name.html.erb template
        @chat_history = []
        @default_landing_page = true
    end

    def get_chat_with_id
        @chat_id = params[:chat_id].to_i # use :chat_id as defined in config/routes.rb, not :id like in application.html.erb
        @chat_history = get_messages_given_chatid(@chat_id)
        @default_landing_page = false
        render("index")
    end 

    def handle_user_msg
        # message must be a string, post() expects a string
        message = {'message'=>params[:message]}.to_json.to_s
        puts message

        # send form contents to python side 
        langchain_endpoint = "/langchain/"
        uri = URI.parse(LANGCHAIN_API + langchain_endpoint)
        response = Net::HTTP.post(uri, message, {'content-type': 'application/json'})

        if response.is_a?(Net::HTTPSuccess)
            data = JSON.parse(response.body)
        else
            puts "Error: #{response.message}"
        end
        p data 

        # package response
        data = {"id"=>100, "role"=>"assistant", "content"=>data["responses"]}

        params[:message] = nil
        # get_chat_with_id # call this method to handle redirect to get_chat_with_id screen 
        @chat_id = params[:chat_id].to_i # use :chat_id as defined in config/routes.rb, not :id like in application.html.erb
        get_chat_with_id
        return 
    end 

    private # methods defined here onwards is private 

    def set_chat_ids
        user_id = $USER # change this to show diff users 
        @user_name = "User #{user_id}"
        @list_of_chat_ids = get_chatid_given_userid(user_id)
    end

    def authorize_chat_access
        chat_id = params[:chat_id].to_i
        unless @list_of_chat_ids.map { |chat| chat[:chat_id] }.include?(chat_id)
            redirect_to root_path, alert: "You are not authorized to access this chat."
        end
    end

    def get_chatid_given_userid(user_id)
        res = Chat.get_chatid_given_userid(user_id)
        res[:chat_ids].map {|e| {chat_id: e, chat_name: "chat id: #{e}"}}
    end

    def get_messages_given_chatid(chat_id)
        res = Message.get_messages_given_chatid(chat_id)
        res.map{|e| {"id"=> e['message_id'], "role"=> e['role'], "content"=> e['content']}}
    end 
end
