"""
Point d'entrée principal du projet.
C'est ici qu'on instancie les différents composants (UI, Moteur) et qu'on lance le jeu.
"""
from ui import UI
from moteur import Moteur

if __name__ == "__main__":
    ui = UI()
    moteur = Moteur(ui)
    moteur.lancer()
