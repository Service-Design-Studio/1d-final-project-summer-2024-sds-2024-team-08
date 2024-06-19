class ApplicationController < ActionController::Base
    #Simulate logged-in user, prevent user from accessing chats using ID
    before_action :simulate_login
    USER = 2

    def simulate_login(user_id = nil)
        session[:user_id] = USER # Simulating a logged-in user with ID 1
    end

    def current_user_id
        session[:user_id]
    end

end
