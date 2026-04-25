def lire_fichier_transport(chemin):
    with open(chemin, "r") as fichier:
        lignes = fichier.readlines()

    n, m = map(int, lignes[0].split())

    couts = []
    provisions = []

    for i in range(1, n + 1):
        valeurs = list(map(int, lignes[i].split()))
        couts.append(valeurs[:-1])
        provisions.append(valeurs[-1])

    demandes = list(map(int, lignes[n + 1].split()))

    return couts, provisions, demandes