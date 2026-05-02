#  2. AFFICHAGE DES TABLEAUX
def _lw(n, m, A, provisions, commandes):
    """Largeur de colonne pour l'alignement."""
    w = 4
    for i in range(n):
        for j in range(m):
            w = max(w, len(str(A[i][j])))
    w = max(w, len(str(max(provisions))), len(str(max(commandes))))
    return w + 2


def _label_w(n, m):
    return max(len(f"P{n}"), len(f"C{m}")) + 2


def afficher_matrice_couts(n, m, A, provisions, commandes):
    """Affiche la matrice des couts unitaires."""
    w = _lw(n, m, A, provisions, commandes)
    lw = _label_w(n, m)
    sep_len = lw + 6 + (w + 2) * m + 12
    print("\n" + "=" * sep_len)
    print("  MATRICE DES COUTS")
    print("=" * sep_len)
    # En-tete
    h = " " * (lw + 6)
    for j in range(m):
        h += f"{'C'+str(j+1):^{w+2}}"
    h += f"  {'Provis.':>8}"
    print(h)
    print("  " + "-" * (sep_len - 2))
    for i in range(n):
        row = f"  {'P'+str(i+1):<{lw}}  "
        for j in range(m):
            row += f"{A[i][j]:>{w+2}}"
        row += f"  {provisions[i]:>8}"
        print(row)
    print("  " + "-" * (sep_len - 2))
    row = f"  {'Comm.':<{lw}}  "
    for j in range(m):
        row += f"{commandes[j]:>{w+2}}"
    print(row)
    print()


def afficher_proposition(n, m, A, proposition, provisions, commandes,
                          base_set, label="PROPOSITION DE TRANSPORT"):
    """Affiche la proposition : cases de base entre parentheses, autres '-'."""
    w = _lw(n, m, A, provisions, commandes) + 2   # largeur cellule (avec parentheses)
    lw = _label_w(n, m)
    sep_len = lw + 6 + w * m + 12
    print("\n" + "=" * sep_len)
    print(f"  {label}")
    print("=" * sep_len)
    h = " " * (lw + 6)
    for j in range(m):
        h += f"{'C'+str(j+1):^{w}}"
    h += f"  {'Provis.':>8}"
    print(h)
    print("  " + "-" * (sep_len - 2))
    for i in range(n):
        row = f"  {'P'+str(i+1):<{lw}}  "
        for j in range(m):
            if (i, j) in base_set:
                cell = f"({proposition[i][j]})"
            else:
                cell = "-"
            row += f"{cell:^{w}}"
        row += f"  {provisions[i]:>8}"
        print(row)
    print("  " + "-" * (sep_len - 2))
    row = f"  {'Comm.':<{lw}}  "
    for j in range(m):
        row += f"{commandes[j]:^{w}}"
    print(row)
    print()


def afficher_potentiels(n, m, u, v):
    """Affiche les potentiels u_i et v_j."""
    print("\n  POTENTIELS")
    print("  " + "-" * 50)
    print("    Fournisseurs : " + "  ".join(f"u[P{i+1}]={u[i]}" for i in range(n)))
    print("    Clients      : " + "  ".join(f"v[C{j+1}]={v[j]}" for j in range(m)))
    print()


def afficher_table_couts_potentiels(n, m, A, u, v, provisions, commandes):
    """Affiche la table des couts potentiels u_i + v_j."""
    vals_str = [str(u[i] + v[j]) for i in range(n) for j in range(m)]
    w = max(6, max(len(s) for s in vals_str) + 2)
    lw = _label_w(n, m)
    sep_len = lw + 6 + w * m + 4
    print("\n" + "=" * sep_len)
    print("  TABLE DES COUTS POTENTIELS  (u_i + v_j)")
    print("=" * sep_len)
    h = " " * (lw + 6)
    for j in range(m):
        h += f"{'C'+str(j+1):^{w}}"
    print(h)
    print("  " + "-" * (sep_len - 2))
    for i in range(n):
        row = f"  {'P'+str(i+1):<{lw}}  "
        for j in range(m):
            row += f"{u[i]+v[j]:^{w}}"
        print(row)
    print()


def afficher_table_marginaux(n, m, A, u, v, base_set):
    """
    Affiche la table des couts marginaux a_ij - u_i - v_j.
    Cases de base -> '--'. Retourne (meilleure_arete, valeur_min).
    """
    hors_base_vals = [A[i][j] - u[i] - v[j]
                      for i in range(n) for j in range(m)
                      if (i, j) not in base_set]
    w = max(6, (max(len(str(x)) for x in hors_base_vals) + 2) if hors_base_vals else 6)
    lw = _label_w(n, m)
    sep_len = lw + 6 + w * m + 4
    print("\n" + "=" * sep_len)
    print("  TABLE DES COUTS MARGINAUX  (a_ij - u_i - v_j)")
    print("  (cases de base affichees comme '--')")
    print("=" * sep_len)
    h = " " * (lw + 6)
    for j in range(m):
        h += f"{'C'+str(j+1):^{w}}"
    print(h)
    print("  " + "-" * (sep_len - 2))

    meilleure = None
    meilleure_val = 0
    for i in range(n):
        row = f"  {'P'+str(i+1):<{lw}}  "
        for j in range(m):
            if (i, j) in base_set:
                row += f"{'--':^{w}}"
            else:
                marg = A[i][j] - u[i] - v[j]
                row += f"{marg:^{w}}"
                if marg < meilleure_val:
                    meilleure_val = marg
                    meilleure = (i, j)
        print(row)
    print()
    return meilleure, meilleure_val
