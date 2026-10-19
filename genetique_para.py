import multiprocessing as mp
import os
import random
import time

from sudoku import fitness
from genetique import genetique


def _worker(puzzle, worker_id, stop_event, result_queue,
            population_size, seuil_stagnation):
    random.seed(time.time_ns() ^ os.getpid() ^ worker_id)

    solution, score, generations, _ = genetique(
        puzzle,
        population_size=population_size,
        seuil_stagnation=seuil_stagnation,
        stop_event=stop_event,
        nom_worker=worker_id
    )

    # Seul un worker qui a réellement trouvé une solution publie
    if score == 0 and not stop_event.is_set():
        stop_event.set()
        result_queue.put((solution, generations, worker_id))


def genetique_parallele(puzzle, nombre_processus=None,
                        population_size=100, seuil_stagnation=40):
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
            args=(puzzle, i, stop_event, result_queue,
                  population_size, seuil_stagnation)
        )
        for i in range(nombre_processus)
    ]

    try:
        for p in processus:
            p.start()

        solution, generations, worker_id = result_queue.get()
        temps = time.perf_counter() - debut

        print(f"\n[Genetique Worker {worker_id}] "
              f"SOLUTION TROUVEE en {generations:,} generations!", flush=True)

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