
import random
import time

from sudoku import initialiser, fitness


def selection_tournoi(population, taille_tournoi=3):
    candidats = random.sample(
        population,
        min(taille_tournoi, len(population))
    )

    return min(candidats, key=fitness)


def croisement(parent1, parent2):
    """
    Chaque ligne provient de l'un des parents.
    Les chiffres initiaux restent fixes.
    """
    enfant = []

    for r in range(9):
        source = parent1 if random.random() < 0.5 else parent2
        enfant.append(source[r][:])

    return enfant


def mutation(enfant, puzzle, taux_mutation=0.3):
    """
    Échange deux cases libres d'une même ligne.
    Préserve les chiffres initiaux et les lignes valides.
    """
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


def genetique(
    puzzle,
    population_size=100,
    taux_mutation=0.3,
    seuil_stagnation=100
):
    debut = time.perf_counter()

    if population_size < 2:
        raise ValueError("La population doit contenir au moins 2 individus.")

    # Générer la population initiale
    population = [
        initialiser(puzzle)
        for _ in range(population_size)
    ]

    generations = 0
    meilleur_score_global = float("inf")
    meilleur_global = None
    generations_sans_progres = 0

    while True:
        scores = [fitness(individu) for individu in population]
        generations += 1

        # Identifier le meilleur individu de la génération
        meilleur_index = scores.index(min(scores))
        meilleur = population[meilleur_index]
        meilleur_score = scores[meilleur_index]

        # Arrêter uniquement lorsqu'une solution est trouvée
        if meilleur_score == 0:
            temps = time.perf_counter() - debut

            return (
                [ligne[:] for ligne in meilleur],
                0,
                generations,
                temps
            )

        # Suivre les progrès
        if meilleur_score < meilleur_score_global:
            meilleur_score_global = meilleur_score
            meilleur_global = [
                ligne[:] for ligne in meilleur
            ]
            generations_sans_progres = 0
        else:
            generations_sans_progres += 1

        # Conserver les deux meilleurs individus
        indices_tries = sorted(
            range(len(population)),
            key=lambda i: scores[i]
        )

        nouvelle_population = [
            [ligne[:] for ligne in population[i]]
            for i in indices_tries[:2]
        ]

        # Créer les descendants
        while len(nouvelle_population) < population_size:
            parent1 = selection_tournoi(population)
            parent2 = selection_tournoi(population)

            enfant = croisement(parent1, parent2)
            enfant = mutation(
                enfant,
                puzzle,
                taux_mutation
            )

            nouvelle_population.append(enfant)

        # Diversifier la population après une stagnation
        if generations_sans_progres >= seuil_stagnation:
            # Garder le meilleur individu connu
            nouvelle_population = [
                [ligne[:] for ligne in meilleur_global]
            ]

            # Introduire de nouveaux individus aléatoires
            nombre_immigrants = max(
                1, population_size // 5
            )

            while len(nouvelle_population) < population_size:
                nouvelle_population.append(initialiser(puzzle))

            generations_sans_progres = 0

            print(
                f"Génération {generations}: stagnation détectée. "
                f"Nouvelle population diversifiée."
            )

        population = nouvelle_population
