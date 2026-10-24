import time

from puzzle_state import is_solvable, write_log

def _depth_limited_search(initial_state, goal_board, limit, state, iteration_log):
    stack = [initial_state]
    depth_map = {tuple(initial_state.board): 0}

    while stack:

        node = stack.pop()

        state["nodes_explored"] += 1
        state["iteration"] += 1

        if node.board == goal_board:
            iteration_log.append(
                f"{state['iteration']}\t{len(stack)}"
            )
            return node

        depth = depth_map[tuple(node.board)]

        if depth < limit:

            for neighbor in node.get_neighbors():

                key = tuple(neighbor.board)

                if key not in depth_map or depth_map[key] > depth + 1:
                    depth_map[key] = depth + 1
                    stack.append(neighbor)

        # Taille de la frontière
        iteration_log.append(
            f"{state['iteration']}\t{len(stack)}"
        )

    return None

#IDDFS (Iterative Deepening Depth-First Search) 
def iddfs(initial_state, goal_board, log_file=None, max_limit=31): #limite de 31 car on sait que c'est le max https://www.cs.princeton.edu/courses/archive/spring20/cos226/assignments/8puzzle/checklist.php
    start_time = time.time()

    result = None
    iteration_log = []
    state = {"nodes_explored": 0, "iteration": 0}

    if not is_solvable(initial_state.board):

        result = None

    else:

        limit = 0

        while limit <= max_limit:

            result = _depth_limited_search(
                initial_state,
                goal_board,
                limit,
                state,
                iteration_log
            )

            if result is not None:
                break

            limit += 1

    elapsed = time.time() - start_time

    write_log(
        log_file,
        iteration_log,
        state["nodes_explored"],
        elapsed
    )

    return result
