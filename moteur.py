from modele.espece import CATALOGUE
from modele.exploitation import Exploitation


SAISONS = ("Printemps", "Été", "Automne", "Hiver")
NOMBRE_SAISONS = 12


class Moteur:
    def __init__(self, ui):
        self._ui = ui
        self._donnees = Exploitation()
        self.saisons_passees = 0
        self.depenses_graines = 0
        self.recettes_ventes = 0
        self.nourriture_recoltee = 0
        self.bonus_recus = 0

    def planter(self):
        x, y = self._ui.demander_coordonnees()
        self._ui.afficher_catalogue(CATALOGUE)
        choix = self._ui.demander_entier("Numéro de la culture : ")
        if not 1 <= choix <= len(CATALOGUE):
            raise ValueError("Ce numéro de culture n'existe pas.")
        espece = CATALOGUE[choix - 1]
        self._donnees.planter(x, y, espece)
        self.depenses_graines += espece.prix_graine
        self._ui.afficher_texte(f"{espece.nom} planté : {espece.prix_graine} € de semences.")

    def arroser(self):
        x, y = self._ui.demander_coordonnees()
        quantite = self._ui.demander_entier("Volume d'eau (m³, entier) : ")
        self._donnees.arroser(x, y, quantite)
        self._ui.afficher_texte(f"Parcelle arrosée avec {quantite} m³ d'eau.")

    def recolter(self):
        x, y = self._ui.demander_coordonnees()
        quantite = self._donnees.recolter(x, y)
        self.nourriture_recoltee += quantite
        self._ui.afficher_texte(f"Récolte : {quantite} kg de nourriture.")

    def vendre(self):
        self._ui.afficher_texte(f"Stock disponible : {self._donnees.nourriture} kg. Prix : 1 €/kg.")
        quantite = self._ui.demander_entier("Masse à vendre (kg, entier) : ")
        recette = self._donnees.vendre_nourriture(quantite)
        self.recettes_ventes += recette
        self._ui.afficher_texte(f"Vente de {quantite} kg : {recette} € reçus.")

    def passer_saison(self):
        if self.saisons_passees >= NOMBRE_SAISONS:
            raise ValueError("Les 12 saisons sont terminées.")
        morts = self._donnees.avancer_saison()
        self.saisons_passees += 1
        self.bonus_recus += 1000
        self._ui.afficher_texte("Saison écoulée : +20 m³ d'eau et +1000 € de bonus.")
        for x, y, cause in morts:
            self._ui.afficher_texte(f"Culture morte en ({x}, {y}) : {cause}.")

    def bilan(self):
        total_biodiversite = 0
        for ligne in self._donnees.grille:
            for parcelle in ligne:
                total_biodiversite += parcelle.biodiversite
        biodiversite = total_biodiversite / 9
        benefice = self.recettes_ventes - self.depenses_graines
        raisons = []
        if benefice <= 0:
            raisons.append("Le bénéfice agricole doit être strictement positif.")
        if biodiversite < 50:
            raisons.append("La biodiversité moyenne doit atteindre 50 %.")
        return {
            "nourriture_recoltee": self.nourriture_recoltee,
            "nourriture_restante": self._donnees.nourriture,
            "recettes_ventes": self.recettes_ventes,
            "depenses_graines": self.depenses_graines,
            "bonus_recus": self.bonus_recus,
            "argent_final": self._donnees.argent,
            "benefice": benefice,
            "biodiversite": biodiversite,
            "victoire": len(raisons) == 0,
            "raisons": raisons,
        }

    def lancer(self):
        self._ui.afficher_accueil()
        while True:
            finale = self.saisons_passees == NOMBRE_SAISONS
            if finale:
                periode = "Phase finale — 12 saisons écoulées (3 ans)"
            else:
                nom = SAISONS[self.saisons_passees % 4]
                annee = self.saisons_passees // 4 + 1
                periode = f"Saison {self.saisons_passees + 1}/12 : {nom} — année {annee}"
            self._ui.afficher_ferme(self._donnees, periode, self.bilan())
            self._ui.afficher_menu(finale)
            choix = self._ui.demander_entier("  Votre choix > ")
            try:
                if finale and choix not in (0, 5, 6, 8):
                    raise ValueError("Choix indisponible pendant la phase finale.")
                if choix == 0 and finale:
                    break
                elif choix == 1:
                    self._ui.afficher_catalogue(CATALOGUE)
                elif choix == 2:
                    x, y = self._ui.demander_coordonnees()
                    self._ui.afficher_parcelle(self._donnees.get_parcelle(x, y))
                elif choix == 3:
                    self.planter()
                elif choix == 4:
                    self.arroser()
                elif choix == 5:
                    self.recolter()
                elif choix == 6:
                    self.vendre()
                elif choix == 7:
                    self.passer_saison()
                elif choix == 8 and finale:
                    self._ui.afficher_bilan(self.bilan())
                else:
                    raise ValueError("Choisissez un numéro du menu.")
            except ValueError as erreur:
                self._ui.afficher_texte(f"Action refusée : {erreur}")
        self._ui.afficher_texte("\nRésultat définitif")
        self._ui.afficher_bilan(self.bilan())
