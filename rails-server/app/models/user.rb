# class User < ApplicationRecord
#     def self.get_all
#         all
#     end 

#     # returns hash in this format {"user_id"=>1, "name"=>"Genie"}
#     def self.get_user_by_id(id) 
#         (res = where(user_id: id).first).nil? ? {} : res.attributes
#     end

#     def insert_new_user(name)

#     end 
# end
