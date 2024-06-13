class ChatsController < ApplicationController
    def index
        # "convention over configuration" -> do not explicit render something at the end of controller action 
        # Rails auto look for action_name.html.erb template 
        user = 1
        @list_of_chat_ids = get_chatid_given_userid(user)
        @chat_history = []
    end

    def get_chat_with_id
        @list_of_chat_ids = [] # just so application.html.erb doesnt cry TODO: fix this 
        chat_id = params[:chat_id].to_i # use :chat_id as defined in config/routes.rb, not :id like in application.html.erb
        @chat_history = get_messages_given_chatid(chat_id)
        render("index")
    end 

    private # methods defined here onwards is private 
    def get_chatid_given_userid(user_id)
        # temp method that emulates db call 
        content = [
            {
                "uid": 1,
                "chat_ids": [1,4,5]
            },
            {
                "uid": 2,
                "chat_ids": [2,3]
            }
        ].detect{|user| user[:uid] == user_id}[:chat_ids]
    end

    def get_messages_given_chatid(chat_id)
        # temp method that emulates db call 
        content = [
            {
                "chat_id": 1,
                "messages": [
                    {"id": 999, "role": "user", "content": "some fat ass string"},
                    {"id": 998, "role": "assistant", "content": "assistant dump truck"},
                ]
            },
            {
                "chat_id": 2,
                "messages": [
                    {"id": 997, "role": "user", "content": "help me"},
                    {"id": 996, "role": "assistant", "content": "no"},
                ]
            },
            {
                "chat_id": 3,
                "messages": [
                    {"id": 995, "role": "user", "content": "rails suck"},
                    {"id": 994, "role": "assistant", "content": "get railed"},
                ]
            },
            {
                "chat_id": 4,
                "messages": []
            },
            {
                "chat_id": 5,
                "messages": []
            }
        ].detect{|chat| chat[:chat_id] == chat_id}[:messages]
    end 
end
