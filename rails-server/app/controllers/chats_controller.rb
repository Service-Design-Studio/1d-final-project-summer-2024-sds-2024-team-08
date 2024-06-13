class ChatsController < ApplicationController
    def index
        # "convention over configuration" -> do not explicit render something at the end of controller action 
        # Rails auto look for action_name.html.erb template 

        # given a user id, get chat ids
        @user_1_chat_id = [
            {
                :id => 1,
                :title => "chat 1"
            },
            {
                :id => 2,
                :title => "chat 2"
            },
            {
                :id => 3,
                :title => "chat 3"
            },
        ]
        # click on button on sidebar -> make get request for chat messages 
        # display content on index.html
    end

    def get_chat_with_id
        @user_1_chat_id = {} # just so application.html.erb doesnt cry 
        chat_id = params[:chat_id].to_i # use :chat_id as defined in config/routes.rb, not :id like in application.html.erb
        @chat_history = get_chatid_from_db(chat_id)
        render("index")
    end 

    private # methods defined here onwards is private 
    def get_chatid_from_db(find_chat_id)
        # example content, this method will be replaced with method that calls python server 
        all_chatids_with_content = [
            {
                :id => 1,
                :content => "aaa"
            },
            {
                :id => 2,
                :content => "bbb"
            },
            {
                :id => 3,
                :content => "ccc"
            },
        ]
        all_chatids_with_content.each do |chat_history|
            if chat_history[:id] == find_chat_id
                return chat_history
            end
        end
    end 
end
