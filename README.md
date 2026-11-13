# JeuFarmerEcoPlus — Agro-simulateur écologique, Terminale NSI

Un jeu console pour cultiver neuf parcelles pendant douze saisons, soit trois ans.
Il faut vendre ses récoltes tout en préservant la biodiversité du sol.
Les chiffres sont des réglages de jeu, pas une simulation exacte de l'agriculture réelle.

## Lancement et tests

Python 3, sans bibliothèque externe. Depuis le dossier contenant `main.py`,
pour jouer, une seule commande :

```console
python main.py
```

Pour vérifier le projet, les tests sont facultatifs pour jouer :

```console
python tests/tests_modeles.py
```

Si l'alias `python` est inaccessible, utiliser le chemin de l'interpréteur
installé. Sur la machine de vérification, les commandes PowerShell sont :

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe" main.py
& "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe" tests/tests_modeles.py
```

Ne pas lancer les tests avec `python -O`, car cette option désactive les `assert`.
Le fichier de tests vérifie le modèle et joue des parties avec les vraies saisies
et les vrais affichages de l'interface, en fournissant automatiquement les réponses.

## Prendre en main le jeu

L'accueil affiche le logo JeuFarmerEcoPlus en ASCII, la durée et l'objectif de la
partie. Appuyer sur Entrée pour jouer.
Le tableau de jeu et son menu tiennent sur 24 lignes, avant la saisie : prévoir
une console de 78 colonnes et 25 lignes, avec une police à chasse fixe.
Le bénéfice agricole et la biodiversité moyenne restent visibles.
Les actions sont regroupées : observer, cultiver et gérer.

Le menu propose : 1 catalogue, 2 état d'une parcelle, 3 planter, 4 arroser,
5 récolter, 6 vendre et 7 passer la saison. Une parcelle se choisit par
`x = colonne`, puis `y = ligne`, avec des coordonnées de 1 à 3.

La grille encadrée affiche le nom de la culture et son état : `Vide` et
`Sol au repos` pour une jachère, `Croissance n/d` pour une plante en croissance,
et `nom [M]` avec `Prête à récolter !` pour une plante mature.
La consultation d'une parcelle montre son humidité, son azote et sa biodiversité
avec des jauges ASCII et leurs valeurs exactes, ainsi que la dernière espèce
plantée et les conditions de survie de la culture présente.
Les saisons suivent l'ordre Printemps, Été, Automne, Hiver, répété trois fois.

Parcours simple : **planter → passer une saison → récolter → vendre**.
La plantation achète directement les semences pour une parcelle. Il faut passer autant de saisons
que la durée de la culture avant de récolter : un radis demande une évolution,
des pois en demandent deux. La récolte rejoint le stock global de nourriture ;
la vente transforme ensuite ce stock en argent.

Seul le choix 7 fait avancer le temps. Les autres actions peuvent être répétées
dans la même saison. Une saisie incorrecte permet de réessayer ; une action
refusée ne consomme rien et ne modifie pas la ferme. Une réserve vide ne met
pas fin à la partie.

Après la douzième évolution, le menu final permet seulement de récolter (5),
vendre (6), consulter le bilan (8) ou terminer (0). Il permet notamment de
récolter les plantes devenues matures à la dernière évolution. Terminer affiche
le résultat définitif, même s'il reste des plantes ou de la nourriture.

## Unités et état initial

- Ferme : 10 000 €, 100 m³ d'eau, 0 t de nourriture et une grille de 3 × 3.
- Chaque parcelle : humidité 50 %, azote 60 %, biodiversité 50 %, aucune
  espèce active ou précédente, croissance 0.
- Les trois paramètres du sol restent entre 0 et 100. La réserve d'eau de la
  ferme est distincte de l'humidité du sol et n'a pas de plafond.

Dans le modèle, l'argent est un nombre entier d'euros, l'eau un nombre entier
de mètres cubes et la nourriture un nombre entier de kilogrammes. Le catalogue,
le tableau de la ferme et le bilan affichent les masses en tonnes :
**1 t = 1 000 kg**. Les confirmations de récolte et le stock avant vente sont
affichés en kilogrammes. Les ventes se saisissent en kilogrammes entiers
et les arrosages en mètres cubes entiers.
Une unité de masse affichée de 0,001 t correspond donc exactement à 1 kg.

Les paramètres du sol sont des indices sur 100, affichés en pourcentages.
Leurs variations se mesurent en points. La convention d'arrosage du jeu est
**1 m³ = +1 point d'humidité** ; 1 m³ représente 1 000 litres d'eau.
Ces choix donnent des unités cohérentes au jeu sans constituer un modèle
agronomique calibré sur une surface réelle de parcelle.

## Catalogue

Le prix couvre les semences pour une parcelle. Le rendement est la masse
récoltée par parcelle, affichée en tonnes et stockée en kilogrammes dans le
modèle. L'eau minimale est un seuil d'humidité du sol,
pas un prélèvement sur la réserve. L'impact sur l'azote s'applique à chaque
progression réelle de croissance. Toutes les cultures sont disponibles en toute saison.

| Culture | Durée (saisons) | Semences (€) | Récolte (t) | Humidité min (%) | Azote min (%) | Impact azote (points) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Blé | 2 | 800 | 2,8 | 20 | 15 | -8 |
| Maïs | 3 | 1 500 | 6,5 | 40 | 30 | -12 |
| Pomme de terre | 3 | 1 200 | 5,0 | 30 | 20 | -10 |
| Carotte | 2 | 600 | 2,2 | 20 | 10 | -5 |
| Radis | 1 | 400 | 1,0 | 15 | 5 | -3 |
| Laitue | 1 | 500 | 1,2 | 30 | 10 | -5 |
| Tomate | 3 | 1 400 | 6,0 | 35 | 25 | -10 |
| Courgette | 2 | 1 200 | 4,0 | 35 | 20 | -8 |
| Chou | 2 | 1 000 | 3,5 | 30 | 25 | -10 |
| Pois | 2 | 600 | 2,0 | 20 | 0 | +6 |
| Haricot | 2 | 700 | 2,4 | 25 | 0 | +5 |
| Fève | 3 | 700 | 3,2 | 20 | 0 | +8 |

## Règles agricoles

Planter exige une case libre et assez d'argent. La croissance repart de 0.
Replanter une espèce ayant le même nom que la dernière plantée retire
10 points de biodiversité, sans descendre sous 0. Planter une autre espèce
évite ce malus, sans donner de bonus immédiat. La dernière espèce est mémorisée
après chaque plantation réussie, même si la plante meurt ensuite.

Arroser exige un volume entier strictement positif en m³, assez d'eau en réserve et une
quantité ne dépassant pas `100 - humidite`. La quantité est transférée
exactement de la réserve vers le sol. On peut aussi arroser une case vide.

À chaque passage de saison, la ferme reçoit 20 m³ d'eau et un bonus de 1 000 €, puis
chacune des neuf parcelles évolue une seule fois dans cet ordre :

1. La pluie ajoute 10 d'humidité, avec un plafond de 100.
2. Une parcelle vide au début de l'évolution récupère 10 d'azote et
   5 de biodiversité, avec un plafond de 100 pour chacun.
3. Une plante présente survit si l'humidité atteint son eau minimale,
   si l'azote atteint son seuil et si la biodiversité atteint 20 %.
   Sinon elle meurt : la case est libérée et la croissance revient à 0,
   sans nourriture ni remboursement. Son sol ne profite du repos qu'à
   l'évolution suivante. La cause est affichée, avec priorité à l'humidité,
   puis à l'azote, puis à la biodiversité. Les autres parcelles évoluent aussi.
4. Une plante survivante non mature gagne 1 de croissance et applique son
   impact sur l'azote, borné entre 0 et 100. Une plante mature ne grandit plus
   et ne modifie plus l'azote, mais peut encore mourir.
5. L'évaporation retire 20 d'humidité, sans descendre sous 0.

Récolter exige une plante mature. Le rendement rejoint le stock global,
la case est libérée et la croissance revient à 0. L'état du sol et la dernière
espèce sont conservés. Une plante ne peut être récoltée qu'une fois.

## Économie, bilan et victoire

Le prix de vente choisi pour le jeu est fixe : **1 €/kg, soit 1 000 €/t**,
pour toutes les cultures. Il ne représente pas leurs cours agricoles réels.
La vente exige une masse entière strictement positive en kilogrammes,
ne dépassant pas le stock disponible.
Il n'y a ni stock de graines ni inventaire par culture.

```text
bénéfice agricole (€) = recettes des ventes (€) - dépenses en semences (€)
```

Les bonus saisonniers sont exclus du bénéfice. La nourriture non vendue
reste affichée, sans compter comme une recette.
La victoire exige **un bénéfice strictement positif** et **une biodiversité
moyenne des neuf parcelles supérieure ou égale à 50 %**. La moyenne réelle
sert à décider la victoire avant l'arrondi d'affichage. Un bénéfice nul est
une défaite ; une biodiversité exactement à 50 % est acceptée.

Le bilan affiche la nourriture totale récoltée, le stock restant, les ventes,
les dépenses en graines, les bonus reçus, l'argent final, le bénéfice, la
biodiversité moyenne et le résultat avec ses raisons. Il n'y a pas de score pondéré.

Exemple gagnant : planter des pois (culture 10) en (1, 1) au début, passer
deux saisons, récolter 2 t et vendre les 2 000 kg, puis laisser les neuf parcelles
au repos jusqu'à la fin. Après douze évolutions : semences 600 €, ventes 2 000 €,
bénéfice 1 400 €, bonus 12 000 €, argent final **23 400 €**,
biodiversité moyenne **100 %**.

## Organisation et adaptation du sujet

Le lancement du squelette est conservé : `UI()`, `Moteur(ui)`, puis
`moteur.lancer()`. Le modèle remplace `ExempleModele` :

- `modele/espece.py` : sept caractéristiques et un seul catalogue partagé.
- `modele/parcelle.py` : sol, croissance, survie et récolte d'une case.
- `modele/exploitation.py` : neuf parcelles distinctes et ressources de la ferme.
- `moteur.py` : actions, saisons, statistiques cumulées et calcul du bilan.
- `ui.py` : affichages et saisies ; aucun calcul agricole ou économique.
- `tests/tests_modeles.py` : tests avec `assert`, exécutables directement.
- `diagramme_classes.svg` : attributs, méthodes et relations du modèle.

Les trois classes du modèle n'utilisent ni `print()` ni `input()`.
Les actions métier invalides lèvent `ValueError`, capturée par le moteur.
La croissance appartient à la parcelle ; plusieurs parcelles peuvent partager
la même espèce. La méthode UML `objectif_atteint(cible)` compare le stock de
nourriture à une cible en kilogrammes ; elle ne détermine pas la victoire.

Pour remplacer les anciennes unités abstraites, les montants d'argent et les
masses récoltées ont été multipliés par 100 dans le modèle. Cette mise à
l'échelle conserve les rapports entre capital, coûts, ventes et bonus.
Les seuils du sol, la réserve d'eau et les durées de croissance sont conservés.

Une seule mission avancée est réalisée : **mission A**, dans le périmètre
monoculture, rotation et jachère décrit ci-dessus. Les conditions financières
et écologiques remplacent volontairement l'objectif initial de nourriture :
aucun seuil de 150 nourritures et aucune victoire anticipée.
Cette version ne prétend pas couvrir tous les points du barème du PDF.

Sont exclus : missions B et C, bocages, interface graphique, sauvegarde,
météo aléatoire, température, engrais, pesticides, animaux, stock de graines
et marché variable. L'archive et le PDF d'origine sont conservés.

## Membres de l'équipe — à remplir par les élèves

| Prénom et nom | Contributions réelles |
| --- | --- |
| À remplir | À remplir |

## Journal de bord — à remplir par les élèves

| Date réelle | Membre | Travail effectué et vérification |
| --- | --- | --- |
| À remplir | À remplir | À remplir |
