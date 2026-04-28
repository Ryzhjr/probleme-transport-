"""
=============================================================
  FICHIER : main.py
  RÔLE    : Point d'entrée du programme — Structure globale
  SECTION : 2.2 du projet
=============================================================

STRUCTURE GLOBALE (pseudo-code du projet) :
    Tant que l'utilisateur veut tester un problème :
        1. Choisir le numéro du problème
        2. Lire le fichier .txt et stocker en mémoire
        3. Afficher la matrice des coûts
        4. Choisir l'algorithme de proposition initiale (NO ou BH)
        5. Exécuter l'algorithme choisi et afficher la proposition
        6. Dérouler le marche-pied avec potentiel :
            - Afficher proposition + coût
            - Tester dégénérescence (cycle / non-connexe)
            - Corriger si besoin
            - Calculer et afficher les potentiels
            - Afficher coûts potentiels et marginaux
            - Si non optimal → ajouter arête améliorante + nouvelle itération
            - Sinon → sortir
        7. Afficher la solution optimale
        8. Proposer de changer de problème
    Fin
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
# Import de tous les modules du projet
from lecteur       import lire_probleme
from utilitaires   import (afficher_matrice_couts,
                                afficher_proposition,
                                afficher_couts_potentiels,
                                afficher_couts_marginaux,
                                calculer_cout_total)
from nord_ouest    import nord_ouest
from balas_hammer  import balas_hammer
from marche_pied   import marche_pied


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────

# Dossier contenant les fichiers .txt des problèmes
DOSSIER_DONNEES = "donnees"

# Nombre de problèmes disponibles dans les annexes
NB_PROBLEMES = 12


# ─────────────────────────────────────────────────────────────────────────────
# FONCTIONS D'INTERFACE
# ─────────────────────────────────────────────────────────────────────────────

def afficher_banniere():
    """Affiche le titre du programme au lancement."""
    print("=" * 62)
    print("   PROJET RECHERCHE OPÉRATIONNELLE — EFREI PARIS S6")
    print("   Méthode du marche-pied avec potentiel")
    print("   Algorithmes : Nord-Ouest & Balas-Hammer")
    print("=" * 62)


def choisir_probleme():
    """
    Demande à l'utilisateur de choisir un numéro de problème (1 à 12).

    Retourne :
        num_probleme (int) : numéro du problème choisi
        ou None si l'utilisateur veut quitter
    """
    print(f"\n  Problèmes disponibles : 1 à {NB_PROBLEMES}")
    print(f"  Tapez [q] pour quitter\n")

    while True:
        saisie = input("  → Numéro du problème : ").strip().lower()

        # L'utilisateur veut quitter
        if saisie == 'q':
            return None

        # Vérifier que c'est un entier valide dans [1, NB_PROBLEMES]
        if saisie.isdigit():
            num = int(saisie)
            if 1 <= num <= NB_PROBLEMES:
                return num

        # Saisie invalide
        print(f"  ⚠ Saisie invalide. Entrez un entier entre 1 "
              f"et {NB_PROBLEMES}.")


def choisir_algorithme():
    """
    Demande à l'utilisateur de choisir l'algorithme de proposition initiale.

    Retourne :
        'NO' pour Nord-Ouest
        'BH' pour Balas-Hammer
    """
    print("\n  Algorithme de proposition initiale :")
    print("    [1]  Nord-Ouest  (NO) — rapide, ignore les coûts")
    print("    [2]  Balas-Hammer (BH) — plus lent, tient compte des coûts")

    while True:
        saisie = input("  → Votre choix [1/2] : ").strip()

        if saisie == '1':
            return 'NO'
        elif saisie == '2':
            return 'BH'
        else:
            print("  ⚠ Saisie invalide. Tapez 1 ou 2.")


def construire_chemin_fichier(num_probleme):
    """
    Construit le chemin vers le fichier .txt du problème.

    Exemple : num=5 → "donnees/probleme5.txt"
    """
    nom_fichier = f"probleme{num_probleme}.txt"
    chemin = os.path.join(DOSSIER_DONNEES, nom_fichier)
    return chemin


def verifier_fichier(chemin):
    """
    Vérifie que le fichier existe et est accessible.

    Retourne True si ok, False sinon.
    """
    if not os.path.exists(chemin):
        print(f"\n  ⚠ Fichier introuvable : '{chemin}'")
        print(f"  Vérifiez que le fichier .txt est bien dans "
              f"le dossier '{DOSSIER_DONNEES}/'")
        return False
    return True


def demander_continuer():
    """
    Demande à l'utilisateur s'il veut tester un autre problème.

    Retourne True pour continuer, False pour quitter.
    """
    print("\n" + "─" * 62)
    saisie = input("  Tester un autre problème ? [o/n] : ").strip().lower()
    return saisie in ('o', 'oui', 'y', 'yes', '1')


# ─────────────────────────────────────────────────────────────────────────────
# RÉSOLUTION D'UN PROBLÈME (cœur du programme)
# ─────────────────────────────────────────────────────────────────────────────

def resoudre_un_probleme(num_probleme, algo):
    """
    Résout un problème de transport de bout en bout.

    Étapes :
        1. Lecture du fichier .txt
        2. Affichage de la matrice des coûts
        3. Proposition initiale (NO ou BH)
        4. Affichage de la proposition initiale
        5. Marche-pied avec potentiel
        6. Affichage de la solution optimale

    Paramètres :
        num_probleme (int) : numéro du problème (1 à 12)
        algo         (str) : 'NO' ou 'BH'

    Retourne :
        cout_optimal (int) : coût de la solution optimale
    """

    # ── Étape 1 : Lecture du fichier ──────────────────────────────────────────
    chemin = construire_chemin_fichier(num_probleme)

    print(f"\n{'═'*62}")
    print(f"  PROBLÈME {num_probleme}  |  Algorithme : {algo}")
    print(f"  Fichier : {chemin}")
    print(f"{'═'*62}")

    n, m, cout, provisions, commandes = lire_probleme(chemin)

    print(f"\n  Dimensions : {n} fournisseur(s) × {m} client(s)")

    # ── Étape 2 : Affichage de la matrice des coûts ───────────────────────────
    afficher_matrice_couts(n, m, cout, provisions, commandes)

    # ── Étape 3 : Proposition initiale ───────────────────────────────────────
    if algo == 'NO':
        # Algorithme Nord-Ouest
        # On passe des COPIES de provisions et commandes
        # car l'algo les modifie (décrémente au fil des allocations)
        transport, base = nord_ouest(n, m, provisions[:], commandes[:])

    else:
        # Algorithme Balas-Hammer
        transport, base = balas_hammer(n, m, cout,
                                       provisions[:], commandes[:])

    # ── Étape 4 : Affichage de la proposition initiale ───────────────────────
    afficher_proposition(
        n, m, transport, base, provisions, commandes, cout,
        titre=f"PROPOSITION INITIALE ({algo})"
    )

    # ── Étape 5 : Marche-pied avec potentiel ─────────────────────────────────
    # C'est ici que se fait toute l'optimisation
    transport, base, cout_optimal = marche_pied(
        n, m, cout, transport, base, provisions, commandes,
        verbose=True
    )

    return cout_optimal


# ─────────────────────────────────────────────────────────────────────────────
# MENU PRINCIPAL (boucle principale)
# ─────────────────────────────────────────────────────────────────────────────

def menu_principal():
    """
    Boucle principale du programme.
    Permet de tester plusieurs problèmes à la suite.

    Correspond au pseudo-code de la section 2.2 :
        Tant que l'utilisateur veut tester un problème → résoudre
    """

    afficher_banniere()

    # Tableau récapitulatif des résultats (pour affichage final)
    resultats = []   # liste de tuples (num_pb, algo, coût_optimal)

    continuer = True

    while continuer:

        print("\n" + "─" * 62)
        print("  MENU PRINCIPAL")
        print("─" * 62)
        print("  [1-12]  Résoudre un problème de transport")
        print("  [r]     Afficher le récapitulatif des résultats")
        print("  [q]     Quitter")

        saisie = input("\n  → Votre choix : ").strip().lower()

        # ── Quitter ───────────────────────────────────────────────────────────
        if saisie == 'q':
            continuer = False

        # ── Récapitulatif ─────────────────────────────────────────────────────
        elif saisie == 'r':
            afficher_recapitulatif(resultats)

        # ── Résoudre un problème ──────────────────────────────────────────────
        elif saisie.isdigit() and 1 <= int(saisie) <= NB_PROBLEMES:
            num = int(saisie)
            chemin = construire_chemin_fichier(num)

            # Vérifier que le fichier existe avant de continuer
            if not verifier_fichier(chemin):
                continue

            # Choisir l'algorithme
            algo = choisir_algorithme()

            # Résoudre le problème
            try:
                cout_opt = resoudre_un_probleme(num, algo)
                # Mémoriser le résultat
                resultats.append((num, algo, cout_opt))

            except Exception as e:
                print(f"\n  ⚠ Erreur lors de la résolution : {e}")
                import traceback
                traceback.print_exc()

        else:
            print("  ⚠ Saisie invalide.")

    # ── Fin du programme ──────────────────────────────────────────────────────
    if resultats:
        afficher_recapitulatif(resultats)

    print("\n  Au revoir !\n")


# ─────────────────────────────────────────────────────────────────────────────
# RÉCAPITULATIF FINAL
# ─────────────────────────────────────────────────────────────────────────────

def afficher_recapitulatif(resultats):
    """
    Affiche un tableau récapitulatif de tous les problèmes résolus
    avec leur algorithme et leur coût optimal.

    Exemple :
        ╔══ RÉCAPITULATIF ══╗
          Pb   Algo   Coût optimal
          ─────────────────────────
           1    NO        3 000
           1    BH        3 000
           5    BH          425
    """
    if not resultats:
        print("\n  Aucun problème résolu pour l'instant.")
        return

    print("\n╔══ RÉCAPITULATIF DES RÉSULTATS ══╗")
    print(f"  {'Pb':>4}  {'Algo':>6}  {'Coût optimal':>15}")
    print("  " + "─" * 30)
    for num, algo, cout in resultats:
        print(f"  {num:>4}  {algo:>6}  {cout:>15}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# MODE LIGNE DE COMMANDE
# ─────────────────────────────────────────────────────────────────────────────

def mode_cli():
    """
    Mode ligne de commande pour lancer directement un problème :

    Usage :
        python main.py <num_probleme> <algo>

    Exemples :
        python main.py 5 NO     → résout problème 5 avec Nord-Ouest
        python main.py 12 BH    → résout problème 12 avec Balas-Hammer
    """
    num  = int(sys.argv[1])
    algo = sys.argv[2].upper() if len(sys.argv) >= 3 else 'NO'

    if algo not in ('NO', 'BH'):
        print("  ⚠ Algorithme invalide. Utilisez 'NO' ou 'BH'.")
        sys.exit(1)

    chemin = construire_chemin_fichier(num)
    if not verifier_fichier(chemin):
        sys.exit(1)

    resoudre_un_probleme(num, algo)


# ─────────────────────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    if len(sys.argv) >= 2:
        # Mode CLI : python main.py 5 NO
        mode_cli()
    else:
        # Mode interactif : python main.py
        menu_principal()