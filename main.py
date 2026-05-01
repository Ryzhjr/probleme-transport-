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
    """
    Lit, resout et affiche un probleme de transport complet.
    algo : 'NO' (Nord-Ouest) ou 'BH' (Balas-Hammer).
    """
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
    afficher_proposition(n, m, A, prop_init, provisions, commandes,
                         base_set=base_init, label="PROPOSITION INITIALE")

    prop_opt, base_opt, cout_opt = marche_pied(
        n, m, A, prop_init, base_init, provisions, commandes)
    return prop_opt, base_opt, cout_opt

def menu_principal():
    print("\n" + "=" * 65)
    print("  RESOLUTION DE PROBLEMES DE TRANSPORT")
    print("  Efrei Paris - Recherche Operationnelle S6")
    print("=" * 65)

    while True:
        print("\nOptions :")
        print("  1. Resoudre un probleme depuis un fichier .txt")
        print("  2. Etude de complexite (generation aleatoire)")
        print("  0. Quitter")
        choix = input("\nVotre choix : ").strip()

        if choix == '0':
            print("Au revoir !")
            break
        elif choix == '1':
            fichier = input("Nom du fichier .txt : ").strip()
            print("Algorithme initial :")
            print("  1. Nord-Ouest")
            print("  2. Balas-Hammer")
            algo = 'NO' if input("Votre choix (1/2) : ").strip() == '1' else 'BH'
            try:
                resoudre_probleme(fichier, algo)
            except FileNotFoundError:
                print(f"  Fichier '{fichier}' introuvable.")
            except AssertionError as e:
                print(f"  Erreur dans les donnees : {e}")
            except Exception as e:
                print(f"  Erreur : {e}")
                import traceback; traceback.print_exc()
        elif choix == '2':
            etude_complexite()
        else:
            print("Choix invalide.")




if __name__ == '__main__':
    if len(sys.argv) >= 3:
        resoudre_probleme(sys.argv[1], sys.argv[2].upper())
    else:
        menu_principal()