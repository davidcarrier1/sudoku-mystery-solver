import multiprocessing as mp
import os
import random
import time

from genetique import genetique


def _worker(puzzle, worker_id, stop_event, result_queue,
            population_size, seuil_stagnation, max_seconds):
    random.seed(time.time_ns() ^ os.getpid() ^ worker_id)

    solution, score, generations, temps = genetique(
        puzzle,
        population_size=population_size,
        seuil_stagnation=seuil_stagnation,
        max_seconds=max_seconds,
        stop_event=stop_event,
        nom_worker=worker_id,
    )

    if score == 0:
        stop_event.set()

    result_queue.put((solution, score, generations, temps, worker_id))


def genetique_parallele(puzzle, nombre_processus=None,
                        population_size=50, seuil_stagnation=40,
                        max_seconds=120.0):
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
                  population_size, seuil_stagnation, max_seconds),
        )
        for i in range(nombre_processus)
    ]

    try:
        for p in processus:
            p.start()

        resultats = [result_queue.get() for _ in range(nombre_processus)]
        best = min(resultats, key=lambda t: t[1])
        solution, score, generations, _, worker_id = best
        temps = time.perf_counter() - debut

        if score == 0:
            print(f"\n[Genetique W{worker_id}] SOLUTION TROUVEE en "
                  f"{generations:,} generations!", flush=True)
        else:
            print(f"\n[Genetique] Meilleur score: {score} "
                  f"(worker {worker_id}, {generations:,} gen)", flush=True)

        return solution, score, generations, temps

    finally:
        stop_event.set()
        for p in processus:
            if p.is_alive():
                p.terminate()
        for p in processus:
            p.join()
        result_queue.close()
        result_queue.join_thread()