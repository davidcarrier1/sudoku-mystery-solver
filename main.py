
import csv
import random
import os

from sudoku import (
    lire_puzzles_csv,
    afficher_grille,
    sauvegarder_grille
)

from hill_climbing import hill_climbing
from hill_climbing_para import hill_climbing_parallele
from genetique import genetique
from genetique_para import genetique_parallele


def main():
    random.seed()

    puzzles = lire_puzzles_csv("puzzle.csv")

    if not puzzles:
        print("Aucun puzzle trouve dans puzzle.csv.")
        return

    resultats = []

    for puzzle in puzzles:
        numero = puzzle["numero"]
        grille = puzzle["grille"]
        rating = puzzle["rating"]

        print("\n" + "=" * 50)
        print(f"PUZZLE {numero} - Difficulté : {rating}")
        afficher_grille(grille)

        algorithmes = [
            (
                "Hill Climbing Parallel",
                lambda grille: hill_climbing_parallele(
                    grille,
                    nombre_processus=4
                )
            ),
            (
                "Genetique Parallel",
                lambda grille: genetique_parallele(
                    grille,
                    nombre_processus=4,
                    population_size=100
                )
            )
        ]

        for nom, algorithme in algorithmes:
            print(f"\nExecution : {nom}")

            solution, score, iterations, temps = algorithme(grille)

            reussi = score == 0

            print("Conflits :", score)
            print("Iterations :", iterations)
            print(f"Temps : {temps:.4f} secondes")
            print("Resolu :", "Oui" if reussi else "Non")

            # Sauvegarder la solution candidate
            nom_fichier = (
                f"solution_{numero}_"
                f"{nom.replace(' ', '_')}.txt"
            )

            sauvegarder_grille(nom_fichier, solution)

            resultats.append([
                numero,
                rating,
                nom,
                score,
                iterations,
                round(temps, 6),
                reussi
            ])

    # Enregistrer tous les résultats
    with open(
        "resultats.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as fichier:
        writer = csv.writer(fichier)

        writer.writerow([
            "Puzzle",
            "Difficulty",
            "Algorithme",
            "Conflits",
            "Iterations",
            "Temps_secondes",
            "Resolu"
        ])

        writer.writerows(resultats)

    print("\n" + "=" * 50)
    print("Tous les tests sont termines.")
    print("Resultats enregistres dans resultats.csv.")


if __name__ == "__main__":
    main()
