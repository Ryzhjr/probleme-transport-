"""
=============================================================
  FICHIER : nord_ouest.py
  RÔLE    : Algorithme du coin Nord-Ouest
  SECTION : 2.1 (fonction 3 du projet)
=============================================================

PRINCIPE DE L'ALGORITHME :
    On part de la case en haut à gauche (Nord-Ouest) du tableau.
    À chaque étape, on alloue le maximum possible à la case courante,
    c'est-à-dire min(provision disponible, commande restante).
    
    - Si la provision du fournisseur i est épuisée → on descend (i+1)
    - Si la commande du client j est satisfaite   → on avance (j+1)
    - Si les deux sont épuisés simultanément      → cas dégénéré,
      on crée une arête fictive à 0 et on avance

COMPLEXITÉ : O(n + m) — on parcourt chaque ligne et colonne une seule fois.

REMARQUE : Cet algorithme ignore totalement les coûts → la proposition
initiale obtenue est souvent loin de l'optimum, mais elle est rapide
à calculer et toujours réalisable.
"""


def nord_ouest(n, m, provisions, commandes, verbose=True):
    """
    Construit une proposition initiale de transport par la méthode
    du coin Nord-Ouest.

    Paramètres :
        n          (int)  : nombre de fournisseurs
        m          (int)  : nombre de clients
        provisions (list) : copie des provisions [P1..Pn]  ← on va les modifier
        commandes  (list) : copie des commandes  [C1..Cm]  ← on va les modifier
        verbose    (bool) : afficher le détail des allocations

    Retourne :
        transport  (list[list]) : matrice n×m des quantités transportées
        base       (set)        : ensemble des tuples (i,j) alloués
                                  (= les arêtes de l'arbre de transport)
    """

    if verbose:
        print("\n╔══ ALGORITHME NORD-OUEST ══╗")

    # ── Initialisation ────────────────────────────────────────────────────────
    # Matrice de transport : toutes les cases à 0 au départ
    transport = [[0] * m for _ in range(n)]

    # La BASE contient les cases allouées (arêtes de l'arbre couvrant)
    # Un arbre couvrant d'un graphe biparti n×m a exactement n+m-1 arêtes
    base = set()

    # Copies locales pour ne pas modifier les listes originales
    prov = provisions[:]   # provisions restantes par fournisseur
    cmd  = commandes[:]    # commandes restantes par client

    # ── Curseur : on commence en haut à gauche (i=0, j=0) ────────────────────
    i, j = 0, 0

    # ── Boucle principale : on avance jusqu'à épuiser tout ───────────────────
    while i < n and j < m:

        # Quantité allouée = minimum entre ce que Pi peut fournir
        # et ce que Cj a commandé
        q = min(prov[i], cmd[j])

        # On stocke cette allocation dans la matrice et dans la base
        transport[i][j] = q
        base.add((i, j))

        if verbose:
            print(f"  b[P{i+1}, C{j+1}] = min(provision={prov[i]}, "
                  f"commande={cmd[j]}) = {q}")

        # On déduit q des provisions et commandes restantes
        prov[i] -= q
        cmd[j]  -= q

        # ── Décision : où aller ensuite ? ────────────────────────────────────
        if prov[i] == 0 and cmd[j] == 0:
            # CAS DÉGÉNÉRÉ : les deux s'épuisent en même temps
            # On avance sur la ligne (convention) sauf si c'est la dernière
            if i + 1 < n:
                i += 1
            else:
                j += 1

        elif prov[i] == 0:
            # Le fournisseur i est épuisé → on passe au fournisseur suivant
            i += 1

        else:
            # La commande j est satisfaite → on passe au client suivant
            j += 1

    if verbose:
        print(f"\n  → Base obtenue : {len(base)} arêtes "
              f"(requis pour arbre : n+m-1 = {n+m-1})")
        print()

    return transport, base