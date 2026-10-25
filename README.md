# Laboratoire 2 : A* et Sudoku

Le labo est en deux parties : l'algorithme A* sur le 8-puzzle placé dans le fichier A*, puis la résolution de Sudoku avec une recherche locale (hill climbing) et un algorithme génétique.


## Partie 1 : A*

### Heuristiques utilisées

On a codé deux heuristiques, et on peut choisir laquelle utiliser à chaque exécution.

La première est la distance de Manhattan : pour chaque tuile, on compte combien de cases la sépare de sa position finale, et on additionne le tout.

La deuxième est le nombre de cases mal placées : on compte simplement les tuiles qui ne sont pas à leur place finale. La case vide n'est pas comptée non plus.

Ce sont les deux heuristiques que nous avons vues dans le cours pour solver le problème de 8-puzzle. Elles garantissent que A* trouve toujours une solution optimale. Manhattan est beaucoup plus informée que les cases mal placées, ce qui donne une vraie comparaison au niveau mémoire et temps pour le même résultat optimal, mais pas du tout le même effort pour y arriver.

### Comment ça marche dans notre code

La liste ouverte est une simple liste de tuples (f, g, état), où g est le nombre de déplacements déjà faits, h est l'estimation donnée par l'heuristique (f = g + h). À chaque itération, on prend l'élément avec le plus petit f (en cas d'égalité, le plus ancien). On garde aussi un dictionnaire du meilleur g connu pour chaque état. Avant de lancer la recherche, on vérifie si le puzzle est solvable, si le puzzle est impossible, l'algorithme s'arrête tout de suite.

### Ce qu'on enregistre

Pour chaque exécution, on écrit un fichier log. Chaque ligne correspond à une itération et contient :

- le numéro de l'itération
- g, h et f de l'état exploré
- ouverts : la taille de la liste ouverte
- l'état du puzzle

À la fin du fichier, on trouve le nombre total d'itérations, puis le temps d'exécution en secondes.

### Résultats

Pour l'exmple 1, les deux heuristiques trouvent une solution de 20 déplacements, donc la même longueur optimale. Avec les cases mal placées, on à considérablement plus d'itérations. En comparant les logs des deux heuristiques, il est flagrant que Manattan prend moins de temps et moins de mémoire. Voici un exemple de résultat : Manhattan | 283 | 0.0033 | 169 | Cases mal placées | 3667 | 0.3987 | 2090 |

Les logs complets sont dans le dossier logs.

## Partie 2 : Sudoku

### Comment on représente le problème

Une solution est une grille 9x9 complète. Pour la créer, on remplit chaque ligne avec les chiffres qui lui manquent, dans un ordre aléatoire, sans toucher aux chiffres de départ. Comme ça, chaque ligne est toujours valide, et tout le problème se résume à régler les colonnes et les sous-grilles 3x3.

La fonction objectif : pour chaque colonne et chaque bloc 3x3, on compte combien de chiffres de 1 à 9 manquent. Un score de 0 veut dire que le sudoku est résolu. Les deux algorithmes utilisent exactement la même fonction.

### Hill climbing

On échange deux cases libres dans une même ligne (Principe de voisin). Ça garde les lignes valides et ça respecte les chiffres donnés. À chaque étape, on évalue tous les échanges possibles, on garde le meilleur, et on s'en sert pour avancer. S'il y a plusieurs meilleurs voisins à égalité, on en choisit un au hasard. Pour que ce soit assez rapide, on ne recalcule pas toute la fonction objectif à chaque voisin, on regarde seulement les colonnes et les blocs touchés par l'échange (l'état avant vs après).

Comme vu en cours, le hill climbing de base reste coincé dans les minimums locaux et sur les plateaux, ce qui arrive tout le temps au sudoku. Ainsi, on autorise un nombre limité de mouvements latéraux, soit 50. On fait également un redémarrage aléatoire quand on est vraiment bloqué. Cette version évite qu'on s'arrête presque toujours sur une grille avec quelques conflits et ne résolve jamais rien. Une itération est le nombre de voisins évalués.

### Algorithme génétique

Fonction de fitness : le nombre de conflits dans les colonnes et les blocs 3x3. Plus c'est bas, mieux c'est, et 0 veut dire que le sudoku est résolu.

Population : 100 individus générés aléatoirement au départ.

Sélection des parents : On pige 3 individus au hasard dans la population et le meilleur des trois (la plus petite fitness) devient parent. On le fait deux fois pour avoir deux parents. Pour ne jamais perdre la meilleur solution trouvée, on garde 10% des meilleurs individus. Ils passent directement à la génération suivante.

Crossover : pour chaque ligne de l'enfant, on la prend au hasard du parent 1 ou du parent 2. On a choisi ce croisement par lignes parce qu'un croisement qui mélange des morceaux de lignes casserait la validité des lignes.

Mutation : pour chaque ligne de l'enfant (de base 10 % de prob), on échange deux cases libres de cette ligne (comme hill climbing). Le taux augment quand la population arrête de s'améliorer (max 50%).
Si la meilleure fitness ne s'améliore pas pendant 40 générations, on garde seulement la meilleure moitié de la population et on remplace l'autre moitié par de nouveaux individus aléatoires (Diversité).

On arrête quand on troucve un individu avec un fitness de 0. Une itération est une génération.

### Parallélisme

Au début, on a lancé nos algorithmes, avec un seul processus, et on s'est vite rendu compte que c'était extrêmement lent et surtout très dépendant de la chance. Les deux algorithmes partent de grilles aléatoires : une exécution peut tomber sur la solution rapidement, et la suivante, sur le même puzzle, peut tourner pendant des minutes sans y arriver.

Comme les exécutions sont indépendantes les unes des autres, on a décidé de lancer plusieurs copies de l'algorithme en même temps : 4 processus qui partent chacun de leur côté avec une graine aléatoire différente. Dès que l'un des processus trouve une solution, il prévient les autres et tout s'arrête. Ça ne rend pas l'algorithme plus intelligent, mais ça augmente beaucoup les chances qu'au moins un des processus ait de la chance rapidement. 

### Résultats

Chaque puzzle a été exécuté une fois par algorithme, avec les 4 processus en parallèle. Les résultats complets sont dans resultats.csv et les grilles dans les fichiers solution_*.txt. Les 20 exécutions ont fonctionnés et ont trouvés une solution valide ou il n'y avait plus de conflits.

| Puzzle | Cote | HC itérations | HC temps (s) | G générations | G temps (s) |
|---|---|---|---|---|---|
| 1 | Simple | 4 561 064 | 51.5 | 82 | 7.5 |
| 2 | Simple | 30 405 078 | 347.1 | 1 199 | 109.3 |
| 3 | Simple | 1 684 548 | 19.5 | 71 | 6.3 |
| 4 | Simple | 5 056 119 | 58.0 | 450 | 38.7 |
| 5 | Simple | 12 371 883 | 142.9 | 2 517 | 231.5 |
| 6 | Simple | 202 488 | 2.7 | 120 | 10.6 |
| 7 | Simple | 4 440 056 | 51.5 | 29 | 2.8 |
| 8 | Simple | 9 042 572 | 104.1 | 658 | 62.8 |
| 9 | Simple | 76 050 900 | 867.6 | 87 | 9.0 |
| 10 | Simple | 6 872 972 | 78.0 | 688 | 59.8 |

Résumé :

| | Hill climbing | Génétique |
|---|---|---|
| Puzzles résolus | 10 / 10 | 10 / 10 |
| Temps moyen | 172.3 s | 53.8 s |
| Temps médian | 68.0 s | 24.7 s |
| Temps min | 2.7 s | 2.8 s |
| Temps max | 867.6 s | 231.5 s |
| Temps total | 1 723 s | 538 s |
| Itérations moyennes | 15 068 768 voisins | 590 générations |

## Comparaison des algorithmes

Pour ce qui est du temps, on peut voir que l'algorithme génétique a été plus rapide 8 fois sur 10, avec un temps moyen de 24.7 s contre 68.0 s pour le hill climbing. On peut aussi dire que l'algorithme génétique à utilisé un temps total 3 fois plus petit que le hill climbing. 

Au niveau de la constance d'éxécution on voit que le hill climbing est beaucoup plus dépendant de la chance. En effet, son temps varie entre 2.7 s et 867.6 s, alors que le génétique reste entre 2.8 s et 231.5 s. On peut confirmer ce qu'on a observé au début, les deux algorithmes ont une part de hasard. Cependant, le hill climbing a un temps de résolution qui varie plus que le génétique d'une exécution à l'autre, et ce, parce qu'on a ajouté la recherche locale et un redémarrage complet au génétique.

Pour les nombres d'itérations, ils ne se comparent pas directement, puisqu'une itération du hill climbing est un voisin évalué et une itération du génétique est une génération complète (100 enfants, chacun avec de la recherche locale). 

Au niveau de la mémoire, le hill climbing garde une seule grille à la fois. Le génétique garde 100 grilles, donc il utilise plus de mémoire, mais les effets reste assez minime avec un sudoku.

Pour la facilité d'implémentation, le hill climbing est plus simple à écrire. Le génétique demande plus de pièces (sélection, croisement, mutation, redémarrage) et surtout beaucoup plus d'ajustements afin qu'il fonctionne sans attendre de nombreuses heures.

## Ce qu'on a appris

Avec A*, on a vu à quel point la qualité de l'heuristique change tout. On a la même solution optimale, mais 13 fois plus d'états explorés avec les cases mal placées qu'avec Manhattan, et également beaucoup plus de temps et de mémoire.

Pour le sudoku, on a appris que ces méthodes n'ont aucune garantie, contrairement à A*. Le hill climbing de base se bloque dans les minimums locaux, et il a fallu ajouter les mouvements latéraux et les redémarrages. L'algorithme génétique classique ne foncionnait pas avec une performance suffisante, il arrivait souvent à 2 conflits et restait coincé,sans parfois ce résoudre. On a donc dû rechercher une solution pour optimiser le tout, et cela, a été réaliser par l'ajout d'une recherche locale sur les enfants et d'un redémarrage complet. On aurait aussi pu utiliser un recuit simulé comme on l'a vu en cours, cepandant il était plus complexe à mettre place.

Finalement, le parallélisme n'améliore pas l'algorithme, mais il aide beaucoup quand le temps d'exécution dépend de la chance, avec 4 processus, il suffit qu'un seul soit chanceux. 