class ApplicationController < ActionController::Base
    #Simulate logged-in user, prevent user from accessing chats using ID
    before_action :simulate_login
    $USER = 2

    def simulate_login
        session[:user_id] = $USER # Simulating a logged-in user with ID 1
    end

    def current_user_id
        session[:user_id]
    end

    def change_user
        user_id = params[:user_id].to_i
        $USER = user_id
        simulate_login
        redirect_to root_path, notice: "Switched to User #{user_id}"
    end

end
