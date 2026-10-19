import random
import time

from sudoku import initialiser, fitness


def selection_tournoi(population, scores, taille_tournoi=3):
    """Tournoi : on réutilise les scores déjà calculés (pas de recalcul)."""
    indices = random.sample(range(len(population)),
                            min(taille_tournoi, len(population)))
    return population[min(indices, key=lambda i: scores[i])]


def croisement(parent1, parent2):
    """Chaque ligne vient d'un des deux parents (les lignes restent valides)."""
    return [(parent1 if random.random() < 0.5 else parent2)[r][:]
            for r in range(9)]


def mutation(enfant, puzzle, taux_mutation):
    """Échange deux cases libres d'une même ligne (garde les lignes valides)."""
    for r in range(9):
        if random.random() < taux_mutation:
            libres = [c for c in range(9) if puzzle[r][c] == 0]
            if len(libres) >= 2:
                c1, c2 = random.sample(libres, 2)
                enfant[r][c1], enfant[r][c2] = enfant[r][c2], enfant[r][c1]
    return enfant


def amelioration_locale(individu, puzzle, score, essais=15, t_accept=0.0):
    """
    Mutation 'dirigée' : on tente quelques échanges dans une ligne
    et on garde l'échange seulement s'il ne dégrade pas la fitness.
    """
    for _ in range(essais):
        r = random.randrange(9)
        libres = [c for c in range(9) if puzzle[r][c] == 0]
        if len(libres) < 2:
            continue
        c1, c2 = random.sample(libres, 2)
        ligne = individu[r]
        ligne[c1], ligne[c2] = ligne[c2], ligne[c1]
        nouveau = fitness(individu)
        if nouveau <= score or random.random() < t_accept:
            score = nouveau
            if score == 0:
                break
        else:
            ligne[c1], ligne[c2] = ligne[c2], ligne[c1]  # annule
    return score


def genetique(
    puzzle,
    population_size=100,
    taux_mutation=0.1,
    seuil_stagnation=40,
    taux_elites=0.1,
    max_generations=None,
    essais_locaux=15,
    t_accept=0.02,
    stop_event=None,
    nom_worker=None
):
    debut = time.perf_counter()

    if population_size < 2:
        raise ValueError("La population doit contenir au moins 2 individus.")

    nb_elites = max(2, int(population_size * taux_elites))
    population = [initialiser(puzzle) for _ in range(population_size)]
    scores = [fitness(ind) for ind in population]

    generations = 0
    meilleur_score_global = float("inf")
    meilleur_global = None
    sans_progres = 0

    while max_generations is None or generations < max_generations:
        if stop_event is not None and stop_event.is_set():
            break
        generations += 1

        i_best = min(range(population_size), key=lambda i: scores[i])
        meilleur_score = scores[i_best]

        if meilleur_score < meilleur_score_global:
            meilleur_score_global = meilleur_score
            meilleur_global = [l[:] for l in population[i_best]]
            sans_progres = 0
        else:
            sans_progres += 1

        if nom_worker is not None and generations % 100 == 0:
            print(f"[Genetique Worker {nom_worker}] Generation: {generations:,} "
                  f"| Meilleure fitness: {meilleur_score_global}", flush=True)

        if meilleur_score_global == 0:
            return (meilleur_global, 0, generations,
                    time.perf_counter() - debut)

        # Mutation adaptative : plus on stagne, plus on explore
        taux = min(0.6, taux_mutation * (1 + sans_progres / 10))

        # Élitisme
        ordre = sorted(range(population_size), key=lambda i: scores[i])
        nouvelle = [[l[:] for l in population[i]] for i in ordre[:nb_elites]]
        nouveaux_scores = [scores[i] for i in ordre[:nb_elites]]

        # Descendants
        while len(nouvelle) < population_size:
            p1 = selection_tournoi(population, scores)
            p2 = selection_tournoi(population, scores)
            enfant = mutation(croisement(p1, p2), puzzle, taux)
            s = fitness(enfant)
            s = amelioration_locale(enfant, puzzle, s, essais_locaux, t_accept)
            nouvelle.append(enfant)
            nouveaux_scores.append(s)

        # Stagnation : on garde les élites et on réinjecte du sang neuf
        if sans_progres >= seuil_stagnation:
            # Redémarrage quasi complet : on ne garde que 2 élites
            # (le meilleur global reste sauvegardé dans meilleur_global)
            nb_garde = 2
            nouvelle = nouvelle[:nb_garde]
            nouveaux_scores = nouveaux_scores[:nb_garde]
            while len(nouvelle) < population_size:
                ind = initialiser(puzzle)
                nouvelle.append(ind)
                nouveaux_scores.append(fitness(ind))
            sans_progres = 0

        population, scores = nouvelle, nouveaux_scores

    return meilleur_global, meilleur_score_global, generations, \
        time.perf_counter() - debut