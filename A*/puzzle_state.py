# État objectif du 8-puzzle
GOAL_STATE = [1, 2, 3, 4, 5, 6, 7, 8, 0]


# Noms des mouvements possibles et leur déplacement
MOVES = {
    "Haut": -3,
    "Bas": 3,
    "Gauche": -1,
    "Droite": 1,
}


# Classe représentant un état du puzzle
class PuzzleState:

    def __init__(self, board, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move

    def __eq__(self, other):
        return isinstance(other, PuzzleState) and self.board == other.board

    def __hash__(self):
        return hash(tuple(self.board))

    def __repr__(self):
        return "\n".join(
            " ".join(map(str, self.board[i:i + 3]))
            for i in range(0, 9, 3)
        )

    def find_zero(self):
        return self.board.index(0)

    def get_neighbors(self):
       

        neighbors = []

        zero = self.find_zero()
        row, col = divmod(zero, 3)

        for name, delta in MOVES.items():

            new_zero = zero + delta

            # Vérifier que la nouvelle position est dans le tableau
            if not (0 <= new_zero < 9):
                continue

            new_row, new_col = divmod(new_zero, 3)

            # Vérifier que le déplacement est réellement adjacent
            # (empêche par exemple de passer de la colonne 0 à 2)
            if abs(row - new_row) + abs(col - new_col) != 1:
                continue

            new_board = self.board[:]
            new_board[zero], new_board[new_zero] = \
                new_board[new_zero], new_board[zero]

            neighbors.append(
                PuzzleState(new_board, parent=self, move=name)
            )

        return neighbors

def read_initial_state(file_path):
    #Lit un fichier .txt et retourne un PuzzleState correspondant à l'état initial décrit dans ce fichier.

    content = file_path.read_text(encoding="utf-8")

    board = []

    for line in content.splitlines():

        if not line.strip():
            continue

        values = line.split("\t")

        row = []

        for value in values:
            value = value.strip()
            row.append(0 if value == "" else int(value))

        # Ajouter des 0 si la dernière case est absente
        while len(row) < 3:
            row.append(0)

        board.extend(row)

    if len(board) != 9:
        raise ValueError(
            f"Le fichier {file_path.name} contient {len(board)} "
            "valeurs au lieu de 9."
        )

    return PuzzleState(board)


# Vérifier si un puzzle est solvable par inversions https://www.cs.princeton.edu/courses/archive/spr18/cos226/assignments/8puzzle/index.html
def is_solvable(board):
    tiles = [x for x in board if x != 0]

    inversions = sum(
        1
        for i in range(len(tiles))
        for j in range(i + 1, len(tiles))
        if tiles[i] > tiles[j]
    )

    return inversions % 2 == 0

def get_solution_path(state):
 
    moves = []

    while state is not None and state.parent is not None:
        moves.append(state.move)
        state = state.parent

    moves.reverse()

    return moves

def write_log(log_file, iteration_log, nodes_explored, elapsed):

    if log_file is None:
        return

    with open(log_file, "w", encoding="utf-8") as f:

        for line in iteration_log:
            f.write(f"{line}\n")

        f.write(f"{nodes_explored}\n")
        f.write(f"{elapsed:.6f}\n")

def print_solution(state):
  
    path_states = []

    while state is not None:
        path_states.append(state)
        state = state.parent

    path_states.reverse()

    for s in path_states:
        print(s)
        print("-----")
