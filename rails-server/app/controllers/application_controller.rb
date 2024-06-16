class ApplicationController < ActionController::Base
    #Simulate logged-in user, prevent user from accessing chats using ID
    before_action :simulate_login

    def simulate_login
        session[:user_id] = 1 # Simulating a logged-in user with ID 1
    end

    def current_user_id
        session[:user_id]
    end

end
