"""
=============================================================
  FICHIER : lecteur.py
  RÔLE    : Lecture du fichier .txt et stockage en mémoire
  SECTION : 2.1 (fonction 1 du projet)
=============================================================

FORMAT DU FICHIER .txt :
    n m
    a[1,1]  a[1,2]  ...  a[1,m]  P1
    a[2,1]  a[2,2]  ...  a[2,m]  P2
    ...
    a[n,1]  a[n,2]  ...  a[n,m]  Pn
    C1  C2  ...  Cm
"""


def lire_probleme(nom_fichier):
    """
    Lit un fichier .txt de problème de transport et retourne
    toutes les données structurées en mémoire.

    Supporte deux formats :
    Format 1 : coûts + provision sur la même ligne
        n m
        a[1,1] a[1,2] ... a[1,m]  P1
        a[2,1] a[2,2] ... a[2,m]  P2
        ...
        C1  C2  ...  Cm

    Format 2 : coûts seuls, puis provisions séparées, puis commandes
        n m
        a[1,1] a[1,2] ... a[1,m]
        a[2,1] a[2,2] ... a[2,m]
        ...
        P1  P2  ...  Pn
        C1  C2  ...  Cm

    Retourne :
        n          (int)        : nombre de fournisseurs
        m          (int)        : nombre de clients
        cout       (list[list]) : matrice n×m des coûts unitaires
        provisions (list)       : liste des n provisions [P1..Pn]
        commandes  (list)       : liste des m commandes  [C1..Cm]
    """

    # ── Étape 1 : Ouverture et nettoyage du fichier ───────────────────────────
    with open(nom_fichier, 'r') as f:
        # On lit toutes les lignes, on supprime les espaces inutiles
        # et on ignore les lignes vides avec le filtre l.strip()
        lignes = [l.strip() for l in f if l.strip()]

    # ── Étape 2 : Lecture des dimensions n et m (1ère ligne) ─────────────────
    # Exemple : "4 3" → n=4 fournisseurs, m=3 clients
    premiere = lignes[0].split()
    n = int(premiere[0])   # nombre de fournisseurs (lignes du tableau)
    m = int(premiere[1])   # nombre de clients (colonnes du tableau)

    # ── Étape 3 : Détection du format et lecture ──────────────────────────────
    cout       = []   # contiendra la matrice des coûts unitaires
    provisions = []   # contiendra la provision de chaque fournisseur

    # Vérifier le format en regardant la première ligne de données
    premiere_ligne_donnees = list(map(int, lignes[1].split()))
    
    if len(premiere_ligne_donnees) == m + 1:
        # Format 1 : provisions à la fin de chaque ligne de coûts
        for i in range(1, n + 1):
            vals = list(map(int, lignes[i].split()))
            cout.append(vals[:m])        # les m premiers = coûts a[i][0..m-1]
            provisions.append(vals[m])   # le dernier     = provision Pi
        
        # Les commandes sont à la ligne n+2
        commandes = list(map(int, lignes[n + 1].split()))
    
    elif len(premiere_ligne_donnees) == m:
        # Format 2 : provisions sur une ligne séparée, commandes sur une autre
        for i in range(1, n + 1):
            vals = list(map(int, lignes[i].split()))
            cout.append(vals)  # tous les éléments = coûts
        
        # Les provisions sont à la ligne n+2
        provisions = list(map(int, lignes[n + 1].split()))
        
        # Les commandes sont à la ligne n+3
        commandes = list(map(int, lignes[n + 2].split()))
    
    else:
        raise ValueError(f"Format non reconnu : première ligne de données a {len(premiere_ligne_donnees)} valeurs "
                        f"(attendu {m} ou {m+1})")

    # ── Étape 4 : Vérification de l'équilibre ΣPi = ΣCj ─────────────────────
    # Le projet impose le cas équilibré ; on affiche un avertissement sinon
    if sum(provisions) != sum(commandes):
        print(f"  ⚠ ATTENTION : problème non équilibré !")
        print(f"    ΣP = {sum(provisions)}, ΣC = {sum(commandes)}")
    else:
        print(f"  ✓ Problème équilibré : ΣP = ΣC = {sum(provisions)}")

    return n, m, cout, provisions, commandes