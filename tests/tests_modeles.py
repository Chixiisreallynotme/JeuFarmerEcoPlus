import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parent.parent))

from modele.espece import CATALOGUE, Espece
from modele.exploitation import Exploitation
from modele.parcelle import Parcelle
from moteur import Moteur
from ui import UI


def verifier_refus(action, *arguments):
    try:
        action(*arguments)
    except ValueError:
        return
    raise AssertionError("L'action aurait dû lever ValueError.")


def etat_ferme(ferme):
    parcelles = []
    for ligne in ferme.grille:
        for parcelle in ligne:
            parcelles.append(vars(parcelle).copy())
    return ferme.argent, ferme.eau, ferme.nourriture, parcelles


def executer_partie(saisies):
    moteur = Moteur(UI())
    sortie = StringIO()
    textes = [""] + [str(saisie) for saisie in saisies]
    with patch("builtins.input", side_effect=textes), redirect_stdout(sortie):
        moteur.lancer()
    return moteur, sortie.getvalue()


def test_catalogue():
    valeurs = [
        ("Blé", 2, 800, 2800, 20, 15, -8),
        ("Maïs", 3, 1500, 6500, 40, 30, -12),
        ("Pomme de terre", 3, 1200, 5000, 30, 20, -10),
        ("Carotte", 2, 600, 2200, 20, 10, -5),
        ("Radis", 1, 400, 1000, 15, 5, -3),
        ("Laitue", 1, 500, 1200, 30, 10, -5),
        ("Tomate", 3, 1400, 6000, 35, 25, -10),
        ("Courgette", 2, 1200, 4000, 35, 20, -8),
        ("Chou", 2, 1000, 3500, 30, 25, -10),
        ("Pois", 2, 600, 2000, 20, 0, 6),
        ("Haricot", 2, 700, 2400, 25, 0, 5),
        ("Fève", 3, 700, 3200, 20, 0, 8),
    ]
    assert len(CATALOGUE) == 12
    for espece, attendu in zip(CATALOGUE, valeurs):
        assert (espece.nom, espece.duree_croissance, espece.prix_graine,
                espece.rendement, espece.eau_min, espece.azote_min,
                espece.impact_azote) == attendu


def test_grille_et_coordonnees():
    ferme = Exploitation()
    assert (ferme.argent, ferme.eau, ferme.nourriture) == (10000, 100, 0)
    identifiants = []
    for y in range(1, 4):
        for x in range(1, 4):
            parcelle = ferme.get_parcelle(x, y)
            identifiants.append(id(parcelle))
            assert (parcelle.x, parcelle.y) == (x, y)
            assert (parcelle.humidite, parcelle.azote, parcelle.biodiversite) == (50, 60, 50)
            assert parcelle.espece is None and parcelle.derniere_espece is None
            assert parcelle.croissance == 0
    assert len(set(identifiants)) == 9
    assert ferme.get_parcelle(3, 2) is ferme.grille[1][2]
    for x, y in [(0, 1), (-1, 2), (4, 1), (1, 4), (1, 0), (1.5, 1), (True, 1), (1, "2")]:
        avant = etat_ferme(ferme)
        verifier_refus(ferme.get_parcelle, x, y)
        verifier_refus(ferme.planter, x, y, CATALOGUE[0])
        verifier_refus(ferme.arroser, x, y, 1)
        verifier_refus(ferme.recolter, x, y)
        assert etat_ferme(ferme) == avant


def test_plantation_et_refus():
    ferme = Exploitation()
    ble = CATALOGUE[0]
    ferme.planter(1, 1, ble)
    assert ferme.argent == 9200
    avant = etat_ferme(ferme)
    verifier_refus(ferme.planter, 1, 1, ble)
    assert etat_ferme(ferme) == avant
    ferme.argent = 799
    avant = etat_ferme(ferme)
    verifier_refus(ferme.planter, 2, 1, ble)
    assert etat_ferme(ferme) == avant
    ferme.argent = 800
    ferme.planter(2, 1, ble)
    assert ferme.argent == 0
    assert ferme.get_parcelle(1, 1).espece is ferme.get_parcelle(2, 1).espece is ble
    ferme.get_parcelle(1, 1).avancer_saison()
    assert ferme.get_parcelle(2, 1).croissance == 0


def test_arrosage():
    ferme = Exploitation()
    parcelle = ferme.get_parcelle(1, 1)
    for quantite in (0, -1, 1.5, "2", True, 51):
        avant = etat_ferme(ferme)
        verifier_refus(ferme.arroser, 1, 1, quantite)
        verifier_refus(parcelle.arroser, quantite)
        assert etat_ferme(ferme) == avant
    ferme.eau = 10
    avant = etat_ferme(ferme)
    verifier_refus(ferme.arroser, 1, 1, 11)
    assert etat_ferme(ferme) == avant
    ferme.arroser(1, 1, 10)
    assert (ferme.eau, parcelle.humidite) == (0, 60)
    ferme.eau = 40
    ferme.planter(1, 1, CATALOGUE[0])
    ferme.arroser(1, 1, 40)
    assert (ferme.eau, parcelle.humidite) == (0, 100)


def test_croissance_et_recolte_unique():
    ferme = Exploitation()
    ferme.planter(1, 1, CATALOGUE[0])
    parcelle = ferme.get_parcelle(1, 1)
    avant = etat_ferme(ferme)
    verifier_refus(ferme.recolter, 1, 1)
    assert etat_ferme(ferme) == avant
    ferme.avancer_saison()
    assert (parcelle.croissance, parcelle.humidite, parcelle.azote) == (1, 40, 52)
    assert not parcelle.est_mature()
    ferme.avancer_saison()
    assert parcelle.est_mature() and parcelle.azote == 44
    ferme.avancer_saison()
    assert (parcelle.croissance, parcelle.azote) == (2, 44)
    sol = parcelle.humidite, parcelle.azote, parcelle.biodiversite
    assert ferme.recolter(1, 1) == 2800 and ferme.nourriture == 2800
    assert parcelle.est_libre() and parcelle.croissance == 0
    assert parcelle.derniere_espece is CATALOGUE[0]
    assert (parcelle.humidite, parcelle.azote, parcelle.biodiversite) == sol
    avant = etat_ferme(ferme)
    verifier_refus(ferme.recolter, 1, 1)
    assert etat_ferme(ferme) == avant


def test_toutes_les_cultures():
    for espece in CATALOGUE:
        parcelle = Parcelle(1, 1)
        parcelle.planter(espece)
        for saison in range(espece.duree_croissance):
            parcelle.arroser(100 - parcelle.humidite)
            assert parcelle.avancer_saison() is None
            assert parcelle.croissance == saison + 1
        assert parcelle.est_mature()
        assert parcelle.recolter() == espece.rendement


def test_morts_et_priorite_des_causes():
    cas = [(0, 0, 0, "humidité insuffisante"),
           (80, 0, 0, "azote insuffisant"),
           (80, 60, 19, "biodiversité insuffisante")]
    for humidite, azote, biodiversite, cause in cas:
        parcelle = Parcelle(1, 1)
        parcelle.planter(CATALOGUE[1])
        parcelle.humidite = humidite
        parcelle.azote = azote
        parcelle.biodiversite = biodiversite
        assert parcelle.avancer_saison() == cause
        assert parcelle.est_libre() and parcelle.croissance == 0
        assert parcelle.derniere_espece is CATALOGUE[1]
        assert (parcelle.azote, parcelle.biodiversite) == (azote, biodiversite)
        assert parcelle.avancer_saison() is None
        assert (parcelle.azote, parcelle.biodiversite) == (azote + 10, biodiversite + 5)


def test_evolution_apres_une_mort():
    ferme = Exploitation()
    ferme.planter(1, 1, CATALOGUE[1])
    ferme.planter(2, 1, CATALOGUE[3])
    ferme.get_parcelle(1, 1).humidite = 0
    assert ferme.avancer_saison() == [(1, 1, "humidité insuffisante")]
    assert ferme.get_parcelle(2, 1).croissance == 1
    assert ferme.get_parcelle(3, 3).azote == 70
    assert (ferme.argent, ferme.eau, ferme.nourriture) == (8900, 120, 0)


def test_seuils_survie_et_plante_mature():
    parcelle = Parcelle(1, 1)
    parcelle.planter(CATALOGUE[0])
    parcelle.humidite = 10
    parcelle.azote = 15
    parcelle.biodiversite = 20
    assert parcelle.avancer_saison() is None
    assert (parcelle.croissance, parcelle.azote, parcelle.humidite) == (1, 7, 0)
    parcelle = Parcelle(1, 1)
    parcelle.planter(CATALOGUE[4])
    parcelle.avancer_saison()
    assert parcelle.est_mature()
    parcelle.humidite = 0
    assert parcelle.avancer_saison() == "humidité insuffisante"
    assert parcelle.est_libre()


def test_bornes_du_sol():
    parcelle = Parcelle(1, 1)
    parcelle.humidite, parcelle.azote, parcelle.biodiversite = 95, 95, 98
    parcelle.avancer_saison()
    assert (parcelle.humidite, parcelle.azote, parcelle.biodiversite) == (80, 100, 100)
    parcelle.planter(CATALOGUE[9])
    parcelle.avancer_saison()
    assert parcelle.azote == 100


def test_monoculture_rotation_et_jachere():
    parcelle = Parcelle(1, 1)
    radis = CATALOGUE[4]
    parcelle.planter(radis)
    parcelle.avancer_saison()
    parcelle.recolter()
    autre_radis = Espece("Radis", 1, 400, 1000, 15, 5, -3)
    parcelle.planter(autre_radis)
    assert parcelle.biodiversite == 40
    parcelle.avancer_saison()
    parcelle.recolter()
    parcelle.planter(CATALOGUE[9])
    assert parcelle.biodiversite == 40
    parcelle.avancer_saison()
    parcelle.avancer_saison()
    parcelle.recolter()
    azote = parcelle.azote
    parcelle.avancer_saison()
    assert parcelle.biodiversite == 45 and parcelle.azote == azote + 10
    parcelle.biodiversite = 5
    parcelle.planter(CATALOGUE[9])
    assert parcelle.biodiversite == 0


def test_vente_et_objectif_uml():
    ferme = Exploitation()
    ferme.nourriture = 2000
    for quantite in (0, -1, 2001, 1.5, "2", True):
        avant = etat_ferme(ferme)
        verifier_refus(ferme.vendre_nourriture, quantite)
        assert etat_ferme(ferme) == avant
    assert ferme.objectif_atteint(2000)
    assert not ferme.objectif_atteint(2001)
    assert ferme.vendre_nourriture(700) == 700
    assert (ferme.nourriture, ferme.argent) == (1300, 10700)
    assert ferme.vendre_nourriture(1300) == 1300
    assert (ferme.nourriture, ferme.argent) == (0, 12000)
    ferme.nourriture = 1
    assert ferme.vendre_nourriture(1) == 1
    assert (ferme.nourriture, ferme.argent) == (0, 12001)


def test_bilan_limites():
    moteur = Moteur(UI())
    moteur.bonus_recus = 12000
    moteur._donnees.argent = 22000
    assert moteur.bilan()["benefice"] == 0
    assert not moteur.bilan()["victoire"]
    moteur.recettes_ventes = 600
    moteur.depenses_graines = 600
    assert not moteur.bilan()["victoire"]
    moteur.recettes_ventes = 601
    assert moteur.bilan()["biodiversite"] == 50
    assert moteur.bilan()["victoire"]
    moteur._donnees.get_parcelle(1, 1).biodiversite = 49
    assert moteur.bilan()["biodiversite"] == 449 / 9
    assert not moteur.bilan()["victoire"]
    moteur.recettes_ventes = 0
    assert len(moteur.bilan()["raisons"]) == 2


def test_presentation_console():
    ui = UI()
    ferme = Exploitation()
    ferme.planter(1, 1, CATALOGUE[4])
    ferme.get_parcelle(1, 1).avancer_saison()
    ferme.planter(2, 1, CATALOGUE[2])
    ferme.get_parcelle(3, 1).humidite = 0
    ferme.get_parcelle(3, 1).azote = 100
    ferme.nourriture = 1
    avant = etat_ferme(ferme)
    sortie = StringIO()
    with patch("builtins.input", return_value="") as saisie, redirect_stdout(sortie):
        ui.afficher_accueil()
        ui.afficher_ferme(ferme, "Saison 1/12 : Printemps — année 1", Moteur(ui).bilan())
        ui.afficher_menu(False)
        ui.afficher_menu(True)
        ui.afficher_catalogue(CATALOGUE)
        ui.afficher_parcelle(ferme.get_parcelle(1, 1))
        ui.afficher_parcelle(ferme.get_parcelle(3, 1))
        ui.afficher_bilan(Moteur(ui).bilan())
    texte = sortie.getvalue()
    assert saisie.call_count == 1
    assert etat_ferme(ferme) == avant
    assert "JeuFarmerEcoPlus" in texte and "Objectif :" in texte
    assert "Appuyez sur Entrée" in saisie.call_args.args[0]
    assert "Sol au repos" in texte and "Croissance 0/3" in texte
    assert "Radis [M]" in texte and "Prête à récolter !" in texte
    assert "Seul [7] fait avancer le temps" in texte
    assert "[0] Terminer" in texte and "Pour survivre" in texte
    assert "[..........]   0 %" in texte and "[##########] 100 %" in texte
    assert "Nourriture : 0.001 t" in texte and "Eau : 100 m³" in texte
    assert "Argent : 8400 €" in texte
    for ligne in texte.splitlines():
        assert len(ligne) <= 78, ligne
        if ligne.startswith("    +") or (ligne.count("|") == 4 and ligne.endswith("|")):
            assert len(ligne) == 77, ligne


def test_tableau_compact_et_objectifs():
    ui = UI()
    moteur = Moteur(ui)
    moteur.recettes_ventes = 1400
    moteur._donnees.get_parcelle(1, 1).biodiversite = 41
    sortie = StringIO()
    with redirect_stdout(sortie):
        ui.afficher_ferme(moteur._donnees, "Saison 1/12 : Printemps — année 1", moteur.bilan())
        ui.afficher_menu(False)
    texte = sortie.getvalue()
    assert "  Bénéfice : +1400 € | Biodiversité : 49.00 %" in texte.splitlines()
    assert len(texte.splitlines()) <= 24
    for numero in range(1, 8):
        assert f"[{numero}]" in texte


def test_scenario_gagnant():
    saisies = [3, 1, 1, 10, 7, 7, 5, 1, 1, 6, 2000] + [7] * 10 + [8, 0]
    moteur, sortie = executer_partie(saisies)
    bilan = moteur.bilan()
    assert moteur.saisons_passees == 12 and bilan["bonus_recus"] == 12000
    assert bilan["depenses_graines"] == 600 and bilan["recettes_ventes"] == 2000
    assert bilan["benefice"] == 1400 and bilan["argent_final"] == 23400
    assert bilan["nourriture_recoltee"] == 2000 and bilan["nourriture_restante"] == 0
    assert bilan["biodiversite"] == 100 and bilan["victoire"]
    assert moteur._donnees.eau == 340
    assert sortie.count("Saison écoulée :") == 12
    assert "Printemps — année 1" in sortie and "Hiver — année 3" in sortie
    assert "Résultat définitif" in sortie and "Victoire" in sortie
    assert "Nourriture totale récoltée : 2.000 t" in sortie
    assert "Vente de 2000 kg : 2000 €" in sortie


def test_recolte_finale_et_limite_des_saisons():
    saisies = [7] * 11 + [3, 1, 1, 5, 4, 1, 1, 5, 7]
    saisies += [3, 4, 7, 5, 1, 1, 6, 1000, 8, 0]
    moteur, sortie = executer_partie(saisies)
    assert moteur.saisons_passees == 12 and moteur.bonus_recus == 12000
    assert moteur.nourriture_recoltee == 1000 and moteur.recettes_ventes == 1000
    assert moteur.bilan()["benefice"] == 600 and moteur._donnees.argent == 22600
    assert sortie.count("Saison écoulée :") == 12
    assert sortie.count("Choix indisponible pendant la phase finale.") == 3
    assert "[2]" not in sortie.split("Phase finale", 1)[1]
    avant = etat_ferme(moteur._donnees)
    verifier_refus(moteur.passer_saison)
    assert etat_ferme(moteur._donnees) == avant and moteur.bonus_recus == 12000


def test_saisies_et_actions_refusees():
    saisies = ["abc", 99, 1, 2, 0, 1, 3, 1, 1, 0]
    saisies += [3, 1, 1, 10, 3, 1, 1, 10, 5, 1, 1, 4, 1, 1, 0, 6, 1]
    moteur, sortie = executer_partie(saisies + [7] * 12 + [0])
    assert "Saisissez un nombre entier." in sortie
    assert "coordonnées" in sortie and "déjà occupée" in sortie
    assert "encore mature" in sortie and "stock de nourriture" in sortie
    assert "Culture morte en (1, 1) : humidité insuffisante." in sortie
    assert moteur.depenses_graines == 600 and moteur.nourriture_recoltee == 0
    assert moteur.recettes_ventes == 0 and moteur._donnees.argent == 21400
    assert moteur._donnees.eau == 340 and moteur.saisons_passees == 12


if __name__ == "__main__":
    tests = [test_catalogue, test_grille_et_coordonnees, test_plantation_et_refus,
             test_arrosage, test_croissance_et_recolte_unique, test_toutes_les_cultures,
             test_morts_et_priorite_des_causes, test_evolution_apres_une_mort,
             test_seuils_survie_et_plante_mature, test_bornes_du_sol,
             test_monoculture_rotation_et_jachere, test_vente_et_objectif_uml,
             test_bilan_limites, test_presentation_console, test_tableau_compact_et_objectifs,
             test_scenario_gagnant,
             test_recolte_finale_et_limite_des_saisons, test_saisies_et_actions_refusees]
    for test in tests:
        test()
    print(f"{len(tests)} tests réussis.")
