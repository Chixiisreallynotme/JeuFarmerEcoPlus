class UI:
    def afficher_accueil(self):
        self.afficher_texte(r"""
       ### ### # # ###  #  ##  # # ### ##  ### ### ### ##  #   # # ###
         # #   # # #   # # # # ### #   # # #   #   # # # # #   # # #  
         # ##  # # ##  ### ##  ### ##  ##  ##  #   # # ##  #   # # ###
       # # #   # # #   # # # # # # #   # # #   #   # # #   #   # #   #
       ### ### ### #   # # # # # # ### # # ### ### ### #   ### ### ###
""")
        self.afficher_texte(
            "  9 parcelles | 12 saisons | 3 ans\n"
            "  Objectif : bénéfice > 0 € et biodiversité moyenne >= 50 %.\n")
        self.demander_texte("  Appuyez sur Entrée pour jouer...")

    def afficher_texte(self, texte):
        print(texte)

    def demander_texte(self, message="Votre choix : "):
        return input(message)

    def demander_entier(self, message):
        while True:
            try:
                return int(self.demander_texte(message))
            except ValueError:
                self.afficher_texte("  [!] Saisissez un nombre entier. Validez avec Entrée.")

    def demander_coordonnees(self):
        self.afficher_texte("\n  Choisissez une parcelle : colonne x, puis ligne y.")
        x = self.demander_entier("Colonne x (1 à 3) : ")
        y = self.demander_entier("Ligne y (1 à 3) : ")
        return x, y

    def afficher_ferme(self, exploitation, periode, bilan):
        self.afficher_texte("\n" + "=" * 78)
        self.afficher_texte(f"  JeuFarmerEcoPlus | {periode}")
        self.afficher_texte(
            f"  Argent : {exploitation.argent} € | Eau : {exploitation.eau} m³ "
            f"| Nourriture : {exploitation.nourriture / 1000:.3f} t")
        self.afficher_texte(
            f"  Bénéfice : {bilan['benefice']:+} € | "
            f"Biodiversité : {bilan['biodiversite']:.2f} %")
        self.afficher_texte("     " + " ".join(f"{x:^23}" for x in range(1, 4)))
        bordure = "    +" + ("-" * 23 + "+") * 3
        self.afficher_texte(bordure)
        for ligne in exploitation.grille:
            cases = []
            etats = []
            for parcelle in ligne:
                if parcelle.est_libre():
                    texte = "Vide"
                    etat = "Sol au repos"
                elif parcelle.est_mature():
                    texte = f"{parcelle.espece.nom} [M]"
                    etat = "Prête à récolter !"
                else:
                    texte = parcelle.espece.nom
                    etat = f"Croissance {parcelle.croissance}/{parcelle.espece.duree_croissance}"
                cases.append(f"{texte:^23}")
                etats.append(f"{etat:^23}")
            self.afficher_texte(f" {ligne[0].y}  |" + "|".join(cases) + "|")
            self.afficher_texte("    |" + "|".join(etats) + "|")
            self.afficher_texte(bordure)
        self.afficher_texte("  x = colonne, y = ligne. [M] = récolte prête.")

    def afficher_menu(self, finale):
        if finale:
            self.afficher_texte(
                "  DERNIÈRES RÉCOLTES | Les 12 saisons sont terminées.\n"
                "  [5] Récolter                  [6] Vendre\n"
                "  [8] Consulter le bilan        [0] Terminer\n"
                "  Vendez vos dernières récoltes avant de demander le résultat définitif.")
        else:
            self.afficher_texte(
                "  OBSERVER                  CULTIVER                 GÉRER\n"
                "  [1] Catalogue             [3] Planter              [5] Récolter\n"
                "  [2] Parcelle et sol       [4] Arroser              [6] Vendre\n"
                "  [7] Passer la saison      +20 m³ d'eau, +1000 € ; les cultures évoluent.\n"
                "  Seul [7] fait avancer le temps. Plusieurs actions sont possibles.")
        self.afficher_texte("-" * 78)

    def afficher_catalogue(self, catalogue):
        self.afficher_texte("\n" + "=" * 78)
        self.afficher_texte("  LE CATALOGUE | Choisissez ce que vous voulez cultiver")
        self.afficher_texte("-" * 78)
        self.afficher_texte(
            f"{'N°':>3} {'Culture':<16} {'Sais.':>5} {'Prix €':>8} {'Récolte t':>10} "
            f"{'Eau %':>6} {'Azote %':>8} {'Effet azote':>12}")
        self.afficher_texte("-" * 78)
        for numero, espece in enumerate(catalogue, 1):
            self.afficher_texte(
                f"{numero:>3} {espece.nom:<16} {espece.duree_croissance:>5} "
                f"{espece.prix_graine:>8} {espece.rendement / 1000:>10.3f} "
                f"{espece.eau_min:>6} {espece.azote_min:>8} {espece.impact_azote:+12}")
        self.afficher_texte("-" * 78)
        self.afficher_texte(
            "  Prix = semences pour une parcelle ; récolte en tonnes (1 t = 1000 kg).\n"
            "  Eau / azote = seuils du sol en % ; effet azote en points par croissance.\n"
            "  Vente au tarif fixe du jeu : 1 €/kg, soit 1000 €/t.")

    def afficher_parcelle(self, parcelle):
        self.afficher_texte("\n" + "=" * 78)
        self.afficher_texte(f"  VOTRE SOL | Parcelle ({parcelle.x}, {parcelle.y})")
        self.afficher_texte("-" * 78)
        if parcelle.est_libre():
            self.afficher_texte("Parcelle vide, au repos.")
        else:
            etat = "mature" if parcelle.est_mature() else "en croissance"
            self.afficher_texte(
                f"{parcelle.espece.nom} : {parcelle.croissance}/"
                f"{parcelle.espece.duree_croissance} ({etat})")
        for nom, valeur in (("Humidité", parcelle.humidite),
                            ("Azote", parcelle.azote),
                            ("Biodiversité", parcelle.biodiversite)):
            remplis = valeur // 10
            jauge = "#" * remplis + "." * (10 - remplis)
            self.afficher_texte(f"  {nom:<13} [{jauge}] {valeur:>3} %")
        if not parcelle.est_libre():
            self.afficher_texte(
                f"\n  Pour survivre : humidité >= {parcelle.espece.eau_min} %, "
                f"azote >= {parcelle.espece.azote_min} %,\n"
                "  et biodiversité >= 20 %. La pluie arrive avant cette vérification.")
        derniere = "aucune" if parcelle.derniere_espece is None else parcelle.derniere_espece.nom
        self.afficher_texte(f"Dernière espèce plantée : {derniere}")
        self.afficher_texte("-" * 78)
        self.afficher_texte("  Au repos : +10 points d'azote et +5 de biodiversité par saison.")
        self.afficher_texte("  Arrosage : 1 m³ ajoute 1 point d'humidité, avec un plafond de 100 %.")

    def afficher_bilan(self, bilan):
        self.afficher_texte("\n" + "=" * 78)
        self.afficher_texte("  BILAN DE VOTRE EXPLOITATION")
        self.afficher_texte("-" * 78)
        self.afficher_texte("  RÉCOLTES ET ÉCONOMIE\n")
        self.afficher_texte(f"Nourriture totale récoltée : {bilan['nourriture_recoltee'] / 1000:.3f} t")
        self.afficher_texte(f"Nourriture restante : {bilan['nourriture_restante'] / 1000:.3f} t")
        self.afficher_texte(f"Recettes des ventes : {bilan['recettes_ventes']} €")
        self.afficher_texte(f"Dépenses en semences : {bilan['depenses_graines']} €")
        self.afficher_texte(f"Bonus saisonniers reçus : {bilan['bonus_recus']} €")
        self.afficher_texte(f"Argent final : {bilan['argent_final']} €")
        self.afficher_texte(f"Bénéfice agricole (ventes - semences) : {bilan['benefice']} €")
        self.afficher_texte(f"Biodiversité moyenne : {bilan['biodiversite']:.2f} %")
        self.afficher_texte("\n  Les bonus sont exclus du bénéfice ; le stock non vendu ne rapporte rien.")
        self.afficher_texte("-" * 78)
        if bilan["victoire"]:
            self.afficher_texte("Victoire : bénéfice positif et biodiversité moyenne d'au moins 50 %.")
        else:
            self.afficher_texte("Défaite :")
            for raison in bilan["raisons"]:
                self.afficher_texte(f"- {raison}")
        self.afficher_texte("=" * 78)

