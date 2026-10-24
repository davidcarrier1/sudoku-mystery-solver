import random
import time

from sudoku import initialiser, fitness


def selection_tournoi(population, scores, taille_tournoi=3):
    indices = random.sample(range(len(population)),
                            min(taille_tournoi, len(population)))
    return population[min(indices, key=lambda i: scores[i])]


def croisement(parent1, parent2):
    """Chaque ligne vient d'un des deux parents (lignes toujours valides)."""
    return [(parent1 if random.random() < 0.5 else parent2)[r][:]
            for r in range(9)]


def mutation(enfant, rows_libres, taux):
    """Échange deux cases libres d'une même ligne."""
    for r, libres in rows_libres:
        if random.random() < taux:
            c1, c2 = random.sample(libres, 2)
            enfant[r][c1], enfant[r][c2] = enfant[r][c2], enfant[r][c1]
    return enfant


def genetique(
    puzzle,
    population_size=100,
    taux_mutation=0.1,
    seuil_stagnation=40,
    taux_elites=0.1,
    max_generations=None,
    stop_event=None,
    nom_worker=None,
):
    debut = time.perf_counter()
    if population_size < 2:
        raise ValueError("La population doit contenir au moins 2 individus.")

    rows_libres = []
    for r in range(9):
        libres = [c for c in range(9) if puzzle[r][c] == 0]
        if len(libres) >= 2:
            rows_libres.append((r, libres))

    nb_elites = max(2, int(population_size * taux_elites))

    def nouvel_individu():
        ind = initialiser(puzzle)
        return ind, fitness(ind)

    population, scores = [], []
    for _ in range(population_size):
        ind, s = nouvel_individu()
        population.append(ind)
        scores.append(s)

    generations = 0
    meilleur_score_global = float("inf")
    meilleur_global = None
    sans_progres = 0

    while max_generations is None or generations < max_generations:
        if stop_event is not None and stop_event.is_set():
            break
        generations += 1

        ordre = sorted(range(population_size), key=lambda i: scores[i])
        i_best = ordre[0]

        if scores[i_best] < meilleur_score_global:
            meilleur_score_global = scores[i_best]
            meilleur_global = [l[:] for l in population[i_best]]
            sans_progres = 0
        else:
            sans_progres += 1

        if nom_worker is not None and generations % 50 == 0:
            print(f"[Genetique Worker {nom_worker}] Generation: "
                  f"{generations:,} | Meilleure fitness: "
                  f"{meilleur_score_global}", flush=True)

        if meilleur_score_global == 0:
            return (meilleur_global, 0, generations,
                    time.perf_counter() - debut)

        taux = min(0.5, taux_mutation * (1 + sans_progres / 10))

        nouvelle = [[l[:] for l in population[i]] for i in ordre[:nb_elites]]
        nouveaux_scores = [scores[i] for i in ordre[:nb_elites]]

        while len(nouvelle) < population_size:
            p1 = selection_tournoi(population, scores)
            p2 = selection_tournoi(population, scores)
            enfant = mutation(croisement(p1, p2), rows_libres, taux)
            s = fitness(enfant)
            nouvelle.append(enfant)
            nouveaux_scores.append(s)
            if s == 0:
                break

        # Stagnation : on remplace seulement la moitié la plus faible
        if sans_progres >= seuil_stagnation and 0 not in nouveaux_scores:
            ordre2 = sorted(range(len(nouvelle)),
                            key=lambda i: nouveaux_scores[i])
            garde = ordre2[:len(nouvelle) // 2]
            nouvelle = [nouvelle[i] for i in garde]
            nouveaux_scores = [nouveaux_scores[i] for i in garde]
            while len(nouvelle) < population_size:
                ind, s = nouvel_individu()
                nouvelle.append(ind)
                nouveaux_scores.append(s)
            sans_progres = 0

        population, scores = nouvelle, nouveaux_scores
        population_size = len(population)

    return (meilleur_global, meilleur_score_global, generations,
            time.perf_counter() - debut)