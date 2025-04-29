from AutoScope.spanselection.utils.GraphUtil import split_path_into_distinct_branch


def check_graph_valid(graph):
    for edge in graph.edge:
        if "edu.fudan" in edge[0] or "edu.fudan" in edge[1]:
            return True

def branch_partition(trace_data, x_graph, utility_dict):
    trace, path = identify_path(trace_data, x_graph, utility_dict)
    span_branch = split_path_into_distinct_branch(x_graph.edge, path)
    return span_branch


def connect_nodes(edges):
    graph = {}

    for edge in edges:
        start, end = edge
        if start not in graph:
            graph[start] = {'prev': None, 'next': None}
        if end not in graph:
            graph[end] = {'prev': None, 'next': None}

        # Set predecessor and successor
        if graph[start]['next'] is not None:
            raise ValueError(f"Node {start} already has a successor, orphan node detected")
        graph[start]['next'] = end

        if graph[end]['prev'] is not None:
            raise ValueError(f"Node {end} already has a predecessor, orphan node detected")
        graph[end]['prev'] = start

    # Find the starting node (the one without a predecessor)
    start_node = None
    for node in graph:
        if graph[node]['prev'] is None:
            if start_node is not None:
                raise ValueError("Multiple starting nodes detected, orphan node detected")
            start_node = node

    if start_node is None:
        raise ValueError("No starting node found, orphan node detected")

    # Build the ordered list
    result = []
    current_node = start_node
    while current_node is not None:
        result.append(current_node)
        current_node = graph[current_node]['next']

    # Check if any nodes were not included in the result
    if len(result) != len(graph):
        raise ValueError("Orphan node detected")

    return result


