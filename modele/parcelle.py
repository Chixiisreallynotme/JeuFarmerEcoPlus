class Parcelle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.espece = None
        self.croissance = 0
        self.humidite = 50
        self.azote = 60
        self.biodiversite = 50
        self.derniere_espece = None

    def est_libre(self):
        return self.espece is None

    def planter(self, espece):
        if not self.est_libre():
            raise ValueError("Cette parcelle est déjà occupée.")
        if self.derniere_espece is not None:
            if self.derniere_espece.nom == espece.nom:
                self.biodiversite = max(0, self.biodiversite - 10)
        self.espece = espece
        self.croissance = 0
        self.derniere_espece = espece

    def arroser(self, quantite):
        if type(quantite) is not int or quantite <= 0:
            raise ValueError("Le volume d'eau doit être un entier positif en m³.")
        if quantite > 100 - self.humidite:
            raise ValueError("Cette quantité dépasserait 100 % d'humidité.")
        self.humidite += quantite  # Convention du jeu : 1 m³ ajoute 1 point.

    def avancer_saison(self):
        self.humidite = min(100, self.humidite + 10)
        cause = None
        if self.est_libre():
            self.azote = min(100, self.azote + 10)
            self.biodiversite = min(100, self.biodiversite + 5)
        else:
            if self.humidite < self.espece.eau_min:
                cause = "humidité insuffisante"
            elif self.azote < self.espece.azote_min:
                cause = "azote insuffisant"
            elif self.biodiversite < 20:
                cause = "biodiversité insuffisante"
            if cause is not None:
                self.espece = None
                self.croissance = 0
            elif not self.est_mature():
                self.croissance += 1
                self.azote = max(0, min(100, self.azote + self.espece.impact_azote))
        self.humidite = max(0, self.humidite - 20)
        return cause

    def est_mature(self):
        return (self.espece is not None
                and self.croissance >= self.espece.duree_croissance)

    def recolter(self):
        if self.est_libre():
            raise ValueError("Cette parcelle est vide.")
        if not self.est_mature():
            raise ValueError("Cette culture n'est pas encore mature.")
        quantite = self.espece.rendement
        self.espece = None
        self.croissance = 0
        return quantite
