import time

from puzzle_state import is_solvable, write_log

def bfs(initial_state, goal_board, log_file=None):
    start_time = time.time()

    result = None
    nodes_explored = 0
    iteration_log = []

    if not is_solvable(initial_state.board):

        result = None

    else:

        queue = [initial_state]
        visited = {tuple(initial_state.board)}

        iteration = 0

        while queue:

            state = queue.pop(0)  # FIFO 
            nodes_explored += 1
            iteration += 1

            if state.board == goal_board:
                result = state
                iteration_log.append(f"{iteration}\t{len(queue)}")
                break

            for neighbor in state.get_neighbors():

                key = tuple(neighbor.board)

                if key not in visited:
                    visited.add(key)
                    queue.append(neighbor)

            # Taille de la frontière 
            iteration_log.append(f"{iteration}\t{len(queue)}")

    elapsed = time.time() - start_time

    write_log(
        log_file,
        iteration_log,
        nodes_explored,
        elapsed
    )

    return result