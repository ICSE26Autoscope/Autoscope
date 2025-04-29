from collections import defaultdict, deque
import matplotlib.pyplot as plt

class CSGraph:
    def __init__(self):
        self.edges = []
        self.nodes = set()
        self.in_degree = {}

    def add_edge(self, from_node, to_node):
        self.edges.append((from_node, to_node))
        self.nodes.update([from_node, to_node])
        self.in_degree[to_node] = self.in_degree.get(to_node, 0) + 1
        if from_node not in self.in_degree:
            self.in_degree[from_node] = self.in_degree.get(from_node, 0)

    def find_root_nodes(self):
        return [node for node in self.nodes if self.in_degree.get(node, 0) == 0]


def read_graph_from_file(file_path):
    graph = CSGraph()
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if '->' not in line or not line:
                continue
            parts = line.split('->')
            if len(parts) != 2:
                continue
            from_node = parts[0].strip()
            to_node = parts[1].strip()
            graph.add_edge(from_node, to_node)
    return graph


def find_successor(edge_list, node)->list:
    successor_list = []
    for edge in edge_list:
        if edge[0] == node:
            successor_list.append(edge[1])
    return successor_list


def find_predecessor(edge_list, node) -> list:

    """

    :param node:
    :return:
    """
    predecessor_list = []
    for edge in edge_list:
        if edge[1] == node:
            predecessor_list.append(edge[0])
    return predecessor_list


def find_leaf_node(edge_list:list)->list:
    '''
    Find the leaf node of the graph.
    :param edge_list:
    :return:
    '''
    outdegree_map = defaultdict(int)

    all_nodes = set()

    for u, v in edge_list:
        outdegree_map[u] += 1
        all_nodes.add(u)
        all_nodes.add(v)

    leaf_nodes = [node for node in all_nodes if outdegree_map[node] == 0]

    return leaf_nodes


def find_root_node(edge_list: list) -> list:
    '''
    Find the root nodes of the graph.
    A root node is a node with no incoming edges (indegree = 0).

    :param edge_list: List of tuples representing directed edges (u, v) where u -> v
    :return: List of root nodes
    '''
    indegree_map = defaultdict(int)
    all_nodes = set()

    for u, v in edge_list:
        indegree_map[v] += 1  # v has an incoming edge from u
        all_nodes.add(u)
        all_nodes.add(v)

    root_nodes = [node for node in all_nodes if indegree_map[node] == 0]

    return root_nodes[0]


def split_path_into_segments(edge_list, path):

    graph = defaultdict(list)
    for u, v in edge_list:
        graph[u].append(v)

    segments = []
    current_segment = []

    for i in range(len(path)):
        node = path[i]
        current_segment.append(node)

        successors = graph.get(node, [])

        if len(successors) > 1:
            segments.append(current_segment)
            current_segment = []
        elif i == len(path) - 1:
            segments.append(current_segment)

    return segments


def find_distinct_nodes(edge_list, root):
    from collections import defaultdict
    graph = defaultdict(list)
    for u, v in edge_list:
        graph[u].append(v)
    all_paths = []

    def dfs(node, current_path):
        current_path.append(node)
        if not graph[node]:
            all_paths.append(current_path.copy())
        else:
            for successor in graph[node]:
                dfs(successor, current_path.copy())

    dfs(root, [])
    node_count = defaultdict(int)
    for path in all_paths:
        for node in path:
            node_real_name = process_node_name(node)
            node_count[node_real_name] += 1

    distinct_nodes = []
    for node_name, count_time in node_count.items():
        if count_time == 1:
            node_egde_name = reverse_node_name(node_name)
            distinct_nodes.append(node_egde_name)

    return distinct_nodes


def split_path_into_distinct_branch(edge_list, path):
    """

    :param edge_list:
    :param root:
    :param path:
    :return:
    """
    segments = split_path_into_segments(edge_list, path)
    distinct_nodes = [node for node in path]

    distinct_segments = []
    for segment in segments:
        filtered_segment = [node for node in segment if node in distinct_nodes]
        if filtered_segment:
            distinct_segments.append(filtered_segment)

    return distinct_segments


def process_node_name(node_name):
    return node_name


def reverse_node_name(node_name):
    return node_name


def plot_length_distribution(global_length_stats):
    bins = {'1': 0, '2': 0, '3': 0, '4': 0, '5+': 0}
    for length in global_length_stats:
        if length >= 5:
            bins['5+'] += 1
        else:
            bins[str(length)] += 1

    total_count = sum(bins.values())
    for k in bins:
        bins[k] = bins[k] / total_count

    plt.figure(figsize=(10, 6), dpi=600)
    plt.bar(
        bins.keys(),
        bins.values(),
        color='#23426c',
        edgecolor='black'
    )

    plt.xlabel("#DSS", fontsize=14)
    plt.tick_params(axis='both', labelsize=12)
    plt.show()
