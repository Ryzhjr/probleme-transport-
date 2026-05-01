# ============================================================
#  4. ALGORITHME BALAS-HAMMER
# ============================================================

def _calculer_penalites(n, m, A, prov, comm, ligne_fermee, col_fermee):
    """
    Penalites Balas-Hammer : 2e_min - 1er_min sur chaque ligne/colonne ouverte.
    """
    pen_l = []
    for i in range(n):
        if ligne_fermee[i] or prov[i] == 0:
            pen_l.append(None); continue
        vals = sorted(A[i][j] for j in range(m)
                      if not col_fermee[j] and comm[j] > 0)
        if len(vals) >= 2:   pen_l.append(vals[1] - vals[0])
        elif len(vals) == 1: pen_l.append(vals[0])
        else:                pen_l.append(None)

    pen_c = []
    for j in range(m):
        if col_fermee[j] or comm[j] == 0:
            pen_c.append(None); continue
        vals = sorted(A[i][j] for i in range(n)
                      if not ligne_fermee[i] and prov[i] > 0)
        if len(vals) >= 2:   pen_c.append(vals[1] - vals[0])
        elif len(vals) == 1: pen_c.append(vals[0])
        else:                pen_c.append(None)

    return pen_l, pen_c


def balas_hammer(n, m, A, provisions, commandes):
    """
    Proposition initiale par la methode de Balas-Hammer.
    Retourne (proposition, base_set).

    Pseudo-code :
      Tant qu'il reste des cases non satisfaites :
        Calculer penalites lignes et colonnes
        Choisir la ligne/colonne de penalite maximale
        Affecter le max possible dans la case de cout minimal
        Fermer la ligne ou colonne epuisee
    """
    print("\n" + "=" * 60)
    print("  ALGORITHME BALAS-HAMMER")
    print("=" * 60)

    prov = list(provisions)
    comm = list(commandes)
    prop = [[0] * m for _ in range(n)]
    base_set = set()
    ligne_fermee = [False] * n
    col_fermee = [False] * m
    iteration = 0

    while True:
        if all(p == 0 for p in prov) or all(c == 0 for c in comm):
            break
        iteration += 1
        pen_l, pen_c = _calculer_penalites(n, m, A, prov, comm, ligne_fermee, col_fermee)

        print(f"\n  --- Iteration {iteration} ---")
        print("  Penalites lignes  : " +
              ", ".join(f"P{i+1}={pen_l[i]}" for i in range(n) if pen_l[i] is not None))
        print("  Penalites colonnes: " +
              ", ".join(f"C{j+1}={pen_c[j]}" for j in range(m) if pen_c[j] is not None))

        max_pen = -1
        best = None
        for i in range(n):
            if pen_l[i] is not None and pen_l[i] > max_pen:
                max_pen = pen_l[i]; best = ('L', i)
        for j in range(m):
            if pen_c[j] is not None and pen_c[j] > max_pen:
                max_pen = pen_c[j]; best = ('C', j)

        if best is None:
            break

        if best[0] == 'L':
            i_star = best[1]
            print(f"  Penalite maximale = {max_pen} sur ligne P{i_star+1}")
            cols = [j for j in range(m) if not col_fermee[j] and comm[j] > 0]
            j_star = min(cols, key=lambda j: A[i_star][j])
        else:
            j_star = best[1]
            print(f"  Penalite maximale = {max_pen} sur colonne C{j_star+1}")
            ligs = [i for i in range(n) if not ligne_fermee[i] and prov[i] > 0]
            i_star = min(ligs, key=lambda i: A[i][j_star])

        val = min(prov[i_star], comm[j_star])
        prop[i_star][j_star] += val
        base_set.add((i_star, j_star))
        prov[i_star] -= val
        comm[j_star] -= val
        print(f"  Affectation b[P{i_star+1}][C{j_star+1}] = {val}  (cout={A[i_star][j_star]})")

        if prov[i_star] == 0:
            ligne_fermee[i_star] = True
            print(f"  => Fermeture de la ligne P{i_star+1}")
        if comm[j_star] == 0:
            col_fermee[j_star] = True
            print(f"  => Fermeture de la colonne C{j_star+1}")

    print(f"  => {len(base_set)} cases de base (attendu : {n+m-1})")
    return prop, base_set
