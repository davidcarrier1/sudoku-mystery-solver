
import random
import time

from sudoku import initialiser, fitness


def hill_climbing(puzzle):
    debut = time.perf_counter()

    iterations = 0
    meilleur_global = None
    meilleur_score_global = float("inf")

    while True:
        courant = initialiser(puzzle)
        score_courant = fitness(courant)

        while score_courant > 0:
            meilleur_voisin = None
            meilleur_score = score_courant

            for r in range(9):
                libres = [
                    c for c in range(9)
                    if puzzle[r][c] == 0
                ]

                for i in range(len(libres)):
                    for j in range(i + 1, len(libres)):
                        iterations += 1

                        voisin = [ligne[:] for ligne in courant]
                        c1, c2 = libres[i], libres[j]

                        voisin[r][c1], voisin[r][c2] = (
                            voisin[r][c2], voisin[r][c1]
                        )

                        score_voisin = fitness(voisin)

                        if score_voisin < meilleur_score:
                            meilleur_voisin = voisin
                            meilleur_score = score_voisin

            if meilleur_voisin is None:
                break

            courant = meilleur_voisin
            score_courant = meilleur_score

        if score_courant < meilleur_score_global:
            meilleur_global = [ligne[:] for ligne in courant]
            meilleur_score_global = score_courant

        if score_courant == 0:
            temps = time.perf_counter() - debut
            return courant, 0, iterations, temps
