"""
=============================================================
  FICHIER : marche_pied.py
  RÔLE    : Méthode du marche-pied avec potentiel (MODI)
  SECTION : 2.1 (fonction 6 du projet)
=============================================================

PRINCIPE GÉNÉRAL :
    C'est l'algorithme d'optimisation principal. À partir d'une proposition
    initiale (obtenue par NO ou BH), on l'améliore itérativement jusqu'à
    trouver la solution optimale.

    Chaque itération :
      1. Rendre la base non-dégénérée (arbre couvrant = acyclique + connexe)
      2. Calculer les potentiels u[i] et v[j]
      3. Calculer les coûts marginaux c[i][j] - u[i] - v[j] (hors base)
      4. S'il existe un coût marginal NÉGATIF → pas optimal
         → Ajouter la meilleure arête améliorante
         → Maximiser le transport sur le cycle formé
         → Supprimer l'arête devenue nulle
      5. Si tous les coûts marginaux sont ≥ 0 → OPTIMAL, on arrête

GRAPHE BIPARTI :
    La proposition de transport est modélisée comme un graphe biparti :
    - Sommets gauches  : fournisseurs P1..Pn  (numérotés 0..n-1)
    - Sommets droits   : clients C1..Cm       (numérotés n..n+m-1)
    - Arêtes           : les cases de la BASE
    Une base valide = arbre couvrant = n+m-1 arêtes, connexe, sans cycle.
"""
import os
import sys


# ── Configurer le chemin IMMÉDIATEMENT ─────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Import en haut du fichier (jamais à l'intérieur des fonctions) ────────────
from collections import deque
from utilitaires import (afficher_proposition,
                              afficher_couts_potentiels,
                              afficher_couts_marginaux,
                              calculer_cout_total)


# ─────────────────────────────────────────────────────────────────────────────
# CONSTRUCTION DU GRAPHE BIPARTI
# ─────────────────────────────────────────────────────────────────────────────

def construire_adjacence(n, m, base):
    """
    Construit la liste d'adjacence du graphe biparti à partir de la base.

    Numérotation des sommets :
        Fournisseur i  → sommet i       (0 ≤ i < n)
        Client j       → sommet n+j     (n ≤ n+j < n+m)

    Exemple : base={(0,1),(1,0)} avec n=2, m=2
        adj[0] = [3]   (P1 connecté à C2 = sommet 3)
        adj[3] = [0]   (C2 connecté à P1)
        adj[1] = [2]   (P2 connecté à C1 = sommet 2)
        adj[2] = [1]
    """
    adj = {k: [] for k in range(n + m)}
    for (i, j) in base:
        adj[i].append(n + j)      # fournisseur i ↔ client j
        adj[n + j].append(i)
    return adj


# ─────────────────────────────────────────────────────────────────────────────
# TEST D'ACYCLICITÉ + DÉTECTION DU CYCLE (BFS)
# ─────────────────────────────────────────────────────────────────────────────

def detecter_cycle_bfs(n, m, base):
    """
    Détecte un cycle dans le graphe biparti par PARCOURS EN LARGEUR (BFS).

    Principe BFS de détection de cycle :
        On visite les sommets niveau par niveau.
        Si on tombe sur un sommet DÉJÀ VISITÉ qui n'est PAS le parent
        du sommet courant → il existe un cycle.
        On remonte alors les chemins vers leur ancêtre commun (LCA)
        pour reconstruire le cycle.

    Retourne :
        (True,  liste de sommets formant le cycle)  si cycle détecté
        (False, None)                               si acyclique
    """
    adj = construire_adjacence(n, m, base)

    visited = set()
    parent  = {}   # parent[sommet] = sommet précédent dans le BFS

    for depart in range(n + m):
        # On ne démarre que sur les sommets qui ont des arêtes
        if depart in visited or not adj[depart]:
            continue

        # Initialisation du BFS depuis ce sommet
        file = deque([depart])
        visited.add(depart)
        parent[depart] = -1   # -1 = pas de parent (racine)

        while file:
            u = file.popleft()

            for v in adj[u]:
                if v not in visited:
                    # Nouveau sommet : on le visite
                    visited.add(v)
                    parent[v] = u
                    file.append(v)

                elif parent.get(u, -1) != v:
                    # Sommet déjà visité ET pas le parent de u
                    # → CYCLE DÉTECTÉ entre u et v

                    # Reconstruire le chemin depuis u jusqu'à la racine
                    chemin_u = []
                    cur = u
                    while cur != -1:
                        chemin_u.append(cur)
                        cur = parent.get(cur, -1)

                    # Reconstruire le chemin depuis v jusqu'à la racine
                    chemin_v = []
                    cur = v
                    while cur != -1:
                        chemin_v.append(cur)
                        cur = parent.get(cur, -1)

                    # Trouver l'ancêtre commun le plus proche (LCA)
                    ensemble_u = {s: k for k, s in enumerate(chemin_u)}
                    lca = None
                    lca_idx_v = -1
                    for k_v, s in enumerate(chemin_v):
                        if s in ensemble_u:
                            lca = s
                            lca_idx_v = k_v
                            break

                    if lca is None:
                        continue

                    lca_idx_u = ensemble_u[lca]

                    # Cycle = LCA → ... → u → v → ... → LCA
                    branche_u = chemin_u[:lca_idx_u][::-1]
                    branche_v = chemin_v[:lca_idx_v]
                    cycle = [lca] + branche_u + branche_v[::-1]
                    cycle.append(lca)   # fermer le cycle

                    # Vérifier que toutes les arêtes du cycle existent
                    if _cycle_valide(cycle, adj):
                        return True, cycle

    return False, None   # aucun cycle détecté → graphe acyclique


def _cycle_valide(cycle, adj):
    """
    Vérifie que chaque arête consécutive du cycle existe dans le graphe.
    Sécurité supplémentaire après reconstruction du cycle par BFS.
    """
    for k in range(len(cycle) - 1):
        u, v = cycle[k], cycle[k + 1]
        if v not in adj[u]:
            return False
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST DE CONNEXITÉ (BFS)
# ─────────────────────────────────────────────────────────────────────────────

def tester_connexite_bfs(n, m, base):
    """
    Teste si le graphe biparti est CONNEXE par parcours en largeur (BFS).

    Un graphe est connexe s'il n'a qu'une seule composante connexe,
    c'est-à-dire qu'on peut atteindre tout sommet depuis n'importe quel autre.

    Retourne :
        connexe      (bool)       : True si connexe
        composantes  (list[list]) : liste des composantes connexes
                                    (chaque composante = liste de sommets)
    """
    adj = construire_adjacence(n, m, base)

    # On ne considère que les sommets actifs (qui ont au moins une arête)
    sommets_actifs = set()
    for (i, j) in base:
        sommets_actifs.add(i)
        sommets_actifs.add(n + j)

    if not sommets_actifs:
        return True, []

    visited     = set()
    composantes = []

    for depart in sorted(sommets_actifs):
        if depart in visited:
            continue

        # BFS depuis ce sommet → découvre toute sa composante connexe
        composante = []
        file = deque([depart])
        visited.add(depart)

        while file:
            u = file.popleft()
            composante.append(u)
            for v in adj[u]:
                if v not in visited:
                    visited.add(v)
                    file.append(v)

        composantes.append(composante)

    connexe = len(composantes) <= 1
    return connexe, composantes


# ─────────────────────────────────────────────────────────────────────────────
# MAXIMISATION DU TRANSPORT SUR UN CYCLE
# ─────────────────────────────────────────────────────────────────────────────

def maximiser_sur_cycle(n, m, transport, base, cycle, verbose=True):
    """
    Maximise le transport sur un cycle détecté (algorithme du marche-pied).

    PRINCIPE :
        On alterne les signes + et - sur les arêtes du cycle :
            arête 0 (nouvelle) : b[i][j] + δ
            arête 1            : b[i][j] - δ
            arête 2            : b[i][j] + δ
            ...
        où δ = min des valeurs sur les arêtes au signe "-"
        Après maximisation, au moins une arête "-" devient nulle
        et est supprimée de la base.

    Paramètres :
        cycle : liste de sommets bipartis formant un cycle fermé
                Exemple : [0, 3, 1, 2, 0]

    Retourne :
        transport mis à jour
        base      mise à jour
    """

    # ── Convertir le cycle (sommets bipartis) en arêtes (i, j) ───────────────
    aretes = []
    for k in range(len(cycle) - 1):
        u, v = cycle[k], cycle[k + 1]
        # Dans le graphe biparti : u<n = fournisseur, u>=n = client
        if u < n:
            aretes.append((u, v - n))    # fournisseur → client
        else:
            aretes.append((v, u - n))    # client → fournisseur (on retourne)

    # ── Identifier les arêtes "moins" (indices impairs) ───────────────────────
    aretes_moins = [(i, j) for k, (i, j) in enumerate(aretes) if k % 2 == 1]

    # δ = minimum des valeurs transportées sur les arêtes "moins"
    delta = min(transport[i][j] for (i, j) in aretes_moins)

    if verbose:
        # Affichage du cycle avec les noms lisibles
        noms = [f"P{s+1}" if s < n else f"C{s-n+1}" for s in cycle]
        print(f"\n  Cycle détecté : {' → '.join(noms)}")
        print(f"  Conditions sur le cycle :")
        for k, (i, j) in enumerate(aretes):
            signe = "+" if k % 2 == 0 else "-"
            print(f"    b[P{i+1}, C{j+1}] {signe} δ   "
                  f"(valeur actuelle = {transport[i][j]})")
        print(f"  δ = {delta}")

    # ── Appliquer les modifications ───────────────────────────────────────────
    supprimees = []
    for k, (i, j) in enumerate(aretes):
        if k % 2 == 0:
            transport[i][j] += delta    # arête "plus" : on augmente
        else:
            transport[i][j] -= delta    # arête "moins" : on diminue
            if transport[i][j] == 0:
                # Cette arête quitte la base (valeur nulle)
                supprimees.append((i, j))
                base.discard((i, j))

    if verbose:
        noms_supp = [f"b[P{i+1},C{j+1}]" for (i, j) in supprimees]
        print(f"  Arête(s) supprimée(s) de la base : {noms_supp}")

    return transport, base


# ─────────────────────────────────────────────────────────────────────────────
# CORRECTION : RENDRE LE GRAPHE ACYCLIQUE
# ─────────────────────────────────────────────────────────────────────────────

def corriger_cycles(n, m, transport, base, verbose=True):
    """
    Détecte et supprime tous les cycles de la base par maximisation répétée.
    On boucle jusqu'à ce que le graphe soit acyclique.
    """
    nb = 0
    while True:
        a_cycle, cycle = detecter_cycle_bfs(n, m, base)
        if not a_cycle:
            break
        nb += 1
        if verbose:
            print(f"\n  [Suppression cycle #{nb}]")
        transport, base = maximiser_sur_cycle(n, m, transport, base,
                                              cycle, verbose)
    return transport, base


# ─────────────────────────────────────────────────────────────────────────────
# CORRECTION : RENDRE LE GRAPHE CONNEXE
# ─────────────────────────────────────────────────────────────────────────────

def corriger_connexite(n, m, transport, base, cout, verbose=True):
    """
    Ajoute des arêtes fictives (valeur 0, dégénérées) pour rendre
    le graphe connexe.

    On trie les candidats par coût croissant et on ajoute seulement
    les arêtes qui ne créent pas de cycle.
    """
    connexe, composantes = tester_connexite_bfs(n, m, base)
    if connexe:
        return transport, base

    if verbose:
        print(f"\n  [Connexité] {len(composantes)} composantes détectées :")
        for k, comp in enumerate(composantes):
            noms = [f"P{s+1}" if s < n else f"C{s-n+1}" for s in comp]
            print(f"    Composante {k+1} : {noms}")

    # Candidats hors base triés par coût croissant
    candidats = sorted(
        (cout[i][j], i, j)
        for i in range(n)
        for j in range(m)
        if (i, j) not in base
    )

    for _, i, j in candidats:
        # Re-vérifier à chaque ajout
        connexe, _ = tester_connexite_bfs(n, m, base)
        if connexe:
            break

        # Tester si l'ajout de (i,j) crée un cycle
        base.add((i, j))
        a_cycle, _ = detecter_cycle_bfs(n, m, base)

        if a_cycle:
            # Crée un cycle → on enlève et on essaie le suivant
            base.discard((i, j))
            continue

        # Ajout validé — arête fictive avec valeur 0 (dégénérée)
        if verbose:
            print(f"    + Arête fictive b[P{i+1},C{j+1}] = 0 "
                  f"(coût = {cout[i][j]})")

    return transport, base


# ─────────────────────────────────────────────────────────────────────────────
# RENDRE LA BASE VALIDE (ARBRE COUVRANT)
# ─────────────────────────────────────────────────────────────────────────────

def rendre_arbre(n, m, transport, base, cout, verbose=True):
    """
    S'assure que la base est un arbre couvrant valide :
        1. Supprimer tous les cycles (par maximisation)
        2. Ajouter des arêtes fictives si non connexe
    Une base valide a exactement n+m-1 arêtes.
    """
    transport, base = corriger_cycles(n, m, transport, base, verbose)
    transport, base = corriger_connexite(n, m, transport, base, cout, verbose)

    if verbose:
        print(f"\n  Base après correction : {len(base)} arêtes "
              f"(requis : {n+m-1})")
    return transport, base


# ─────────────────────────────────────────────────────────────────────────────
# CALCUL DES POTENTIELS (méthode MODI)
# ─────────────────────────────────────────────────────────────────────────────

def calculer_potentiels(n, m, cout, base):
    """
    Calcule les potentiels u[i] et v[j] à partir des arêtes de la base.

    Système d'équations : u[i] + v[j] = c[i][j]  pour tout (i,j) ∈ base
    Convention de départ : u[0] = 0

    On résout par propagation itérative :
        - Si u[i] connu et v[j] inconnu → v[j] = c[i][j] - u[i]
        - Si v[j] connu et u[i] inconnu → u[i] = c[i][j] - v[j]
    On répète jusqu'à ce que tous les potentiels soient calculés.
    """
    u = [None] * n
    v = [None] * m
    u[0] = 0   # convention : premier potentiel fournisseur = 0

    changement = True
    while changement:
        changement = False
        for (i, j) in base:
            if u[i] is not None and v[j] is None:
                v[j] = cout[i][j] - u[i]
                changement = True
            elif v[j] is not None and u[i] is None:
                u[i] = cout[i][j] - v[j]
                changement = True

    # Sécurité : potentiels restés None → on met 0
    for i in range(n):
        if u[i] is None:
            u[i] = 0
    for j in range(m):
        if v[j] is None:
            v[j] = 0

    return u, v


# ─────────────────────────────────────────────────────────────────────────────
# RECHERCHE DE L'ARÊTE AMÉLIORANTE
# ─────────────────────────────────────────────────────────────────────────────

def trouver_arete_ameliorante(n, m, cout, base, u, v):
    """
    Cherche l'arête hors base avec le coût marginal le plus négatif.

    Coût marginal de (i,j) = c[i][j] - u[i] - v[j]

    Si négatif → ajouter cette arête améliore la solution.
    On prend celle avec la valeur la plus négative (amélioration maximale).

    Retourne :
        (i, j, coût_marginal)  si une arête améliorante existe
        None                   si tous les coûts marginaux ≥ 0 (OPTIMAL)
    """
    meilleure    = None
    meilleur_val = 0   # on cherche strictement < 0

    for i in range(n):
        for j in range(m):
            if (i, j) not in base:
                marginal = cout[i][j] - u[i] - v[j]
                if marginal < meilleur_val:
                    meilleur_val = marginal
                    meilleure    = (i, j, marginal)

    return meilleure


# ─────────────────────────────────────────────────────────────────────────────
# ORIENTATION DU CYCLE
# ─────────────────────────────────────────────────────────────────────────────

def orienter_cycle(cycle, i_new, j_new, n):
    """
    Réoriente le cycle pour que la nouvelle arête (i_new, j_new)
    soit en PREMIÈRE position avec le signe +.

    Cela garantit que la nouvelle arête reçoit +δ (son flux augmente),
    ce qui est nécessaire pour améliorer la solution.
    """
    L = len(cycle) - 1   # longueur du cycle sans le sommet répété

    for k in range(L):
        # Chercher i_new → n+j_new (ordre fournisseur → client)
        if cycle[k] == i_new and cycle[(k + 1) % L] == n + j_new:
            rotated = [cycle[(k + r) % L] for r in range(L)] + [cycle[k]]
            return rotated

        # Ou n+j_new → i_new (ordre inverse → on inverse le cycle)
        if cycle[k] == n + j_new and cycle[(k + 1) % L] == i_new:
            rev = cycle[-2::-1] + [cycle[-2]]
            for kk in range(L):
                if rev[kk] == i_new and rev[(kk + 1) % L] == n + j_new:
                    rotated = [rev[(kk + r) % L] for r in range(L)] + [rev[kk]]
                    return rotated

    return cycle   # cas de secours


# ─────────────────────────────────────────────────────────────────────────────
# ALGORITHME PRINCIPAL : MARCHE-PIED AVEC POTENTIEL
# ─────────────────────────────────────────────────────────────────────────────

def marche_pied(n, m, cout, transport, base, provisions, commandes,
                verbose=True):
    """
    Algorithme principal du marche-pied avec potentiel (méthode MODI).

    Itère jusqu'à atteindre la solution optimale.

    Paramètres :
        n, m       : dimensions du problème
        cout       : matrice des coûts
        transport  : proposition initiale (modifiée en place)
        base       : arêtes actives initiales (modifiée en place)
        provisions : liste des provisions
        commandes  : liste des commandes
        verbose    : afficher tout le détail des itérations

    Retourne :
        transport (list[list]) : proposition optimale
        base      (set)        : arêtes de la solution optimale
        cout_opt  (int/float)  : coût total optimal
    """

    if verbose:
        print("\n" + "═" * 62)
        print("  MÉTHODE DU MARCHE-PIED AVEC POTENTIEL")
        print("═" * 62)

    for iteration in range(1, 100_001):

        if verbose:
            print(f"\n{'─'*62}")
            print(f"  ITÉRATION {iteration}")
            print(f"{'─'*62}")
            ct = calculer_cout_total(n, m, cout, transport)
            print(f"  Coût actuel : {ct}")
            afficher_proposition(n, m, transport, base,
                                 provisions, commandes, cout,
                                 titre="PROPOSITION COURANTE")

        # ── Étape 1 : Corriger la base si elle n'est pas un arbre ─────────────
        nb_requis = n + m - 1
        if len(base) != nb_requis:
            if verbose:
                print(f"  Base dégénérée : {len(base)} arêtes "
                      f"(requis : {nb_requis}) → correction...")
            transport, base = rendre_arbre(n, m, transport, base,
                                           cout, verbose)

        # ── Étape 2 : Calculer les potentiels ─────────────────────────────────
        u, v = calculer_potentiels(n, m, cout, base)

        if verbose:
            print(f"\n  Potentiels calculés :")
            print(f"    u = {[f'u{i+1}={u[i]}' for i in range(n)]}")
            print(f"    v = {[f'v{j+1}={v[j]}' for j in range(m)]}")
            afficher_couts_potentiels(n, m, u, v)
            afficher_couts_marginaux(n, m, cout, u, v, base)

        # ── Étape 3 : Chercher une arête améliorante ──────────────────────────
        ameliorante = trouver_arete_ameliorante(n, m, cout, base, u, v)

        if ameliorante is None:
            # Tous les coûts marginaux ≥ 0 → solution optimale
            if verbose:
                print("  ✓ Tous les coûts marginaux ≥ 0 → Solution OPTIMALE !")
            break

        i_new, j_new, marg = ameliorante
        if verbose:
            print(f"\n  → Arête améliorante : b[P{i_new+1}, C{j_new+1}]"
                  f"  (coût marginal = {marg})")

        # ── Étape 4 : Ajouter l'arête et trouver le cycle formé ───────────────
        base.add((i_new, j_new))
        a_cycle, cycle = detecter_cycle_bfs(n, m, base)

        if not a_cycle:
            if verbose:
                print("  (pas de cycle après ajout → arête dégénérée conservée)")
            continue

        # ── Étape 5 : Orienter le cycle et maximiser ───────────────────────────
        cycle = orienter_cycle(cycle, i_new, j_new, n)

        if verbose:
            print(f"\n  Maximisation sur le cycle :")

        transport, base = maximiser_sur_cycle(n, m, transport, base,
                                              cycle, verbose)

    # ── Solution finale ────────────────────────────────────────────────────────
    cout_opt = calculer_cout_total(n, m, cout, transport)

    if verbose:
        print(f"\n{'═'*62}")
        print(f"  SOLUTION OPTIMALE — Coût total = {cout_opt}")
        print(f"{'═'*62}")
        afficher_proposition(n, m, transport, base,
                             provisions, commandes, cout,
                             titre="PROPOSITION OPTIMALE")

    return transport, base, cout_opt