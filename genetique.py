import math
import random
import time

from sudoku import initialiser, fitness

_EXP_CACHE = {}


def selection_tournoi(population, scores, taille_tournoi=3):
    indices = random.sample(range(len(population)),
                            min(taille_tournoi, len(population)))
    return population[min(indices, key=lambda i: scores[i])]


def croisement(parent1, parent2):
    """Chaque ligne vient d'un des deux parents (lignes toujours valides)."""
    return [(parent1 if random.random() < 0.5 else parent2)[r][:]
            for r in range(9)]


def _compteurs(g):
    cc = [[0] * 10 for _ in range(9)]
    bc = [[0] * 10 for _ in range(9)]
    for r in range(9):
        for c in range(9):
            v = g[r][c]
            cc[c][v] += 1
            bc[(r // 3) * 3 + c // 3][v] += 1
    return cc, bc


def recuit(ind, rows_libres, score, essais, T):
    """
    Recuit simulé à température constante, avec calcul incrémental du delta.
    Mouvement : échange de deux cases libres dans une ligne.
    Modifie `ind` en place et retourne le nouveau score.
    """
    if not rows_libres or score == 0:
        return score
    cc, bc = _compteurs(ind)
    exp_t = _EXP_CACHE.get(T)
    if exp_t is None:
        exp_t = _EXP_CACHE[T] = [math.exp(-d / T) for d in range(0, 17)]
    rnd = random.random
    for _ in range(essais):
        r, libres = random.choice(rows_libres)
        c1 = random.choice(libres)
        c2 = random.choice(libres)
        if c1 == c2:
            continue
        row = ind[r]
        a, b = row[c1], row[c2]
        k1 = (r // 3) * 3 + c1 // 3
        k2 = (r // 3) * 3 + c2 // 3
        d = ((cc[c1][a] == 1) - (cc[c1][b] == 0)
             + (cc[c2][b] == 1) - (cc[c2][a] == 0))
        if k1 != k2:
            d += ((bc[k1][a] == 1) - (bc[k1][b] == 0)
                  + (bc[k2][b] == 1) - (bc[k2][a] == 0))
        if d <= 0 or rnd() < exp_t[d]:
            row[c1], row[c2] = b, a
            cc[c1][a] -= 1; cc[c1][b] += 1
            cc[c2][b] -= 1; cc[c2][a] += 1
            if k1 != k2:
                bc[k1][a] -= 1; bc[k1][b] += 1
                bc[k2][b] -= 1; bc[k2][a] += 1
            score += d
            if score == 0:
                break
    return score


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
    essais_locaux=300,
    t_accept=None,          # conservé pour compatibilité (inutilisé)
    stop_event=None,
    nom_worker=None,
    temperature=0.4,
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
        s = recuit(ind, rows_libres, fitness(ind), essais_locaux,
                   temperature)
        return ind, s

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

        if nom_worker is not None and generations % 20 == 0:
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
            s = recuit(enfant, rows_libres, fitness(enfant),
                       essais_locaux, temperature)
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