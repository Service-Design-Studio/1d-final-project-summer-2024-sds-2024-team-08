class Chat < ApplicationRecord
    def self.get_all
        # all
    end 

    # returns array of chats associated with user, empty array if no chats 
    def self.get_chatid_given_userid(user_id) 
        # handles nil 
        res = where(user_id: user_id)
        {"uid": user_id, "chat_ids": res.map {|e| e.chat_id}}
    end

    def insert_new_chat(user_id)

    end
end