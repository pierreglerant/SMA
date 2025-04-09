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

## Fonctionnalités Implémentées

### Politique de Déplacement

Les robots utilisent une politique de déplacement déterministe avec les caractéristiques suivantes :

Pour l'instant la politique de déplacement est la suivante:
    - Tous les robots effectuent des serpentins de en alternant le sens bas --> haut puis haut --> bas
    - Si ils repèrent un déchet sur l'une des 8 cases adjacentes, ils attrapent le déchet au step suivant en allant sur la case en question
    - Une fois que leur inventaire est plein, les robots se déplacent vers l'ouest. Les robots vert et jaunes déposent le déchet sur la case est adjacente à la frontière ouest de leur zone tandis que les robots rouges déposent leurs déchets dans la zone de dépôt.
    - Les robots verts n'ont accès qu'à leur zone. Les robots jaunes et rouges ont accès à leur zone + à la colonne adjacente à leur frontière est (cela leur permet de récupérer les déchets déposés par les robots des zones plus à l'est).

### Collecte et Traitement des Déchets

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

## Auteurs

- Vogels Arthur
- Pierre Glerant

## Date

11/04/2025