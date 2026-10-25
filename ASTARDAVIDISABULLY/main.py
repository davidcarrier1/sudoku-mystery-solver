from pathlib import Path

from puzzle_state import (
    GOAL_STATE,
    read_initial_state,
    get_solution_path,
)
from largeur import bfs
from profondeur import dfs
from approfondissement import iddfs
from A import a_star_manhattan, a_star_misplaced


# État objectif du 8-puzzle
# [1, 2, 3, 4, 5, 6, 7, 8, 0]


def main():

    print("==============================")
    print("6GEI608 - Laboratoire 1")
    print("8-Puzzle")
    print("==============================")

    # Dossier contenant les fichiers d'entrée
    project_folder = Path(__file__).resolve().parent
    input_folder = project_folder / "input-Ex1"

    # Vérifier que le dossier existe
    if not input_folder.exists():

        print(
            f"\nErreur : le dossier {input_folder} "
            "n'existe pas."
        )

        return

    # Chercher les fichiers .txt
    files = sorted(
        input_folder.glob("*.txt")
    )

    if not files:

        print(
            "\nAucun fichier .txt trouvé "
            "dans le dossier input-Ex1."
        )

        return

    # Afficher les fichiers disponibles
    print("\nFichiers d'entrée disponibles :")

    for index, file in enumerate(files, start=1):

        print(
            f"{index} : {file.name}"
        )

    # Choisir un fichier
    try:

        file_choice = int(
            input(
                "\nChoisissez un fichier "
                "(numéro) : "
            )
        )

        if file_choice < 1 or file_choice > len(files):

            print("Numéro de fichier invalide.")
            return

    except ValueError:

        print("Veuillez entrer un numéro.")
        return

    selected_file = files[file_choice - 1]

    # Lire l'état initial
    try:

        initial_state = read_initial_state(
            selected_file
        )

    except Exception as e:

        print(
            f"\nErreur lors de la lecture du fichier : {e}"
        )

        return

    print(
        f"\nFichier sélectionné : "
        f"{selected_file.name}"
    )

    print("\nÉtat initial :")

    print(initial_state.board)

    print("\nÉtat objectif :")

    print(GOAL_STATE)

    # Menu
    print("\nChoix de l'algorithme :")
    print("1 : Recherche en largeur (BFS)")
    print("2 : Recherche en profondeur (DFS)")
    print("3 : Approfondissement itératif (IDDFS)")
    print("4 : A* (distance de Manhattan)")
    print("5 : A* (cases mal placées)")
    print("6 : Quitter")

    choice = input(
        "\nChoisissez une option : "
    )

    # BFS

    if choice == "1":

        run_algorithm(
            "largeur",
            bfs,
            initial_state,
            selected_file,
            project_folder
        )

    # DFS

    elif choice == "2":

        run_algorithm(
            "profondeur",
            dfs,
            initial_state,
            selected_file,
            project_folder
        )

    # IDDFS

    elif choice == "3":

        run_algorithm(
            "iddfs",
            iddfs,
            initial_state,
            selected_file,
            project_folder
        )

    # A* Manhattan

    elif choice == "4":

        run_algorithm(
            "astar_manhattan",
            a_star_manhattan,
            initial_state,
            selected_file,
            project_folder
        )

    # A* cases mal placées

    elif choice == "5":

        run_algorithm(
            "astar_misplaced",
            a_star_misplaced,
            initial_state,
            selected_file,
            project_folder
        )

    # Quitter

    elif choice == "6":

        print(
            "\nAu revoir !"
        )

    else:

        print(
            "\nOption invalide."
        )


def run_algorithm(prefix, algorithm, initial_state, selected_file, project_folder):

    print(
        f"\nExécution de la recherche en {prefix} "
        f"sur {selected_file.name}..."
    )

    # Dossier pour les fichiers de résultats
    logs_folder = project_folder / "logs"

    logs_folder.mkdir(
        exist_ok=True
    )

    solution = None

    # Faire les 10 exécutions demandées
    for run in range(1, 11):

        print(
            f"  Exécution {run}/10..."
        )

        log_file = (
            logs_folder
            / f"{prefix}_{selected_file.stem}_run_{run}.txt"
        )

        solution = algorithm(
            initial_state,
            GOAL_STATE,
            log_file
        )

    print(
        "\nLes 10 exécutions sont terminées."
    )

    # Afficher la solution
    if solution is not None:

        path = get_solution_path(
            solution
        )

        print(
            "\nSolution trouvée !"
        )

        print(
            f"Nombre de mouvements : "
            f"{len(path)}"
        )

        if path:

            print(
                "Chemin : "
                + " -> ".join(path)
            )

        else:

            print(
                "L'état initial est déjà "
                "l'état objectif."
            )

    else:

        print(
            "\nAucune solution trouvée."
        )


if __name__ == "__main__":
    main()
