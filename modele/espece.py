class Espece:
    def __init__(self, nom, duree_croissance, prix_graine, rendement,
                 eau_min, azote_min, impact_azote):
        self.nom = nom
        self.duree_croissance = duree_croissance
        self.prix_graine = prix_graine  # euros de semences par parcelle
        self.rendement = rendement  # kg récoltés par parcelle
        self.eau_min = eau_min
        self.azote_min = azote_min
        self.impact_azote = impact_azote


CATALOGUE = [
    Espece("Blé", 2, 800, 2800, 20, 15, -8),
    Espece("Maïs", 3, 1500, 6500, 40, 30, -12),
    Espece("Pomme de terre", 3, 1200, 5000, 30, 20, -10),
    Espece("Carotte", 2, 600, 2200, 20, 10, -5),
    Espece("Radis", 1, 400, 1000, 15, 5, -3),
    Espece("Laitue", 1, 500, 1200, 30, 10, -5),
    Espece("Tomate", 3, 1400, 6000, 35, 25, -10),
    Espece("Courgette", 2, 1200, 4000, 35, 20, -8),
    Espece("Chou", 2, 1000, 3500, 30, 25, -10),
    Espece("Pois", 2, 600, 2000, 20, 0, 6),
    Espece("Haricot", 2, 700, 2400, 25, 0, 5),
    Espece("Fève", 3, 700, 3200, 20, 0, 8),
]
