"""
=============================================================
  FICHIER : balas_hammer.py
  RÔLE    : Algorithme de Balas-Hammer (méthode des pénalités)
  SECTION : 2.1 (fonction 4 du projet)
=============================================================

PRINCIPE DE L'ALGORITHME :
    Contrairement à Nord-Ouest, Balas-Hammer tient compte des coûts
    pour construire une proposition initiale de meilleure qualité.

    À chaque itération :
      1. Pour chaque ligne active  → pénalité = 2ème min - 1er min des coûts
         Pour chaque colonne active → pénalité = 2ème min - 1er min des coûts
      2. On choisit la ligne/colonne avec la PLUS GRANDE pénalité
         (c'est celle où le "regret" de ne pas choisir le min est maximal)
      3. On alloue le maximum possible sur la case de coût minimal
         de cette ligne/colonne
      4. On barre la ligne ou la colonne épuisée et on recommence

COMPLEXITÉ : O(n × m × (n + m)) dans le pire des cas.

AVANTAGE vs Nord-Ouest : La proposition initiale est généralement
beaucoup plus proche de l'optimum → moins d'itérations du marche-pied.
"""


def calculer_penalites(n, m, cout, lignes_actives, cols_actives):
    """
    Calcule la pénalité de Balas-Hammer pour chaque ligne et colonne encore active.

    La pénalité d'une ligne i = (2ème plus petit coût) - (plus petit coût)
    parmi les colonnes encore actives de cette ligne.
    Idem pour les colonnes.

    Paramètres :
        n, m           : dimensions du tableau
        cout           : matrice des coûts
        lignes_actives : liste de booléens, True si la ligne i est encore active
        cols_actives   : liste de booléens, True si la colonne j est encore active

    Retourne :
        liste de tuples (pénalité, type, index, index_min_cout)
            type = 'L' pour ligne, 'C' pour colonne
            index = numéro de la ligne ou colonne
            index_min_cout = index de la colonne/ligne où le coût est minimal
    """
    penalites = []

    # ── Pénalités des LIGNES ──────────────────────────────────────────────────
    for i in range(n):
        if not lignes_actives[i]:
            continue  # ligne déjà épuisée → on l'ignore

        # On collecte les coûts disponibles sur cette ligne
        # (seulement les colonnes encore actives)
        couts_dispo = sorted(
            (cout[i][j], j)          # (valeur du coût, indice de colonne)
            for j in range(m)
            if cols_actives[j]
        )

        if len(couts_dispo) >= 2:
            # Pénalité = écart entre le 2ème et le 1er minimum
            penalite = couts_dispo[1][0] - couts_dispo[0][0]
        elif len(couts_dispo) == 1:
            # Un seul coût disponible → pénalité = ce coût lui-même
            penalite = couts_dispo[0][0]
        else:
            continue  # aucune colonne active → on passe

        # On mémorise l'indice j du coût minimal (pour l'allocation)
        j_min = couts_dispo[0][1]
        penalites.append((penalite, 'L', i, j_min))

    # ── Pénalités des COLONNES ────────────────────────────────────────────────
    for j in range(m):
        if not cols_actives[j]:
            continue  # colonne déjà satisfaite → on l'ignore

        couts_dispo = sorted(
            (cout[i][j], i)          # (valeur du coût, indice de ligne)
            for i in range(n)
            if lignes_actives[i]
        )

        if len(couts_dispo) >= 2:
            penalite = couts_dispo[1][0] - couts_dispo[0][0]
        elif len(couts_dispo) == 1:
            penalite = couts_dispo[0][0]
        else:
            continue

        i_min = couts_dispo[0][1]
        penalites.append((penalite, 'C', j, i_min))

    return penalites


def balas_hammer(n, m, cout, provisions, commandes, verbose=True):
    """
    Construit une proposition initiale par la méthode de Balas-Hammer.

    Paramètres :
        n, m       : dimensions
        cout       : matrice des coûts
        provisions : copies des provisions
        commandes  : copies des commandes
        verbose    : afficher le détail

    Retourne :
        transport (list[list]) : matrice des quantités transportées
        base      (set)        : arêtes actives (tuples (i,j))
    """

    if verbose:
        print("\n╔══ ALGORITHME BALAS-HAMMER ══╗")

    # ── Initialisation ────────────────────────────────────────────────────────
    transport = [[0] * m for _ in range(n)]
    base = set()

    prov = provisions[:]
    cmd  = commandes[:]

    # Indicateurs : True = encore actif, False = épuisé/satisfait
    lignes_actives = [True] * n
    cols_actives   = [True] * m

    iteration = 0

    # ── Boucle principale ─────────────────────────────────────────────────────
    while any(lignes_actives) and any(cols_actives):
        iteration += 1

        # ── Étape A : Calculer toutes les pénalités ───────────────────────────
        penalites = calculer_penalites(n, m, cout, lignes_actives, cols_actives)
        if not penalites:
            break  # sécurité : plus rien à faire

        # ── Étape B : Trouver la pénalité maximale ────────────────────────────
        pen_max = max(p[0] for p in penalites)
        meilleures = [p for p in penalites if p[0] == pen_max]

        if verbose:
            print(f"\n  ── Itération {iteration} ──")
            print(f"  Pénalité maximale : {pen_max}")
            for pen, typ, idx, _ in meilleures:
                nom = f"Ligne   P{idx+1}" if typ == 'L' else f"Colonne C{idx+1}"
                print(f"    → {nom} (pénalité = {pen})")

        # ── Étape C : Choisir la première meilleure pénalité ─────────────────
        # En cas d'égalité, on prend la première dans la liste
        _, typ, idx, best_idx = meilleures[0]

        # Déduire (i, j) selon si c'est une ligne ou une colonne
        if typ == 'L':
            i, j = idx, best_idx      # ligne idx, colonne du coût min
        else:
            i, j = best_idx, idx      # ligne du coût min, colonne idx

        # ── Étape D : Allouer le maximum possible ─────────────────────────────
        q = min(prov[i], cmd[j])
        transport[i][j] = q
        base.add((i, j))

        if verbose:
            print(f"  Choix : b[P{i+1}, C{j+1}] = min("
                  f"provision={prov[i]}, commande={cmd[j]}) = {q}")
            print(f"  (case de coût minimal = {cout[i][j]})")

        # Déduire les quantités allouées
        prov[i] -= q
        cmd[j]  -= q

        # ── Étape E : Barrer la ligne et/ou la colonne épuisée ────────────────
        if prov[i] == 0:
            lignes_actives[i] = False
            if verbose:
                print(f"  → Ligne P{i+1} épuisée, on la barre.")

        if cmd[j] == 0:
            cols_actives[j] = False
            if verbose:
                print(f"  → Colonne C{j+1} satisfaite, on la barre.")

    if verbose:
        print(f"\n  → Base obtenue : {len(base)} arêtes "
              f"(requis pour arbre : n+m-1 = {n+m-1})")
        print()

    return transport, base