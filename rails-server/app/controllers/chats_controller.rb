require 'net/http' # import to make HTTP requests 
require 'uri'
require 'json'

class ChatsController < ApplicationController
    before_action :set_chat_ids
    before_action :authorize_chat_access, only: [:get_chat_with_id]

    # define constants here 
    PY_SERVER_URL = "https://python-server-vdvad4wjla-de.a.run.app"
    #shifted USER to application controller

    def index # Rails auto look for action_name.html.erb template
        @chat_history = []
        @default_landing_page = true
    end

    def get_chat_with_id
        chat_id = params[:chat_id].to_i # use :chat_id as defined in config/routes.rb, not :id like in application.html.erb
        @chat_history = get_messages_given_chatid(chat_id)
        @default_landing_page = false
        render("index")
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
        chat_endpoint = "/chats?uid=#{user_id}"
        uri = URI.parse(PY_SERVER_URL + chat_endpoint)
        response = Net::HTTP.get_response(uri)

        if response.is_a?(Net::HTTPSuccess)
            data = JSON.parse(response.body)
        else
            puts "Error: #{response.message}"
            return [] 
        end

        data["chat_ids"].map {|e| {chat_id: e, chat_name: "chat id: #{e}"}}
    end

    def get_messages_given_chatid(chat_id)
        message_endpoint = "/messages?chat_id=#{chat_id}"
        uri = URI.parse(PY_SERVER_URL + message_endpoint)
        response = Net::HTTP.get_response(uri)

        if response.is_a?(Net::HTTPSuccess)
            data = JSON.parse(response.body)
            pp data
        else
            puts "Error: #{response.message}"
            return []
        end

        data["messages"]
    end 
end
