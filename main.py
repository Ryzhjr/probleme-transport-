import sys

from src.lecteur import lire_probleme

from src.affichage import (
    afficher_matrice_couts,
    afficher_proposition
)

from src.nord_ouest import nord_ouest
from src.balas_hammer import balas_hammer

from src.marche_pied import marche_pied
from src.utils import cout_total

from src.complexite import etude_complexite


def resoudre_probleme(fichier, algo):
    print("\n" + "=" * 65)
    print(f"  Fichier : {fichier}")
    print(f"  Algorithme initial : {'Nord-Ouest' if algo == 'NO' else 'Balas-Hammer'}")
    print("=" * 65)

    n, m, A, provisions, commandes = lire_probleme(fichier)

    afficher_matrice_couts(n, m, A, provisions, commandes)

    if algo == 'NO':
        prop_init, base_init = nord_ouest(n, m, provisions, commandes)
    else:
        prop_init, base_init = balas_hammer(n, m, A, provisions, commandes)

    cout_init = cout_total(n, m, A, prop_init)

    print(f"\n  Cout de la proposition initiale : {cout_init}")

    afficher_proposition(
        n, m, A, prop_init, provisions, commandes,
        base_set=base_init,
        label="PROPOSITION INITIALE"
    )

    # Marche-pied
    prop_opt, base_opt, cout_opt = marche_pied(
        n, m, A, prop_init, base_init, provisions, commandes
    )

    return prop_opt, base_opt, cout_opt


def menu_principal():
    print("\n" + "=" * 65)
    print("  RESOLUTION DE PROBLEMES DE TRANSPORT")
    print("  Efrei Paris - Recherche Operationnelle S6")
    print("=" * 65)

    while True:
        print("\nOptions :")
        print("  1. Resoudre un probleme")
        print("  2. Etude de complexite")
        print("  0. Quitter")

        choix = input("\nVotre choix : ").strip()

        if choix == '0':
            print("Au revoir !")
            break
            
        elif choix == '1':

            print("\nChoisissez un probleme :")
            for i in range(1, 13):
                print(f"  {i}. probleme{i}.txt")

            choix_fichier = input("Votre choix (1-12) : ").strip()

            if not choix_fichier.isdigit():
                print("Choix invalide.")
                continue

            num = int(choix_fichier)

            if num < 1 or num > 12:
                print("Choix invalide.")
                continue

            fichier = f"donnees/probleme{num}.txt"

            print("\nAlgorithme initial :")
            print("  1. Nord-Ouest")
            print("  2. Balas-Hammer")

            choix_algo = input("Votre choix (1/2) : ").strip()
            algo = 'NO' if choix_algo == '1' else 'BH'

            try:
                resoudre_probleme(fichier, algo)

            except FileNotFoundError:
                print(f"\nFichier '{fichier}' introuvable.")

            except AssertionError as e:
                print(f"\nErreur dans les donnees : {e}")

            except Exception as e:
                print(f"\nErreur : {e}")
                import traceback
                traceback.print_exc()

            input("\nAppuie sur Entrée pour revenir au menu...")

        elif choix == '2':
            print("\nLancement de l'etude de complexite...\n")

            try:
                etude_complexite()
            except Exception as e:
                print(f"Erreur : {e}")

            input("\nAppuie sur Entrée pour revenir au menu...")

        else:
            print("Choix invalide. Recommence.")

if __name__ == "__main__":
    menu_principal()
