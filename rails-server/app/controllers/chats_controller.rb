require 'net/http' # import to make HTTP requests 
require 'uri'
require 'json'

# constants here 
LANGCHAIN_API = "https://python-server-ohgaalojiq-de.a.run.app/"

class ChatsController < ApplicationController
    before_action :set_chat_ids
    before_action :authorize_chat_access, only: [:get_chat_with_id]

    #shifted USER to application controller
    
    def index # Rails auto look for action_name.html.erb template
        @chat_id = params[:chat_id] || 0
        @chat_history = []
        @default_landing_page = true

    end

    # run this when user go to /c/:id 
    def get_chat_with_id
        @chat_id = params[:chat_id].to_i # use :chat_id as defined in config/routes.rb, not :id like in application.html.erb
        
        # this fetches all messages to display, will need to change this if we using JS to load messages async
        @chat_history = get_messages_given_chatid(@chat_id)
        @default_landing_page = false
        render("index")
    end 

    # run this when user send query 
    def handle_user_msg
        # handle empty request 
        # if params[:message] == "" 
        #     params[:message] = nil
        #     get_chat_with_id # call this method to handle redirect to get_chat_with_id screen 
        #     return 
        # end 

        # message must be a string, post() expects a string
        message = {'message'=>params[:message], 'chat_id'=>params[:chat_id], 'user_id'=> $USER}.to_json.to_s
        puts message

        # send form contents to python side 
        langchain_endpoint = "/langchain/"
        uri = URI.parse(LANGCHAIN_API + langchain_endpoint)
        Net::HTTP.post(uri, message, {'content-type': 'application/json'})

        # reset message to have empty text input 
        params[:message] = nil
        get_chat_with_id # call this method to handle redirect to get_chat_with_id screen 
        return 
    end 

    # for /g/:graph_id endpoint 
    def get_graph_with_id
        graph_id = params[:graph_id]

        # pull graph html from db 
        @graph_content = NetworkGraph.get_graph_by_id(graph_id)
        render("graph", layout: false) # dont use application.html.erb as template 
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

    # prepares each message for display in erb file, prepare network graph html also 
    def get_messages_given_chatid(chat_id)
        res = Message.get_messages_given_chatid(chat_id)
        res.map{|e| {"id"=> e['message_id'],
                    "role"=> e['role'],
                    "content"=> e['content'],
                    "graph_id"=> e['network_graph_id']}}
    end 
end
