class Message < ApplicationRecord
    def self.get_all
        all
    end 

    # returns a single message in array 
    def self.get_message_by_message_id(message_id) 
        (res = where(message_id: message_id).first).nil? ? {} : res.attributes
    end

    # returns array of messages, empty array if no messages 
    def self.get_messages_given_chatid(chat_id)
        where(chat_id: chat_id).map{|r| r.attributes}
    end 

    def insert_new_message(chat_id, sender_id, role, content)

    end 
end