import time

from puzzle_state import is_solvable, write_log


def heuristic(board):#Distance de Manhattan
    distance = 0
    for i in range(9):
        if board[i] != 0:
            x1, y1 = divmod(i, 3)
            x2, y2 = divmod(board[i] - 1, 3)
            distance += abs(x1 - x2) + abs(y1 - y2)
    return distance


def heuristic2(board):#Nombre de cases mal placées
    distance = 0
    for i in range(9):
        if board[i] != 0 and board[i] != i + 1:
            distance += 1
    return distance


def a_star(initial_state, goal_state, log_file=None, h=heuristic):
    start_time = time.time()
    iteration_log = []
    nodes_explored = 0

    # Puzzle impossible à résoudre
    if not is_solvable(initial_state.board):
        write_log(log_file, iteration_log, nodes_explored, time.time() - start_time)
        return None

    # Liste ouverte : simple liste d'éléments (f, g, état)
    open_list = [(h(initial_state.board), 0, initial_state)]
    best_g = {tuple(initial_state.board): 0}

    solution = None

    while open_list:
        # Trouver l'élément avec le plus petit f
        # (en cas d'égalité, le plus ancien est choisi)
        best_index = 0
        for i in range(1, len(open_list)):
            if open_list[i][0] < open_list[best_index][0]:
                best_index = i

        f, g, current = open_list.pop(best_index)
        key = tuple(current.board)

        # Entrée périmée : un meilleur chemin vers cet état a déjà été trouvé
        if g > best_g.get(key, float("inf")):
            continue

        nodes_explored += 1
        iteration_log.append(
            f"Itération {nodes_explored} : g={g} h={f - g} f={f} "
            f"ouverts={len(open_list)} "
            f"état={current.board}"
        )

        if current.board == goal_state:
            solution = current
            break

        for neighbor in current.get_neighbors():
            new_g = g + 1
            nkey = tuple(neighbor.board)

            if new_g < best_g.get(nkey, float("inf")):
                best_g[nkey] = new_g
                new_f = new_g + h(neighbor.board)
                open_list.append((new_f, new_g, neighbor))

    write_log(log_file, iteration_log, nodes_explored, time.time() - start_time)
    return solution


def a_star_manhattan(initial_state, goal_state, log_file=None):
    return a_star(initial_state, goal_state, log_file, h=heuristic)


def a_star_misplaced(initial_state, goal_state, log_file=None):
    return a_star(initial_state, goal_state, log_file, h=heuristic2)