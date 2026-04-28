"""
=============================================================
  FICHIER : utilitaires.py
  RÔLE    : Affichage soigné de tous les tableaux du projet
  SECTION : 2.1 (fonction 2 du projet)
=============================================================

Tableaux à afficher :
  1. Matrice des coûts unitaires
  2. Proposition de transport (bi,j)
  3. Table des coûts potentiels (ui + vj)
  4. Table des coûts marginaux (ci,j - ui - vj)

IMPORTANT : Les colonnes doivent être parfaitement alignées.
"""


# ─────────────────────────────────────────────────────────────────────────────
# FONCTION UTILITAIRE : calcul de la largeur de colonne
# ─────────────────────────────────────────────────────────────────────────────

def largeur_colonne(*listes_de_valeurs):
    """
    Calcule la largeur minimale nécessaire pour afficher toutes les valeurs
    passées en argument sans que les colonnes se décalent.

    On prend le maximum de len(str(v)) pour toute valeur v,
    puis on ajoute 1 pour avoir un peu d'espace.

    Exemple : valeurs = [100, -20, 5000] → max len = 4 → retourne 5
    """
    w = 4  # largeur minimale
    for liste in listes_de_valeurs:
        for v in liste:
            w = max(w, len(str(v)))  # on prend la valeur la plus large
    return w + 1  # +1 pour l'espace de séparation


# ─────────────────────────────────────────────────────────────────────────────
# TABLEAU 1 : Matrice des coûts unitaires
# ─────────────────────────────────────────────────────────────────────────────

def afficher_matrice_couts(n, m, cout, provisions, commandes):
    """
    Affiche la matrice des coûts unitaires a[i][j] avec les provisions
    et les commandes en bordure du tableau.

    Exemple de rendu :
        ╔══ MATRICE DES COÛTS ══╗
                  C1    C2    C3   Prov
               ─────────────────────────
          P1        30    20    20    450
          P2        10    50    20    250
               ─────────────────────────
          Cmd      500   600   300
    """
    print("\n╔══ MATRICE DES COÛTS ══╗")

    # Calcul de la largeur de colonne en tenant compte de toutes les valeurs
    w = largeur_colonne(
        [cout[i][j] for i in range(n) for j in range(m)],  # tous les coûts
        provisions,   # toutes les provisions
        commandes     # toutes les commandes
    )

    # Ligne de séparation horizontale
    sep = "       " + "─" * ((m + 1) * (w + 2))

    # ── En-tête : noms des colonnes C1, C2, ..., Cm + "Prov" ────────────────
    entete = "       "
    for j in range(m):
        entete += f"  {'C' + str(j + 1):>{w}}"   # droite-aligné sur w caractères
    entete += f"  {'Prov':>{w}}"
    print(entete)
    print(sep)

    # ── Corps : une ligne par fournisseur Pi ──────────────────────────────────
    for i in range(n):
        ligne = f"  {'P' + str(i + 1):<5}"   # nom du fournisseur (gauche-aligné)
        for j in range(m):
            ligne += f"  {cout[i][j]:>{w}}"  # coût a[i][j] (droite-aligné)
        ligne += f"  {provisions[i]:>{w}}"   # provision Pi
        print(ligne)

    print(sep)

    # ── Pied : commandes Cj ───────────────────────────────────────────────────
    pied = f"  {'Cmd':<5}"
    for c in commandes:
        pied += f"  {c:>{w}}"
    print(pied)
    print()


# ─────────────────────────────────────────────────────────────────────────────
# TABLEAU 2 : Proposition de transport
# ─────────────────────────────────────────────────────────────────────────────

def afficher_proposition(n, m, transport, base, provisions, commandes,
                          cout=None, titre="PROPOSITION DE TRANSPORT"):
    """
    Affiche la matrice de transport b[i][j].

    Les cases de la BASE (arêtes actives) affichent la valeur b[i][j].
    Les cases hors base affichent "-" (elles ne transportent rien).

    Paramètres :
        transport : matrice n×m des quantités transportées
        base      : set de tuples (i,j) — les arêtes actives de l'arbre
        cout      : si fourni, on affiche le coût total en bas
        titre     : titre du tableau (personnalisable)

    Exemple de rendu :
        ╔══ PROPOSITION INITIALE (NO) ══╗
                  C1    C2    C3   Prov
               ─────────────────────────
          P1       450     -     -    450
          P2        50   200     -    250
               ─────────────────────────
          Cmd      500   200     -
          Coût total : 21500
    """
    print(f"\n╔══ {titre} ══╗")

    # Calcul de la largeur en tenant compte des valeurs du transport
    vals = [transport[i][j] for i in range(n) for j in range(m)]
    w = largeur_colonne(vals, provisions, commandes)

    sep = "       " + "─" * ((m + 1) * (w + 2))

    # ── En-tête ───────────────────────────────────────────────────────────────
    entete = "       "
    for j in range(m):
        entete += f"  {'C' + str(j + 1):>{w}}"
    entete += f"  {'Prov':>{w}}"
    print(entete)
    print(sep)

    # ── Corps ─────────────────────────────────────────────────────────────────
    for i in range(n):
        ligne = f"  {'P' + str(i + 1):<5}"
        for j in range(m):
            if (i, j) in base:
                # Arête de base → on affiche la valeur transportée
                s = str(transport[i][j])
            else:
                # Hors base → tiret (aucun transport sur cette arête)
                s = "-"
            ligne += f"  {s:>{w}}"
        ligne += f"  {provisions[i]:>{w}}"
        print(ligne)

    print(sep)

    # ── Pied ──────────────────────────────────────────────────────────────────
    pied = f"  {'Cmd':<5}"
    for c in commandes:
        pied += f"  {c:>{w}}"
    print(pied)

    # ── Coût total (optionnel) ────────────────────────────────────────────────
    if cout is not None:
        total = sum(cout[i][j] * transport[i][j]
                    for i in range(n) for j in range(m))
        print(f"  Coût total : {total}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# TABLEAU 3 : Coûts potentiels
# ─────────────────────────────────────────────────────────────────────────────

def afficher_couts_potentiels(n, m, u, v):
    """
    Affiche la table des coûts potentiels : u[i] + v[j] pour tout (i,j).

    Les potentiels u[i] (fournisseurs) et v[j] (clients) sont calculés
    à partir des arêtes de base par la méthode MODI :
        u[i] + v[j] = c[i][j]  pour toute arête (i,j) de la base
    avec la convention u[0] = 0.

    Exemple de rendu :
        ╔══ COÛTS POTENTIELS (u_i + v_j) ══╗
          u\\v       30    10    20
                ────────────────────
          0         30    10    20
          -20       10   -10     0
    """
    print("\n╔══ COÛTS POTENTIELS (u_i + v_j) ══╗")

    # Calcul de toutes les valeurs u[i]+v[j]
    pot = [[u[i] + v[j] for j in range(m)] for i in range(n)]

    # Largeur de colonne adaptée aux potentiels (qui peuvent être négatifs)
    w = largeur_colonne(
        [pot[i][j] for i in range(n) for j in range(m)],
        u, v
    )

    # ── En-tête : affiche les v[j] ────────────────────────────────────────────
    # La première colonne affiche "u\v" pour indiquer la structure
    entete = f"  {'u\\v':<8}"
    for j in range(m):
        entete += f"  {v[j]:>{w}}"
    print(entete)
    print("          " + "─" * (m * (w + 2)))

    # ── Corps : une ligne par u[i], affiche u[i]+v[j] ─────────────────────────
    for i in range(n):
        ligne = f"  {u[i]:<8}"   # u[i] en première colonne
        for j in range(m):
            ligne += f"  {pot[i][j]:>{w}}"
        print(ligne)
    print()


# ─────────────────────────────────────────────────────────────────────────────
# TABLEAU 4 : Coûts marginaux
# ─────────────────────────────────────────────────────────────────────────────

def afficher_couts_marginaux(n, m, cout, u, v, base):
    """
    Affiche la table des coûts marginaux : c[i][j] - u[i] - v[j].

    Le coût marginal est calculé uniquement pour les cases HORS BASE.
    Pour les cases de la base, on affiche "(base)".

    Interprétation :
        - Si un coût marginal est NÉGATIF → la solution n'est pas optimale,
          cette arête est une candidate à l'amélioration.
        - Si tous les coûts marginaux sont ≥ 0 → solution OPTIMALE.

    Exemple de rendu :
        ╔══ COÛTS MARGINAUX (c_ij - u_i - v_j) ══╗
                   C1      C2      C3
               ─────────────────────────
          P1    (base)      10   (base)
          P2       -20  (base)      15
    """
    print("\n╔══ COÛTS MARGINAUX (c_ij - u_i - v_j) ══╗")

    # Calcul des coûts marginaux pour les cases hors base
    marginaux = {}
    for i in range(n):
        for j in range(m):
            if (i, j) not in base:
                # Coût marginal = coût réel - potentiel de la case
                marginaux[(i, j)] = cout[i][j] - u[i] - v[j]

    # Largeur de colonne : on inclut len("(base)") = 6
    vals = list(marginaux.values()) if marginaux else [0]
    w = largeur_colonne(vals)
    w = max(w, 6)  # au moins 6 pour "(base)"

    # ── En-tête ───────────────────────────────────────────────────────────────
    entete = "       "
    for j in range(m):
        entete += f"  {'C' + str(j + 1):>{w}}"
    print(entete)
    print("       " + "─" * (m * (w + 2)))

    # ── Corps ─────────────────────────────────────────────────────────────────
    for i in range(n):
        ligne = f"  {'P' + str(i + 1):<5}"
        for j in range(m):
            if (i, j) in base:
                ligne += f"  {'(base)':>{w}}"
            else:
                ligne += f"  {marginaux[(i, j)]:>{w}}"
        print(ligne)
    print()

    # Retourner le dict des marginaux (utile pour le marche-pied)
    return marginaux


# ─────────────────────────────────────────────────────────────────────────────
# CALCUL DU COÛT TOTAL
# ─────────────────────────────────────────────────────────────────────────────

def calculer_cout_total(n, m, cout, transport):
    """
    Calcule le coût total d'une proposition de transport.

    Formule : Σ(i,j) c[i][j] × b[i][j]

    C'est la valeur que l'on cherche à minimiser.
    """
    return sum(cout[i][j] * transport[i][j]
               for i in range(n)
               for j in range(m))