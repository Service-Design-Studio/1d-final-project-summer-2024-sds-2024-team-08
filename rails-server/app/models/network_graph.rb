class NetworkGraph < ApplicationRecord
    self.table_name = 'network_graph'

    def self.get_graph_by_id(graph_id)
        find(graph_id).attributes["content"]
    end

    def self.get_latest_graph_by_chat_id(chat_id)
        where(chat_id: chat_id).order(id: :desc).limit(1).pluck(:content).first
    end
end