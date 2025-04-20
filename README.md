# Simulation de Collecte et Traitement de Déchets Radioactifs

## Description du Projet

Ce projet est une simulation multi-agents qui modélise un environnement où des robots collectent et traitent des déchets radioactifs. L'environnement est divisé en zones de radioactivi té de différents niveaux, et les robots doivent collecter des déchets compatibles avec leur niveau de résistance, les fusionner pour créer des déchets plus toxiques, et les déposer dans une zone de dépôt.

## Structure du Projet

Le projet est organisé en plusieurs fichiers python :

- `agents.py` : Définit les robots
- `model.py` : Implémente le modèle de simulation
- `objects.py` : Définit les objets présents dans l'environnement (déchets, zone de dépôt, zones radioactives) 
- `utils.py` : Contient des fonctions utilitaires
- `visualization.py` : Gère la visualisation de la simulation
- `main.py` : Point d'entrée de l'application

## Agents et Objets

### Robots

Trois types de robots sont définis, chacun avec un niveau de résistance différent :

1. **GreenRobotAgent** : Niveau de résistance 1 (vert)
2. **YellowRobotAgent** : Niveau de résistance 2 (jaune)
3. **RedRobotAgent** : Niveau de résistance 3 (rouge)

Chaque robot possède :

- Un inventaire pour stocker les déchets collectés
- Une liste de déchets traités prêts à être déposés
- Une politique de déplacement

### Objets

1. **Radioactivity** : Zones de radioactivité de différents niveaux (1, 2, 3)
2. **Waste** : Déchets radioactifs de différents niveaux (1, 2, 3)
3. **DisposalZone** : Zone de dépôt pour les déchets traités

## Collecte et Traitement des Déchets

- Les robots ne peuvent collecter que des déchets de leur niveau de résistance
- Les robots peuvent fusionner deux déchets de même niveau pour créer un déchet de niveau supérieur
- Les robots verts fusionnent deux déchets vert pour en faire un jaune avant de le déposer, les robots jaunes fusionnent deux déchets jaunes pour en faire un rouge et les rouges déposent directement chaque déchet rouge qu'ils trouvent 

## Visualisation

La simulation est visualisée à l'aide de Solara, qui fournit :

- Une représentation graphique de la grille avec les agents et les objets
- Un graphique montrant le nombre de déchets restants dans l'environnement
- Des contrôles pour ajuster les paramètres de la simulation

## Paramètres Configurables

- Nombre d'agents de chaque couleur (vert, jaune, rouge)
- Nombre de déchets de chaque niveau

## Comment Exécuter la Simulation

Pour lancer la simulation, exécutez le fichier `main.py`. Une interface web s'ouvrira, permettant de visualiser et de contrôler la simulation.
```bash
solara run first_model.main
```

## Politique de Déplacement sans communication

Chaque robot agit de manière totalement autonome, sans échange d’informations, et couvre sa zone entière.

**Étape 1 : Balayage de la zone**  
- Chaque robot parcourt **l’intégralité** de sa zone en serpentins (alternance bas→haut / haut→bas).  

**Étape 2 : Ramassage et dépôt**  
1. **Ramassage** : dès qu’un déchet est détecté sur une case adjacente, le robot s’y rend pour le saisir
2. **Dépôt** : inventaire plein → direction ouest
   - **Zones verte & jaune** : déposent à l’est de la limite ouest. 
   - **Zone rouge** : déposent dans l’aire de dépôt  
3. **Accès** identique à la variante avec communication (vert seule zone, jaune/rouge avec colonne adjacente à l’est)

> **Note :**  
> - Il n’y a ni découpage en sous‑zones, ni phase terminale coordonnée ; chaque robot continue seul jusqu’à épuisement des déchets dans sa zone.
> - Il y a des cas où la simulation ne peut pas être terminée.  
>   Exemple : S'il n'y a plus de déchets verts au sol et que deux robots de la zone verte ont chacun un déchet vert.  

## Politique de Déplacement avec communication

Les robots suivent une stratégie déterministe en trois phases :

**Étape 1 : Répartition en sous‑zones**  
- Chaque zone est découpée en sous‑zones de largeur égale (écart maximal : une ligne).  
- Chaque robot est affecté à l’une de ces sous‑zones.

**Étape 2 : Parcours en serpentins et collecte**  
1. **Mouvement en serpentins**  
   - Dans sa sous‑zone, chaque robot balaie les lignes en serpentins (alternance bas→haut puis haut→bas).  
2. **Ramassage**  
   - Si un déchet apparaît sur une case adjacente à sa position (et dans sa sous‑zone), le robot s’y rend au pas suivant pour le saisir.  
3. **Dépôt**  
   - Dès que son inventaire est plein, le robot se dirige vers l’ouest :  
     - **Zones verte et jaune** : dépose le déchet sur la case située juste à l’est de la frontière ouest de leur zone.  
     - **Zone rouge** : transporte son déchet jusqu’à l’aire de dépôt.  
4. **Accès aux zones**  
   - **Vert** : uniquement à sa propre zone.  
   - **Jaune et rouge** : à leur zone plus la colonne immédiatement à l’est de leur frontière (pour récupérer les déchets largués par les zones plus à l’est).

**Étape 3 : Phase terminale de chaque zone**  
Lorsque, pour une zone donnée, aucun robot n’a collecté de déchet pendant  
\[
\frac{l \times L}{n_{\text{robots\_zone}}} + 1
\]  
tours ET que la ou les zones plus à l’est ont déjà déclenché leur phase finale, on passe à la procédure suivante :

- **Rassemblement**  
  1. Tous les robots se rejoignent sur la ligne médiane de la zone.
  2. Ils déposent leur déchet et s’immobilisent, sauf un seul.
- **Collecte finale**
  - Le robot restant arpente seul la ligne médiane et y termine la collecte des déchets.

Cette séquence s’applique successivement à la **zone verte**, puis à la **zone jaune**, et enfin à la **zone rouge**.

## Comparaison des résultats sans ou avec communication
## Comparaison des résultats sans ou avec communication

La version finale de l’**algorithme sans communication** correspond au Commit `9b129b0b4ac270c953deed16670d8f74af5ef6cb` (“fix: Corriger le bug d'initialisation”). La version finale de l’**algorithme avec communication** correspond au dernier commit de la branche master.

Le premier **avantage** de l’algorithme avec communication est de résoudre certaines situations qui empêchent les robots de finir leur tâche.

**Exemple :**  
Lorsqu’il n’y a plus de déchets au sol mais que certains robots d’une même zone ont un seul déchet, l’algorithme avec communication permet de résoudre ce problème (Étape 3) alors que celui sans communication ne le permet pas.

Le second avantage de la communication est qu’elle permet d’attribuer des sous‑zones aux robots au début de la simulation, ce qui accélère le ramassage des déchets.

Comme l’algorithme sans communication ne permet pas toujours aux robots de déposer tous leurs déchets dans la zone de dépôt, on ne le comparera pas en nombre total de steps pour vider la zone de dépôt.  
Les algorithmes seront plutôt comparés sur le nombre de steps nécessaires pour qu’il n’y ait plus de déchet au sol, afin de mesurer l’impact de la répartition des robots dans des sous‑zones grâce à la communication.


1e situation :

## Auteurs

- Vogels Arthur
- Pierre Glerant

## Date

20/04/2025