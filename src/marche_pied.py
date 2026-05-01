from collections import deque
import copy

from src.utils import _adj, _lbl
from src.affichage import (
    afficher_proposition,
    afficher_potentiels,
    afficher_table_couts_potentiels,
    afficher_table_marginaux
)
from src.utils import cout_total

def detecter_cycle_bfs(n, m, base_set):
    """
    Detecte un cycle via BFS sur le graphe biparti.
    Retourne (True, cycle_noeuds) ou (False, None).

    Pseudo-code :
      Pour chaque noeud non visite ayant des aretes :
        BFS ; si on rencontre un voisin deja visite != parent => cycle
        Reconstituer le cycle par remontee des parents
    """
    g = _adj(n, m, base_set)
    visite = {}
    parent = {}

    for start in range(n + m):
        if start in visite or not g[start]:
            continue
        queue = deque([start])
        visite[start] = True
        parent[start] = -1

        while queue:
            u = queue.popleft()
            for v in g[u]:
                if v not in visite:
                    visite[v] = True
                    parent[v] = u
                    queue.append(v)
                elif v != parent[u]:
                    # Reconstituer le cycle : remonter de u et v jusqu'a leur ancetre commun
                    chemin_u = []
                    x = u
                    while x != -1:
                        chemin_u.append(x); x = parent[x]
                    chemin_v = []
                    x = v
                    while x != -1:
                        chemin_v.append(x); x = parent[x]
                    set_u = {node: idx for idx, node in enumerate(chemin_u)}
                    ancetre = next((node for node in chemin_v if node in set_u), None)
                    if ancetre is None:
                        cycle = chemin_u + [v]
                    else:
                        idx_anc = set_u[ancetre]
                        part_u = chemin_u[:idx_anc + 1]
                        idx_anc_v = chemin_v.index(ancetre)
                        part_v = chemin_v[:idx_anc_v]
                        cycle = part_u + list(reversed(part_v))

                    print(f"  *** Cycle detecte : {' -> '.join(_lbl(k,n) for k in cycle)} ***")
                    return True, cycle

    return False, None


def tester_connexe_bfs(n, m, base_set):
    """
    Teste la connexite via BFS.
    Retourne (est_connexe, composantes).

    Pseudo-code :
      BFS depuis le 1er noeud actif
      Si tous les noeuds actifs sont atteints => connexe
    """
    g = _adj(n, m, base_set)
    actifs = set(k for k in range(n + m) if g[k])

    if not actifs:
        return True, []

    visite = set()
    composantes = []

    for start in actifs:
        if start in visite:
            continue
        comp = set()
        queue = deque([start])
        visite.add(start); comp.add(start)
        while queue:
            u = queue.popleft()
            for v in g[u]:
                if v not in visite:
                    visite.add(v); comp.add(v); queue.append(v)
        composantes.append(comp)

    if len(composantes) == 1:
        return True, composantes
    else:
        print(f"\n  *** Graphe NON connexe : {len(composantes)} composante(s) ***")
        for idx, comp in enumerate(composantes):
            print(f"    Composante {idx+1} : {sorted(_lbl(k,n) for k in comp)}")
        return False, composantes


# ============================================================
#  7. MAXIMISATION SUR UN CYCLE
# ============================================================

def maximiser_sur_cycle(n, m, proposition, cycle, base_set, arete_entree=None):
    """
    Maximise le transport sur un cycle detecte.
    L'arete d'entree (si fournie) recoit le signe (+).
    delta = min des cases (-).
    Retourne (proposition_modifiee, base_set_modifie).

    Pseudo-code :
      Construire les paires (i,j) du cycle dans l'ordre
      Alterner +/- en commencant par + sur l'arete d'entree
      delta = min(b[i][j]) pour les cases (-)
      Appliquer : cases (+) += delta, cases (-) -= delta
      Retirer de la base les cases devenues nulles
    """
    # Construire les paires (i,j) dans l'ordre du cycle
    paires = []
    for k in range(len(cycle) - 1):
        u, v = cycle[k], cycle[k + 1]
        if u < n and v >= n:
            paires.append((u, v - n))
        elif v < n and u >= n:
            paires.append((v, u - n))

    if not paires:
        return proposition, base_set

    # Placer l'arete d'entree en premier (signe +)
    if arete_entree is not None and arete_entree in paires:
        idx = paires.index(arete_entree)
        paires = paires[idx:] + paires[:idx]

    plus_cases  = paires[0::2]
    moins_cases = paires[1::2]

    print("\n  Conditions sur le cycle :")
    for idx, (i, j) in enumerate(paires):
        signe = "+" if idx % 2 == 0 else "-"
        print(f"    b[P{i+1}][C{j+1}] = {proposition[i][j]}  ({signe})")

    if not moins_cases:
        print("  Aucune case (-) : pas de modification possible.")
        return proposition, base_set

    delta = min(proposition[i][j] for i, j in moins_cases)
    print(f"\n  delta = {delta}")

    prop = copy.deepcopy(proposition)
    new_base = set(base_set)
    supprimees = []

    for i, j in plus_cases:
        prop[i][j] += delta
        new_base.add((i, j))
    for i, j in moins_cases:
        prop[i][j] -= delta
        if prop[i][j] == 0:
            supprimees.append((i, j))
            new_base.discard((i, j))

    if supprimees:
        print("  Arete(s) supprimee(s) : " +
              ", ".join(f"b[P{i+1}][C{j+1}]" for i, j in supprimees))
    else:
        print("  Aucune arete supprimee (delta = 0).")

    return prop, new_base


# ============================================================
#  8. CALCUL DES POTENTIELS
# ============================================================

def calculer_potentiels(n, m, A, base_set):
    """
    Calcule les potentiels u_i et v_j.
    On pose u[0] = 0 et on resout u[i] + v[j] = a[i][j] pour chaque case de base.

    Pseudo-code :
      u[0] = 0
      Propager par fixpoint :
        Si u[i] connu et v[j] inconnu => v[j] = a[i][j] - u[i]
        Si v[j] connu et u[i] inconnu => u[i] = a[i][j] - v[j]
    """
    u = [None] * n
    v = [None] * m
    u[0] = 0

    changed = True
    while changed:
        changed = False
        for (i, j) in base_set:
            if u[i] is not None and v[j] is None:
                v[j] = A[i][j] - u[i]; changed = True
            elif v[j] is not None and u[i] is None:
                u[i] = A[i][j] - v[j]; changed = True

    # Potentiels non determines (graphe non connexe)
    for i in range(n):
        if u[i] is None: u[i] = 0
    for j in range(m):
        if v[j] is None: v[j] = 0

    return u, v


# ============================================================
#  9. COMPLETION DU GRAPHE (non connexe -> arbre couvrant)
# ============================================================

def completer_graphe(n, m, A, proposition, base_set):
    """
    Ajoute des aretes epsilon (valeur 0) pour rendre le graphe connexe.
    On choisit les aretes hors-base de cout minimal qui relient deux composantes.
    Retourne (proposition_modifiee, base_set_modifie).

    Pseudo-code :
      Trier les cases hors-base par cout croissant
      Tant que non connexe :
        Ajouter la case de cout minimal reliant deux composantes distinctes
    """
    prop = copy.deepcopy(proposition)
    new_base = set(base_set)

    cases_vides = sorted(
        ((A[i][j], i, j) for i in range(n) for j in range(m) if (i, j) not in new_base),
        key=lambda x: x[0]
    )

    for _, i, j in cases_vides:
        connexe, composantes = tester_connexe_bfs(n, m, new_base)
        if connexe:
            break
        # Verifier que cette arete relie deux composantes differentes
        test_base = new_base | {(i, j)}
        _, comp_test = tester_connexe_bfs(n, m, test_base)
        if len(comp_test) < len(composantes):
            prop[i][j] = 0   # valeur epsilon
            new_base.add((i, j))
            print(f"  Arete fictive ajoutee : b[P{i+1}][C{j+1}] = 0 (epsilon)")

    return prop, new_base


def rendre_non_degenere(n, m, A, proposition, base_set):
    """
    Corrige la degenerescence :
    1. Elimine tous les cycles par maximisation repetee
    2. Complete si non connexe
    Retourne (proposition_corrigee, base_set_corrige).
    """
    prop = copy.deepcopy(proposition)
    new_base = set(base_set)

    # Etape 1 : eliminer tous les cycles
    for _ in range(200):
        cycle_existe, cycle = detecter_cycle_bfs(n, m, new_base)
        if not cycle_existe:
            break
        prop, new_base = maximiser_sur_cycle(n, m, prop, cycle, new_base)

    # Etape 2 : rendre connexe
    connexe, _ = tester_connexe_bfs(n, m, new_base)
    if not connexe:
        prop, new_base = completer_graphe(n, m, A, prop, new_base)

    return prop, new_base


# ============================================================
#  10. CYCLE ELEMENTAIRE POUR L'ARETE AMELIORANTE
# ============================================================

def trouver_cycle_pour_arete(n, m, base_set, i_star, j_star):
    """
    Trouve le cycle elementaire forme en ajoutant l'arete (i_star, j_star)
    dans l'arbre de la base (SANS cette arete).
    BFS depuis i_star vers (n+j_star), puis fermeture du cycle.
    Retourne la liste des noeuds du cycle (premier = dernier).
    """
    base_sans = base_set - {(i_star, j_star)}
    g = _adj(n, m, base_sans)

    start = i_star
    end = n + j_star
    visite = {start: None}
    queue = deque([start])

    while queue:
        u = queue.popleft()
        if u == end:
            break
        for v in g[u]:
            if v not in visite:
                visite[v] = u
                queue.append(v)

    if end not in visite:
        return [start, end, start]

    path = []
    cur = end
    while cur is not None:
        path.append(cur); cur = visite.get(cur)
    path.reverse()
    return path + [path[0]]


# ============================================================
#  11. METHODE DU MARCHE-PIED AVEC POTENTIEL
# ============================================================

def marche_pied(n, m, A, proposition_initiale, base_set_init, provisions, commandes):
    """
    Methode du marche-pied avec potentiel.

    Pseudo-code :
      prop, base <- proposition_initiale
      Tant que non optimal (max 500 iterations) :
        1. Corriger degenerescence (cycles + connexite)
        2. Calculer potentiels u, v
        3. Afficher tables couts potentiels et marginaux
        4. Si tous marginaux >= 0 => optimal, stop
        5. Sinon trouver arete ameliorante (i*,j*)
               Trouver le cycle elementaire
               Maximiser sur ce cycle
      Afficher proposition optimale et cout final
    """
    prop = copy.deepcopy(proposition_initiale)
    base = set(base_set_init)
    MAX_ITER = 500

    for iteration in range(1, MAX_ITER + 1):
        print("\n" + "#" * 65)
        print(f"  MARCHE-PIED - Iteration {iteration}")
        print("#" * 65)

        cout = cout_total(n, m, A, prop)
        print(f"\n  Cout total courant : {cout}")
        afficher_proposition(n, m, A, prop, provisions, commandes, base_set=base)

        # Verification et correction de la degenerescence
        nb_base = len(base)
        attendu = n + m - 1
        print(f"  Cases de base : {nb_base} (attendu : {attendu})")
        prop, base = rendre_non_degenere(n, m, A, prop, base)
        nb_base = len(base)
        if nb_base != attendu:
            print(f"  Apres correction : {nb_base} cases de base")

        # Calcul et affichage des potentiels
        u, v = calculer_potentiels(n, m, A, base)
        afficher_potentiels(n, m, u, v)
        afficher_table_couts_potentiels(n, m, A, u, v, provisions, commandes)
        meilleure, marg_min = afficher_table_marginaux(n, m, A, u, v, base)

        if meilleure is None:
            print("  *** SOLUTION OPTIMALE ATTEINTE ***")
            break

        i_star, j_star = meilleure
        print(f"  Meilleure arete ameliorante : b[P{i_star+1}][C{j_star+1}]"
              f"  (cout marginal = {marg_min})")

        # Trouver le cycle elementaire et maximiser
        cycle = trouver_cycle_pour_arete(n, m, base, i_star, j_star)
        print(f"  Cycle elementaire : {' -> '.join(_lbl(k,n) for k in cycle)}")

        prop[i_star][j_star] = 0   # sera mis a jour par maximiser_sur_cycle
        base.add((i_star, j_star))
        prop, base = maximiser_sur_cycle(n, m, prop, cycle, base,
                                          arete_entree=(i_star, j_star))
    else:
        print(f"  *** ATTENTION : limite de {MAX_ITER} iterations atteinte ***")

    cout_final = cout_total(n, m, A, prop)
    print("\n" + "=" * 65)
    print("  RESULTAT FINAL")
    print("=" * 65)
    afficher_proposition(n, m, A, prop, provisions, commandes,
                          base_set=base, label="PROPOSITION OPTIMALE")
    print(f"  Cout total optimal : {cout_final}")
    return prop, base, cout_final