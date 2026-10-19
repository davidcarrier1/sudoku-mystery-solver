
import multiprocessing as mp
import os
import random
import time

from sudoku import initialiser, fitness



def _worker(puzzle, worker_id, stop_event, result_queue):
    """Independent Hill Climbing search with progress reporting."""
    random.seed(time.time_ns() ^ os.getpid() ^ worker_id)

    iterations = 0
    meilleur_score_global = float("inf")
    prochain_affichage = 10_000

    while not stop_event.is_set():
        courant = initialiser(puzzle)
        score_courant = fitness(courant)

        if score_courant < meilleur_score_global:
            meilleur_score_global = score_courant

        while score_courant > 0 and not stop_event.is_set():
            meilleur_voisin = None
            meilleur_score = score_courant

            for r in range(9):
                libres = [
                    c for c in range(9)
                    if puzzle[r][c] == 0
                ]

                for i in range(len(libres)):
                    for j in range(i + 1, len(libres)):
                        if stop_event.is_set():
                            return

                        c1, c2 = libres[i], libres[j]

                        voisin = [ligne[:] for ligne in courant]
                        voisin[r][c1], voisin[r][c2] = (
                            voisin[r][c2],
                            voisin[r][c1]
                        )

                        iterations += 1
                        score_voisin = fitness(voisin)

                        if score_voisin < meilleur_score:
                            meilleur_voisin = voisin
                            meilleur_score = score_voisin

                        # Report every 10,000 evaluated neighbors
                        if iterations >= prochain_affichage:
                            print(
                                f"[Worker {worker_id}] "
                                f"Iterations: {iterations:,} | "
                                f"Current fitness: {score_courant} | "
                                f"Best fitness: {min(meilleur_score_global, meilleur_score)}",
                                flush=True
                            )
                            prochain_affichage += 10_000

            if meilleur_voisin is None:
                break

            courant = meilleur_voisin
            score_courant = meilleur_score

            if score_courant < meilleur_score_global:
                meilleur_score_global = score_courant

        if score_courant == 0:
            if not stop_event.is_set():
                result_queue.put(
                    (courant, iterations, worker_id)
                )
                stop_event.set()

                print(
                    f"[Worker {worker_id}] SOLUTION FOUND! "
                    f"Iterations: {iterations:,}",
                    flush=True
                )
            return



def hill_climbing_parallele(puzzle, nombre_processus=None):
    debut = time.perf_counter()

    if nombre_processus is None:
        nombre_processus = max(1, (os.cpu_count() or 2) - 1)

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

        # Wait until one worker finds a solution
        solution, iterations, worker_id = result_queue.get()

        return (
            solution,
            fitness(solution),
            iterations,
            time.perf_counter() - debut
        )

    finally:
        stop_event.set()

        for p in processus:
            if p.is_alive():
                p.terminate()

        for p in processus:
            p.join()

        result_queue.close()
        result_queue.join_thread()
