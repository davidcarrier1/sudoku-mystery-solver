import random
import time

from sudoku import initialiser, fitness, conflits


def _cout_local(grille, r, c1, c2):

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


def selection_tournoi(population, scores, taille_tournoi=3):
    indices = random.sample(range(len(population)),
                            min(taille_tournoi, len(population)))
    return population[min(indices, key=lambda i: scores[i])]


def croisement(parent1, parent2):
    return [(parent1 if random.random() < 0.5 else parent2)[r][:]
            for r in range(9)]


def mutation(enfant, rows_libres, taux):
    for r, libres in rows_libres:
        if random.random() < taux:
            c1, c2 = random.sample(libres, 2)
            enfant[r][c1], enfant[r][c2] = enfant[r][c2], enfant[r][c1]
    return enfant


def amelioration_locale(enfant, score, rows_libres, nb_pas):
    for _ in range(nb_pas):
        if score == 0:
            break

        r, libres = random.choice(rows_libres)
        ligne = enfant[r]

        meilleur_delta = None
        candidats = []
        for i in range(len(libres)):
            for j in range(i + 1, len(libres)):
                c1, c2 = libres[i], libres[j]
                avant = _cout_local(enfant, r, c1, c2)
                ligne[c1], ligne[c2] = ligne[c2], ligne[c1]
                apres = _cout_local(enfant, r, c1, c2)
                ligne[c1], ligne[c2] = ligne[c2], ligne[c1]

                delta = apres - avant
                if meilleur_delta is None or delta < meilleur_delta:
                    meilleur_delta = delta
                    candidats = [(c1, c2)]
                elif delta == meilleur_delta:
                    candidats.append((c1, c2))

        if meilleur_delta is not None and meilleur_delta <= 0:
            c1, c2 = random.choice(candidats)
            ligne[c1], ligne[c2] = ligne[c2], ligne[c1]
            score += meilleur_delta

    return score


def genetique(
    puzzle,
    population_size=100,
    taux_mutation=0.05,
    seuil_stagnation=40,
    taux_elites=0.1,
    pas_locaux=5,
    taux_mutation_max=0.2,
    max_generations=None,
    max_seconds=None,
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

    if not rows_libres:
        sol = initialiser(puzzle)
        return sol, fitness(sol), 0, time.perf_counter() - debut

    nb_elites = max(2, int(population_size * taux_elites))

    def nouvelle_population():
        pop = [initialiser(puzzle) for _ in range(population_size)]
        return pop, [fitness(ind) for ind in pop]

    population, scores = nouvelle_population()

    generations = 0
    redemarrages = 0
    meilleur_score_global = float("inf")
    meilleur_global = None
    meilleur_epoque = float("inf")
    sans_progres = 0

    while max_generations is None or generations < max_generations:
        if stop_event is not None and stop_event.is_set():
            break
        if max_seconds is not None and \
                time.perf_counter() - debut >= max_seconds:
            break
        generations += 1

        ordre = sorted(range(len(population)), key=lambda i: scores[i])
        i_best = ordre[0]

        if scores[i_best] < meilleur_epoque:
            meilleur_epoque = scores[i_best]
            sans_progres = 0
        else:
            sans_progres += 1

        if scores[i_best] < meilleur_score_global:
            meilleur_score_global = scores[i_best]
            meilleur_global = [l[:] for l in population[i_best]]

        if meilleur_score_global == 0:
            if fitness(meilleur_global) == 0:
                return (meilleur_global, 0, generations,
                        time.perf_counter() - debut)
            meilleur_score_global = fitness(meilleur_global)

        # Stagnation : redémarrage complet de la population
        if sans_progres >= seuil_stagnation:
            redemarrages += 1
            population, scores = nouvelle_population()
            meilleur_epoque = float("inf")
            sans_progres = 0
            continue

        taux = min(taux_mutation_max,
                   taux_mutation * (1 + sans_progres / 10))

        nouvelle = [[l[:] for l in population[i]] for i in ordre[:nb_elites]]
        nouveaux_scores = [scores[i] for i in ordre[:nb_elites]]

        while len(nouvelle) < population_size:
            p1 = selection_tournoi(population, scores)
            p2 = selection_tournoi(population, scores)
            enfant = mutation(croisement(p1, p2), rows_libres, taux)
            s = fitness(enfant)
            s = amelioration_locale(enfant, s, rows_libres, pas_locaux)
            nouvelle.append(enfant)
            nouveaux_scores.append(s)
            if s == 0:
                break

        population, scores = nouvelle, nouveaux_scores

    return (meilleur_global, meilleur_score_global, generations,
            time.perf_counter() - debut)