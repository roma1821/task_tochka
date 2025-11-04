import sys
import heapq

MOVE_COST = {'A': 1, 'B': 10, 'C': 100, 'D': 1000}
ROOM_IDX = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
HALLWAY_POS = [0, 1, 3, 5, 7, 9, 10]
ROOM_ENTRANCES = [2, 4, 6, 8]

def parse_input(lines):
    # Разбирает входные данные
    depth = len(lines) - 3
    raw_rooms = [[] for _ in range(4)]
    for i in range(depth):
        line = lines[2 + i]
        for j, pos in enumerate([3, 5, 7, 9]):
            obj = line[pos]
            if obj in 'ABCD':
                raw_rooms[j].append(obj)
    rooms = []
    for i in raw_rooms:
        rooms.append(tuple(reversed(i)))
    return tuple('.' for _ in range(11)), tuple(rooms), depth

def is_room_done(room, room_type, depth):
    # Проверяет готова ли конкретная комната
    if len(room) != depth:
        return False
    return all(x == room_type for x in room)

def can_enter_room(rooms, room_idx, obj, depth):
    # Можно ли войти в комнату, если есть место и нет других объектов
    room = rooms[room_idx]
    if any(x != obj for x in room):
        return False
    return len(room) < depth

def path_clear(hallway, start, end):
    # Проверяет свободен ли путь
    step = 1 if end > start else -1
    for i in range(start + step, end + step, step):
        if hallway[i] != '.':
            return False
    return True

def get_moves(hallway, rooms, depth):
    # Передвижение объектов
    moves = []

    # Из коридора в комнату
    for i, obj in enumerate(hallway):
        if obj == '.':
            continue
        room_idx = ROOM_IDX[obj]
        entrance = ROOM_ENTRANCES[room_idx]
        if not can_enter_room(rooms, room_idx, obj, depth):
            continue
        if not path_clear(hallway, i, entrance):
            continue
        steps = abs(i - entrance) + (depth - len(rooms[room_idx]))
        cost = steps * MOVE_COST[obj]
        new_hallway = list(hallway)
        new_hallway[i] = '.'
        new_rooms = list(list(r) for r in rooms)
        new_rooms[room_idx].append(obj)
        moves.append((cost, tuple(new_hallway), tuple(tuple(r) for r in new_rooms)))

    # Из комнаты в коридор
    for room_idx, room in enumerate(rooms):
        if not room:
            continue
        room_type = 'ABCD'[room_idx]
        if is_room_done(room, room_type, depth):
            continue
        obj = room[-1]
        entrance = ROOM_ENTRANCES[room_idx]
        for hall_pos in HALLWAY_POS:
            if not path_clear(hallway, entrance, hall_pos):
                continue
            steps = abs(hall_pos - entrance) + (depth - len(room) + 1)
            cost = steps * MOVE_COST[obj]
            new_hallway = list(hallway)
            new_hallway[hall_pos] = obj
            new_rooms = list(list(r) for r in rooms)
            new_rooms[room_idx] = new_rooms[room_idx][:-1]
            moves.append((cost, tuple(new_hallway), tuple(tuple(r) for r in new_rooms)))

    return moves

def is_final(rooms, depth):
    # Все ли объекты на своих местах
    for i in range(4):
        if not is_room_done(rooms[i], 'ABCD'[i], depth):
            return False
    return True

def solve(lines: list[str]) -> int:
    # Решение задачи о сортировке в лабиринте
    hallway, rooms, depth = parse_input(lines)
    heap = [(0, hallway, rooms)]
    visited = set()

    while heap:
        energy, hallway, rooms = heapq.heappop(heap)
        state = (hallway, rooms)
        if state in visited:
            continue
        visited.add(state)

        if is_final(rooms, depth):
            return energy

        for cost, new_hall, new_rooms in get_moves(hallway, rooms, depth):
            new_state = (new_hall, new_rooms)
            if new_state not in visited:
                heapq.heappush(heap, (energy + cost, new_hall, new_rooms))

    return 0

def main():
    # Чтение входных данных
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip('\n'))

    result = solve(lines)
    print(result)

if __name__ == "__main__":
    main()
