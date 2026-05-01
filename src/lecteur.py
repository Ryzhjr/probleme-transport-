def lire_probleme(fichier: str):
    """
    Lit un fichier .txt de probleme de transport.
    Retourne : n, m, A (matrice des couts), provisions, commandes.

    Format attendu :
      n m
      a1,1 ... a1,m P1
      ...
      an,1 ... an,m Pn
      C1 C2 ... Cm
    """
    with open(fichier, 'r') as f:
        lignes = [l.strip() for l in f if l.strip()]

    n, m = int(lignes[0].split()[0]), int(lignes[0].split()[1])
    A = []
    provisions = []
    for i in range(1, n + 1):
        vals = list(map(int, lignes[i].split()))
        A.append(vals[:m])
        provisions.append(vals[m])
    commandes = list(map(int, lignes[n + 1].split()))

    assert len(provisions) == n
    assert len(commandes) == m
    assert sum(provisions) == sum(commandes), "Probleme non equilibre"
    return n, m, A, provisions, commandes
