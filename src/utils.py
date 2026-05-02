# COUT TOTAL
def cout_total(n, m, A, proposition):
    """Calcule le cout total d'une proposition de transport."""
    return sum(A[i][j] * proposition[i][j] for i in range(n) for j in range(m))


#  GRAPHE BIPARTI : ADJACENCE, CYCLE, CONNEXITE
def _lbl(k, n):
    """Label d'un noeud : P(i+1) ou C(j+1)."""
    return f"P{k+1}" if k < n else f"C{k-n+1}"


def _adj(n, m, base_set):
    """Liste d'adjacence du graphe biparti (noeuds 0..n-1 = fourn., n..n+m-1 = clients)."""
    g = {k: [] for k in range(n + m)}
    for (i, j) in base_set:
        g[i].append(n + j)
        g[n + j].append(i)
    return g
