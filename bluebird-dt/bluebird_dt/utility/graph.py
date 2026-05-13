from collections import defaultdict


def build_from_edges(edges: list[tuple[str, str]]) -> dict[str, list[str]]:
    """
    Build an undirected graph from a list of edges.
    """

    graph: defaultdict[str, list[str]] = defaultdict(list)
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)

    for node in graph:
        graph[node] = list(dict.fromkeys(graph[node]))

    return graph


def shortest_path(graph: dict[str, list[str]], start: str, end: str, path: list[str] | None = None) -> list[str] | None:
    """
    Find the shortest path between two nodes.
    """

    path = [start] if path is None else [*path, start]

    if start == end:
        return path

    shortest = None
    for node in graph[start]:
        if node not in path:
            new_path = shortest_path(graph, node, end, path)
            if new_path and ((not shortest) or (len(new_path) < len(shortest))):
                shortest = new_path

    return shortest
