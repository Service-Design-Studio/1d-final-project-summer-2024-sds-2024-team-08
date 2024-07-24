Rails.application.routes.draw do
  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html

  # Reveal health status on /up that returns 200 if the app boots with no exceptions, otherwise 500.
  # Can be used by load balancers and uptime monitors to verify that the app is live.
  #get "up" => "rails/health#show", as: :rails_health_check

  # Defines the root path route ("/")
  # root "posts#index"
  
    root("chats#index")

    ##### Chat specific requests #####
    get("/c", to: "chats#index")
    get("c/:chat_id", to: "chats#get_chat_with_id", as: "get_chat_with_id") # display chat history 
    get('change_user/:user_id', to: 'application#change_user', as: 'change_user')

    # util endpoint for graph 
    get("/g/:graph_id", to: "chats#get_graph_with_id", as: "get_graph_with_id")

    post("c/:chat_id", to: "chats#handle_user_msg", as: "handle_user_msg") # send message 
end
