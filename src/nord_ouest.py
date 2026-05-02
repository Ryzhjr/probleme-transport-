#  ALGORITHME NORD-OUEST
def nord_ouest(n, m, provisions, commandes):
    """
    Proposition initiale par la methode du coin Nord-Ouest.
    Retourne (proposition, base_set).
    """
    print("\n" + "=" * 60)
    print("  ALGORITHME NORD-OUEST")
    print("=" * 60)

    prov = list(provisions)
    comm = list(commandes)
    prop = [[0] * m for _ in range(n)]
    base_set = set()

    i, j = 0, 0
    while i < n and j < m:
        val = min(prov[i], comm[j])
        prop[i][j] = val
        base_set.add((i, j))
        prov[i] -= val
        comm[j] -= val
        print(f"    Affectation b[P{i+1}][C{j+1}] = {val}")

        if prov[i] == 0 and comm[j] == 0:
            i += 1
            if i < n and j + 1 < m:
                j += 1
        elif prov[i] == 0:
            i += 1
        else:
            j += 1

    print(f"  => {len(base_set)} cases de base (attendu : {n+m-1})")
    return prop, base_set
