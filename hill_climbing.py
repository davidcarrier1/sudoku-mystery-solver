import random
import time

from sudoku import initialiser, fitness, conflits


def _cout_local(grille, r, c1, c2):
    """
    Conflits des seules unités touchées par un échange dans la ligne r :
    les colonnes c1 et c2 et les blocs 3x3 de (r, c1) et (r, c2).
    (La ligne reste toujours valide, elle n'est pas comptée.)
    """
    total = 0

    for c in (c1, c2):
        total += conflits([grille[i][c] for i in range(9)])

    r0 = (r // 3) * 3
    for b in {c1 // 3, c2 // 3}:
        c0 = b * 3
        total += conflits([
            grille[i][j]
            for i in range(r0, r0 + 3)
            for j in range(c0, c0 + 3)
        ])

    return total


def hill_climbing(
    puzzle,
    limite_plateau=50,
    max_iterations=None,
    stop_event=None,
    nom_worker=None
):
    """
    Hill climbing (steepest ascent) avec :
      - voisinage : échange de deux cases libres dans une même ligne
      - évaluation incrémentale (delta de fitness, pas de copie de grille)
      - mouvements latéraux (plateau) limités à `limite_plateau`
      - redémarrages aléatoires quand on est bloqué

    Retourne (solution, conflits, iterations, temps).
    `iterations` = nombre de voisins évalués.
    """
    debut = time.perf_counter()

    iterations = 0
    redemarrages = 0
    meilleur_global = None
    meilleur_score_global = float("inf")

    # Voisinage fixe (ne dépend que du puzzle)
    echanges = []
    for r in range(9):
        libres = [c for c in range(9) if puzzle[r][c] == 0]
        for i in range(len(libres)):
            for j in range(i + 1, len(libres)):
                echanges.append((r, libres[i], libres[j]))

    def arret():
        if stop_event is not None and stop_event.is_set():
            return True
        return max_iterations is not None and iterations >= max_iterations

    while not arret():
        courant = initialiser(puzzle)
        score = fitness(courant)
        plateau = 0

        while score > 0 and not arret():
            meilleur_delta = None
            candidats = []

            for r, c1, c2 in echanges:
                iterations += 1
                ligne = courant[r]

                avant = _cout_local(courant, r, c1, c2)
                ligne[c1], ligne[c2] = ligne[c2], ligne[c1]
                apres = _cout_local(courant, r, c1, c2)
                ligne[c1], ligne[c2] = ligne[c2], ligne[c1]

                delta = apres - avant

                if meilleur_delta is None or delta < meilleur_delta:
                    meilleur_delta = delta
                    candidats = [(r, c1, c2)]
                elif delta == meilleur_delta:
                    candidats.append((r, c1, c2))

            if meilleur_delta is None or meilleur_delta > 0:
                break  # minimum local

            if meilleur_delta == 0:
                plateau += 1
                if plateau > limite_plateau:
                    break  # trop de mouvements latéraux
            else:
                plateau = 0

            # Départage aléatoire entre les meilleurs voisins
            r, c1, c2 = random.choice(candidats)
            courant[r][c1], courant[r][c2] = courant[r][c2], courant[r][c1]
            score += meilleur_delta

        if score < meilleur_score_global:
            meilleur_score_global = score
            meilleur_global = [l[:] for l in courant]

        if score == 0:
            break

        redemarrages += 1
        if nom_worker is not None and redemarrages % 20 == 0:
            print(f"[HillClimbing Worker {nom_worker}] "
                  f"Redemarrages: {redemarrages:,} | "
                  f"Meilleur score: {meilleur_score_global}", flush=True)

    temps = time.perf_counter() - debut
    return meilleur_global, meilleur_score_global, iterations, temps