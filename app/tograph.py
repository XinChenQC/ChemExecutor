import networkx as nx
import importlib
import os
import sys

# initialized nodes
def initialize_nodes(id: str, node_data):
    class_name = node_data['type'].capitalize()
    module_name = f"app.nodes.{node_data['type']}"  # Use the type directly to form the module name
    nodeData = {  'id': id, 
                'type': node_data['type'],
                'data': node_data['data']}
    print(f"Trying to import module: {module_name}")
    try:
        module = importlib.import_module(module_name)
        print(f"Module imported: {module}")
        class_ = getattr(module, class_name)
        print(f"Class retrieved: {class_}")
        instance = class_(nodeData)
        return instance
    
    except (ImportError, AttributeError) as e:
        print(f"Error initializing class {class_name}: {e}")
        return None


def getGraph(data: str):
    G = nx.DiGraph()
    for node in data["nodes"]:
        G.add_node(node["id"], type=node["type"], data=node["data"])

    # Add edges
    for edge in data["edges"]:
        G.add_edge(edge["source"], edge["target"], id=edge["id"])
    
    # initialize the value of nodes. 
    for node_id, node_data in G.nodes(data=True):
        print(f"Node ID: {node_id}")
        print(f"Node Type: {node_data['type']}")
        print(f"Node Data: {node_data['data']}")
        print("-" * 40)
                # Print edges sourced from this node

        # Initialize the class
        instance = initialize_nodes(node_id, node_data)
        if instance:
            print(f"Initialized class: {type(instance).__name__}")
            G.nodes[node_id]['instance'] = instance
           

        # initialize the value of nodes. 
    for node_id, node_data in G.nodes(data=True):
        # Collect all source node instances for the current target node
        source_nodes = []
        source_edges =     []
        for edge in G.edges(data=True):
            if edge[1] == node_id:
                print(f"Edge ID: {edge[2]['id']}")
                print(f"Source: {edge[0]}")
                print(f"Target: {edge[1]}")
                print("*" * 30)
                
                # Get the source node
                source_node = (edge[0],G.nodes[edge[0]])
                
                #source_node = G.nodes[edge[0]]
                source_nodes.append(source_node)
                
                source_edges.append(edge[2]['id'])
        # Get the instance of the target node
        target_instance = G.nodes[node_id]['instance']
        
        # Call getSource() on the target node's instance and pass the list of source node instances
        if(len(source_nodes)>0): target_instance.getSource(source_nodes, source_edges)

