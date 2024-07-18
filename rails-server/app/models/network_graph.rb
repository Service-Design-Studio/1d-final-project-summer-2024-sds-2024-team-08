class NetworkGraph < ApplicationRecord
    self.table_name = 'network_graph'

    def self.get_graph_by_id(graph_id)
        find(graph_id).attributes["content"]
    end
end