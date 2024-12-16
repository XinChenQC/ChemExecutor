import networkx as nx
import importlib
import os
import sys

# initialized nodes
def initialize_nodes_class(id: str, node_data):
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


def compGraph_init(data: str):
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
        instance = initialize_nodes_class(node_id, node_data)
        if instance:
            print(f"Initialized class: {type(instance).__name__}")
            G.nodes[node_id]['instance'] = instance
        else:
            G.nodes[node_id]['instance'] = None
           

    # First round source data initialization. Get data from previous nodes.  
    for node_id, node_data in G.nodes(data=True):
        # Collect all source node instances for the current target node
        
        source_nodes, source_edges = collect_source_nodes(G, node_id)
        # Get the instance of the target node
        
        target_instance = G.nodes[node_id]['instance']
        if(target_instance is not None):
            # Call getSource() on the target node's instance and pass the list of source node instances
            if(len(source_nodes)>0): target_instance.getSource(source_nodes, source_edges)

    return(G)

def collect_source_nodes(G, node_id):
    source_nodes = []
    source_edges = []
    for edge in G.edges(data=True):
        if edge[1] == node_id:
            print(f"    Edge ID: {edge[2]['id']}, Source: {edge[0]}, Target: {edge[1]}")
            # Get the source node
            source_node = (edge[0], G.nodes[edge[0]])
            source_nodes.append(source_node)
            source_edges.append(edge[2]['id'])
    return source_nodes, source_edges

def compGraph_run(G, task_id):
    '''
    G is the computational graph
    nodes has 'id', 'type' and 'data'
    [node]['data'] has 'input', 'output', 'options' and 'instance'
    returns: 
    '''
    status = 'error'
    tempFile = f'/home/ubuntu/temp-run/{task_id}'
    current_dir = os.getcwd()

    if not os.path.exists(tempFile):
        os.makedirs(tempFile)
    os.chdir(tempFile)

    for node_id, node_data in G.nodes(data=True):
        if node_data['instance'] is None:
            continue  # Skip this iteration if instance is None
        print(node_id, node_data['instance'].status)

    while True:
        all_f = True 
        for node_id, node_data in G.nodes(data=True):
            if node_data['instance'] is None:
                continue  # Skip this iteration if instance is None

            if node_data['instance'].status == 'w':
                node_data['instance'].compute()
                os.chdir(tempFile)
            if node_data['instance'].status != 'f' and node_data['instance'].status != 'e':
                all_f = False
                break
        if all_f:
            status = "Finished"
            break

    for node_id, node_data in G.nodes(data=True):
        if node_data['instance'] is None:
            continue  # Skip this iteration if instance is None
        print(node_id, node_data['instance'].status)
    os.chdir(current_dir)
    return(status)