class ChatsController < ApplicationController
    before_action :set_chat_ids
    before_action :authorize_chat_access, only: [:get_chat_with_id]

    def index
        # "convention over configuration" -> do not explicit render something at the end of controller action 
        # Rails auto look for action_name.html.erb template 
        @chat_history = []
        @default_landing_page = true
    end

    def get_chat_with_id
        # FIXED # @list_of_chat_ids = [] # just so application.html.erb doesnt cry TODO: fix this 
        chat_id = params[:chat_id].to_i # use :chat_id as defined in config/routes.rb, not :id like in application.html.erb
        @chat_history = get_messages_given_chatid(chat_id)
        @default_landing_page = false
        render("index")
    end 

    private # methods defined here onwards is private 

    def set_chat_ids
        user_id = 1
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
        # temp method that emulates db call 
        user_data = [
            {
                "uid": 1,
                "chats": [
                    { chat_id: 1, chat_name: "Oil and Gas Sentiments" },
                    { chat_id: 2, chat_name: "US Strategic Petroleum Reserve" },
                    { chat_id: 3, chat_name: "Mergers and Acquisitions" }
                ]
            },
            {
                "uid": 2,
                "chats": [
                    { chat_id: 4, chat_name: "OPEC News" },
                    { chat_id: 5, chat_name: "Oil Prices Expected To Rise" }
                ]
            }
        ].detect { |user| user[:uid] == user_id }

        user_data ? user_data[:chats] : []
    end

    def get_messages_given_chatid(chat_id)
        # temp method that emulates db call 
        chat = [
      {
        chat_id: 1,
        chat_name: "Oil and Gas Sentiments",
        messages: [
          { id: 999, role: "user", content: "some fat ass string" },
          { id: 998, role: "assistant", content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut libero lacus, faucibus quis finibus sed, tempus quis ex. 
          Maecenas vel velit vitae libero commodo mollis. Fusce felis nunc, blandit a lorem at, egestas tristique nunc. Suspendisse non tellus urna. Proin aliquet leo 
          a lacinia ullamcorper. Vivamus sed arcu sed lorem dapibus facilisis. Cras tincidunt aliquam tincidunt. Donec molestie eros nisi, 
          non pulvinar enim porttitor et. Duis finibus bibendum nunc. Sed tortor erat, laoreet a laoreet eget, tristique posuere ligula. " },
          { id: 989, role: "user", content: "some fat ass string" },
          { id: 988, role: "assistant", content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut libero lacus, faucibus quis finibus sed, tempus quis ex. 
          Maecenas vel velit vitae libero commodo mollis. Fusce felis nunc, blandit a lorem at, egestas tristique nunc. Suspendisse non tellus urna. Proin aliquet leo 
          a lacinia ullamcorper. Vivamus sed arcu sed lorem dapibus facilisis. Cras tincidunt aliquam tincidunt. Donec molestie eros nisi, 
          non pulvinar enim porttitor et. Duis finibus bibendum nunc. Sed tortor erat, laoreet a laoreet eget, tristique posuere ligula. " },
          { id: 979, role: "user", content: "some fat ass string" },
          { id: 978, role: "assistant", content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut libero lacus, faucibus quis finibus sed, tempus quis ex. 
          Maecenas vel velit vitae libero commodo mollis. Fusce felis nunc, blandit a lorem at, egestas tristique nunc. Suspendisse non tellus urna. Proin aliquet leo 
          a lacinia ullamcorper. Vivamus sed arcu sed lorem dapibus facilisis. Cras tincidunt aliquam tincidunt. Donec molestie eros nisi, 
          non pulvinar enim porttitor et. Duis finibus bibendum nunc. Sed tortor erat, laoreet a laoreet eget, tristique posuere ligula. " }
        ]
      },
      {
        chat_id: 2,
        chat_name: "US Strategic Petroleum Reserve",
        messages: [
          { id: 997, role: "user", content: "help me" },
          { id: 996, role: "assistant", content: "no" }
        ]
      },
      {
        chat_id: 3,
        chat_name: "Mergers and Acquisitions",
        messages: [
          { id: 995, role: "user", content: "rails suck" },
          { id: 994, role: "assistant", content: "get railed" }
        ]
      },
      {
        chat_id: 4,
        chat_name: "OPEC News",
        messages: []
      },
      {
        chat_id: 5,
        chat_name: "Oil Prices Expected To Rise",
        messages: []
      }
    ].detect { |chat| chat[:chat_id] == chat_id }
    
    chat ? chat[:messages] : []
    end 
end
