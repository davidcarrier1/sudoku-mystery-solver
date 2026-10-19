import csv
import random

CHIFFRES = set(range(1, 10))


def lire_puzzles_csv(fichier):
    puzzles = []

    with open(fichier, "r", encoding="utf-8-sig", newline="") as f:
        lecteur = csv.DictReader(f)

        for numero, ligne in enumerate(lecteur, start=1):
            texte = ligne["Puzzle"].strip()

            if len(texte) != 81:
                print(f"Puzzle {numero} ignore : longueur incorrecte.")
                continue

            grille = []

            for r in range(9):
                segment = texte[r * 9:(r + 1) * 9]
                grille.append([
                    0 if c == "." else int(c)
                    for c in segment
                ])

            puzzles.append({
                "numero": numero,
                "grille": grille,
                "rating": ligne.get("Difficulty", "Inconnu"),
                "givens": ligne.get("Givens", "")
            })

    return puzzles


def initialiser(grille):
    """Remplit les cases vides sans modifier les chiffres initiaux."""
    solution = []

    for ligne in grille:
        nouvelle_ligne = ligne[:]
        manquants = list(CHIFFRES - set(ligne))
        random.shuffle(manquants)

        index = 0
        for c in range(9):
            if nouvelle_ligne[c] == 0:
                nouvelle_ligne[c] = manquants[index]
                index += 1

        solution.append(nouvelle_ligne)

    return solution


def conflits(groupe):
    """Compte les chiffres manquants parmi les chiffres de 1 à 9."""
    return 9 - len(set(groupe))


def fitness(solution):
    """
    Fonction objectif à minimiser.
    Un score de 0 signifie que le Sudoku est résolu.
    """
    score = 0

    # Conflits dans les colonnes
    for c in range(9):
        colonne = [solution[r][c] for r in range(9)]
        score += conflits(colonne)

    # Conflits dans les sous-grilles 3x3
    for r0 in range(0, 9, 3):
        for c0 in range(0, 9, 3):
            bloc = []

            for r in range(r0, r0 + 3):
                for c in range(c0, c0 + 3):
                    bloc.append(solution[r][c])

            score += conflits(bloc)

    return score


def afficher_grille(grille):
    for r in range(9):
        if r in (3, 6):
            print("------+-------+------")

        for c in range(9):
            if c in (3, 6):
                print("|", end=" ")

            valeur = grille[r][c]
            print(valeur if valeur != 0 else ".", end=" ")

        print()


def sauvegarder_grille(fichier, grille):
    with open(fichier, "w", encoding="utf-8") as f:
        for ligne in grille:
            f.write("".join(str(n) for n in ligne) + "\n")
