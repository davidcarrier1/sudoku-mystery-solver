
import multiprocessing as mp
import os
import random
import time

from sudoku import initialiser, fitness


def selection_tournoi(population, scores, taille_tournoi=3):
    indices = random.sample(
        range(len(population)),
        min(taille_tournoi, len(population))
    )
    meilleur = min(indices, key=lambda i: scores[i])
    return population[meilleur]


def croisement(parent1, parent2):
    """Combine les lignes des deux parents."""
    enfant = []

    for r in range(9):
        source = parent1 if random.random() < 0.5 else parent2
        enfant.append(source[r][:])

    return enfant


def mutation(enfant, puzzle, taux_mutation=0.3):
    """Échange deux cases libres d'une même ligne."""
    for r in range(9):
        if random.random() < taux_mutation:
            libres = [
                c for c in range(9)
                if puzzle[r][c] == 0
            ]

            if len(libres) >= 2:
                c1, c2 = random.sample(libres, 2)
                enfant[r][c1], enfant[r][c2] = (
                    enfant[r][c2],
                    enfant[r][c1]
                )

    return enfant


def _worker(
    puzzle,
    worker_id,
    stop_event,
    result_queue,
    population_size,
    seuil_stagnation
):
    random.seed(time.time_ns() ^ os.getpid() ^ worker_id)

    population = [
        initialiser(puzzle)
        for _ in range(population_size)
    ]

    generations = 0
    meilleur_score_global = float("inf")
    generations_sans_progres = 0
    taux_mutation = 0.3

    while not stop_event.is_set():
        scores = [fitness(ind) for ind in population]
        generations += 1

        meilleur_index = min(
            range(len(scores)),
            key=lambda i: scores[i]
        )
        meilleur = population[meilleur_index]
        meilleur_score = scores[meilleur_index]

        # Succès : fitness égale à zéro
        if meilleur_score == 0:
            if not stop_event.is_set():
                result_queue.put(
                    (meilleur, generations, worker_id)
                )
                stop_event.set()
            return

        # Détecter les progrès
        if meilleur_score < meilleur_score_global:
            meilleur_score_global = meilleur_score
            generations_sans_progres = 0
        else:
            generations_sans_progres += 1

        # Afficher la progression
        if generations % 100 == 0:
            print(
                f"[Genetique Worker {worker_id}] "
                f"Generation: {generations:,} | "
                f"Fitness actuelle: {meilleur_score} | "
                f"Meilleure fitness: {meilleur_score_global}",
                flush=True
            )

        # Conserver les 10 % meilleurs individus
        nombre_elites = max(2, population_size // 10)

        indices_tries = sorted(
            range(len(population)),
            key=lambda i: scores[i]
        )

        nouvelle_population = [
            [ligne[:] for ligne in population[i]]
            for i in indices_tries[:nombre_elites]
        ]

        # Créer les descendants
        while len(nouvelle_population) < population_size:
            parent1 = selection_tournoi(population, scores)
            parent2 = selection_tournoi(population, scores)

            enfant = croisement(parent1, parent2)
            enfant = mutation(enfant, puzzle, taux_mutation)

            nouvelle_population.append(enfant)

        # Remplacer les individus les moins performants
        # si la population stagne trop longtemps
        if generations_sans_progres >= seuil_stagnation:
            nombre_immigrants = max(1, population_size // 5)

            nouvelle_population = nouvelle_population[
                :population_size - nombre_immigrants
            ]

            while len(nouvelle_population) < population_size:
                nouvelle_population.append(initialiser(puzzle))

            generations_sans_progres = 0

            print(
                f"[Genetique Worker {worker_id}] "
                f"Diversification de la population "
                f"a la generation {generations:,}",
                flush=True
            )

        population = nouvelle_population


def genetique_parallele(
    puzzle,
    nombre_processus=None,
    population_size=100,
    seuil_stagnation=100
):
    debut = time.perf_counter()

    if nombre_processus is None:
        nombre_processus = max(1, (os.cpu_count() or 2) - 1)

    if nombre_processus < 1:
        raise ValueError("Il faut au moins un processus.")

    if population_size < 2:
        raise ValueError("La population doit contenir au moins 2 individus.")

    contexte = mp.get_context("spawn")
    stop_event = contexte.Event()
    result_queue = contexte.Queue()

    processus = [
        contexte.Process(
            target=_worker,
            args=(
                puzzle,
                i,
                stop_event,
                result_queue,
                population_size,
                seuil_stagnation
            )
        )
        for i in range(nombre_processus)
    ]

    try:
        for p in processus:
            p.start()

        solution, generations, worker_id = result_queue.get()

        temps = time.perf_counter() - debut

        print(
            f"\n[Genetique Worker {worker_id}] "
            f"SOLUTION TROUVEE en {generations:,} generations!",
            flush=True
        )

        return solution, fitness(solution), generations, temps

    finally:
        stop_event.set()

        for p in processus:
            if p.is_alive():
                p.terminate()

        for p in processus:
            p.join()

        result_queue.close()
        result_queue.join_thread()
