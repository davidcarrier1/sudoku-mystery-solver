import multiprocessing as mp
import os
import random
import time

from sudoku import fitness
from hill_climbing import hill_climbing


def _worker(puzzle, worker_id, stop_event, result_queue):
    random.seed(time.time_ns() ^ os.getpid() ^ worker_id)

    solution, score, iterations, _ = hill_climbing(
        puzzle,
        stop_event=stop_event,
        nom_worker=worker_id
    )

    # Seul un worker qui a réellement trouvé une solution publie
    if score == 0 and not stop_event.is_set():
        stop_event.set()
        result_queue.put((solution, iterations, worker_id))


def hill_climbing_parallele(puzzle, nombre_processus=None):
    debut = time.perf_counter()

    if nombre_processus is None:
        nombre_processus = max(1, (os.cpu_count() or 2) - 1)
    if nombre_processus < 1:
        raise ValueError("Il faut au moins un processus.")

    contexte = mp.get_context("spawn")
    stop_event = contexte.Event()
    result_queue = contexte.Queue()

    processus = [
        contexte.Process(
            target=_worker,
            args=(puzzle, i, stop_event, result_queue)
        )
        for i in range(nombre_processus)
    ]

    try:
        for p in processus:
            p.start()

        solution, iterations, worker_id = result_queue.get()
        temps = time.perf_counter() - debut

        print(f"\n[HillClimbing Worker {worker_id}] "
              f"SOLUTION TROUVEE en {iterations:,} iterations!", flush=True)

        return solution, fitness(solution), iterations, temps

    finally:
        stop_event.set()
        for p in processus:
            if p.is_alive():
                p.terminate()
        for p in processus:
            p.join()
        result_queue.close()
        result_queue.join_thread()