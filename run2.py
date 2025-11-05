from collections import defaultdict, deque
import sys


def solve(edges: list[tuple[str, str]]) -> list[str]:
    # Решение задачи об изоляции вируса

    graph = defaultdict(set)
    gateways = set()

    for node_1, node_2 in edges:
        graph[node_1].add(node_2)
        graph[node_2].add(node_1)
        if node_1.isupper():
            gateways.add(node_1)
        if node_2.isupper():
            gateways.add(node_2)

    # Собираем все коридоры от шлюзов к обычным узлам
    gateway_to_node_links = []
    for gateway in gateways:
        for neighbor in graph[gateway]:
            if not neighbor.isupper():
                gateway_to_node_links.append((gateway, neighbor))
    gateway_to_node_links = sorted(set(gateway_to_node_links))

    removed_gateway_links = set()
    virus_position = 'a'
    result = []

    def get_active_neighbors(current_node):
        #Возвращает соседей с учётом отключённых коридоров
        neighbors = []
        for neighbor in graph[current_node]:
            # Проверка: если это соединение шлюз–узел, не отключено ли оно?
            if current_node.isupper() and not neighbor.isupper():
                if (current_node, neighbor) in removed_gateway_links:
                    continue
            elif neighbor.isupper() and not current_node.isupper():
                if (neighbor, current_node) in removed_gateway_links:
                    continue
            neighbors.append(neighbor)
        return neighbors

    def bfs_distances_from(start_node):
        #Выполняет BFS и возвращает словарь расстояний от start_node до всех достижимых узлов
        distances = {start_node: 0}
        queue = deque([start_node])
        while queue:
            current = queue.popleft()
            for neighbor in get_active_neighbors(current):
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)
        return distances

    def select_target_gateway(current_position):
        #Выбирает целевой шлюз
        distances = bfs_distances_from(current_position)
        reachable_gateways = []
        for gateway in gateways:
            if gateway in distances:
                reachable_gateways.append((distances[gateway], gateway))
        if not reachable_gateways:
            return None
        # Сортируем по расстоянию, затем по имени шлюза
        reachable_gateways.sort(key=lambda item: (item[0], item[1]))
        return reachable_gateways[0][1]

    def compute_next_virus_position(current_position):
        #Определяет следующую позицию вируса
        target_gateway = select_target_gateway(current_position)
        if target_gateway is None:
            return None

        distances_from_gateway = bfs_distances_from(target_gateway)
        current_distance = distances_from_gateway.get(current_position, float('inf'))
        candidate_nodes = []
        for neighbor in get_active_neighbors(current_position):
            neighbor_distance = distances_from_gateway.get(neighbor, float('inf'))
            if neighbor_distance == current_distance - 1:
                candidate_nodes.append(neighbor)

        if not candidate_nodes:
            return None
        candidate_nodes.sort()
        return candidate_nodes[0]

    # Основной игровой цикл
    while True:
        # Проверяем, находится ли вирус рядом с каким-либо шлюзом
        adjacent_gateways = [
            neighbor for neighbor in get_active_neighbors(virus_position)
            if neighbor.isupper()
        ]

        if adjacent_gateways:
            chosen_gateway = min(adjacent_gateways)
            action = f"{chosen_gateway}-{virus_position}"
            result.append(action)
            removed_gateway_links.add((chosen_gateway, virus_position))
        else:
            # Нет немедленной угрозы — отключаем коридор, лежащий на кратчайшем пути к шлюзу
            distances_from_virus = bfs_distances_from(virus_position)
            candidate_actions = []

            for gateway in gateways:
                if gateway not in distances_from_virus:
                    continue
                for node in graph[gateway]:
                    if node.isupper():
                        continue
                    if (gateway, node) in removed_gateway_links:
                        continue
                    # Проверяем, лежит ли коридор gateway–node на кратчайшем пути
                    node_distance = distances_from_virus.get(node, float('inf'))
                    gateway_distance = distances_from_virus[gateway]
                    if node_distance + 1 == gateway_distance:
                        candidate_actions.append((gateway, node))

            # Если нет активных путей — отключаем любой оставшийся коридор к шлюзу
            if not candidate_actions:
                for gateway_link in gateway_to_node_links:
                    if gateway_link not in removed_gateway_links:
                        candidate_actions.append(gateway_link)

            candidate_actions.sort()
            selected_gateway, selected_node = candidate_actions[0]
            action = f"{selected_gateway}-{selected_node}"
            result.append(action)
            removed_gateway_links.add((selected_gateway, selected_node))

        # Вирус делает ход
        virus_position = compute_next_virus_position(virus_position)
        if virus_position is None:
            break

    return result


def main():
    edges = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            node1, sep, node2 = line.partition('-')
            if sep:
                edges.append((node1, node2))

    result = solve(edges)
    for edge in result:
        print(edge)


if __name__ == "__main__":
    main()