"""
Groupe 20 - 11/03/2025 - Vogels Arthur, Pierre Glerant
"""

from mesa import Agent
import random
from .utils import get_pos_delta, get_new_pos
from .objects import Radioactivity, Waste

class RobotAgent(Agent):
    """
    Agent de base pour la simulation de collecte et traitement de déchets.
    """
    
    def __init__(self, model):
        # Initialisation de l'agent et de ses attributs
        super().__init__(model)
        self.knowledge = lambda: 0  # Stockage des connaissances locales
        self.inventory = []         # Inventaire des déchets collectés
        self.ready_to_deliver = []  # Déchets traités prêts à être déposés
        self.inventory_full = False # Statut de remplissage de l'inventaire
        self.level = 0              # Niveau de toxicité
        self.dir_w = random.choice([-1,1])              # Direction horizontale pour la politique
        self.dir_h = random.choice([-1,1])              # Direction verticale pour la politique
        self.vertical_moves_count = 0  # Compteur de déplacements verticaux consécutifs
    
    def __random_policy__(self):
        # Politique aléatoire : si un déchet est proche, se déplacer vers lui
        if len(self.knowledge.close_waste.keys()) > 0:
            return random.choice(list(self.knowledge.close_waste.keys()))
        # Sinon, choisir un mouvement possible au hasard
        return random.choice(self.knowledge.possible_moves)

    def __policy__(self):
        # Politique déterministe basée sur la direction actuelle
        if (self.dir_w, 0) in self.knowledge.possible_moves:
            self.vertical_moves_count = 0  # Réinitialise le compteur car on bouge horizontalement
            return (self.dir_w, 0)
        if (0, self.dir_h) in self.knowledge.possible_moves:
            if self.vertical_moves_count < 2:  # Si on n'a pas encore fait 2 mouvements verticaux
                self.vertical_moves_count += 1
                return (0, self.dir_h)
            else:  # Si on a fait 2 mouvements verticaux, on inverse la direction horizontale
                self.dir_w = -self.dir_w
                self.vertical_moves_count = 0
                return (self.dir_w, 0)
        # Inverse les directions si les mouvements précédents ne sont pas possibles
        self.dir_h = -self.dir_h
        self.dir_w = -self.dir_w
        self.vertical_moves_count = 0
        return (self.dir_w, 0)

    def get_level(self):
        # Retourne le niveau de toxicité du robot
        return self.level

    def process_waste(self):
        # Transforme deux déchets en un déchet plus toxique prêt à être livré
        self.ready_to_deliver.append(self.model.process_waste(self.inventory.pop(), self.inventory.pop()))

    def perceive(self):
        # Met à jour la perception de l'environnement par l'agent
        self.inventory_full = len(self.inventory) > 1
            
        # Récupère les cellules voisines (incluant la position actuelle)
        possible_moves = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=True
        )
        # Calcule les décalages vers les cellules voisines
        self.knowledge.neighbors = [get_pos_delta(self.pos, possible_step) for possible_step in possible_moves]
        # Stocke le contenu des cellules voisines
        self.knowledge.close_contents = {}
        for possible_step in self.knowledge.neighbors:
            self.knowledge.close_contents[possible_step] = self.model.grid.get_cell_list_contents(
                [get_new_pos(self.pos, possible_step)]
            )
        # Initialise la liste des mouvements possibles
        self.knowledge.possible_moves = list(self.knowledge.neighbors)
        # Exclut certaines directions en cas de radioactivité trop élevée
        if (1, 0) in self.knowledge.neighbors:
            for a in self.knowledge.close_contents[(1, 0)]:
                if isinstance(a, Radioactivity) and a.get_radioactivity_level() > self.level:
                    self.knowledge.possible_moves = list(
                        set(self.knowledge.possible_moves) - set([(1, 0), (1, -1), (1, 1)])
                    )
        # Exclut certaines directions en cas de radioactivité trop faible
        for a in self.knowledge.close_contents[(0, 0)]:
            if isinstance(a, Radioactivity) and a.get_radioactivity_level() < self.level:
                self.knowledge.possible_moves = list(
                    set(self.knowledge.possible_moves) - set([(-1, 0), (-1, -1), (-1, 1)])
                )

    def deliberate(self):
        # Si l'inventaire est plein, traiter les déchets
        if self.inventory_full:
            self.process_waste()

        # Si des déchets traités sont prêts, se déplacer vers la droite pour déposer
        if len(self.ready_to_deliver):
            if (1, 0) in self.knowledge.possible_moves:
                return (1, 0)
            else:
                return "DROP"
        
        # Recherche de déchets compatibles dans l'environnement
        self.knowledge.close_waste = {}
        for k in self.knowledge.possible_moves:
            waste_list = [w for w in self.knowledge.close_contents[k] 
                        if isinstance(w, Waste) and w.get_level() == self.get_level()]
            if waste_list:
                self.knowledge.close_waste[k] = waste_list
        
        # Si l'inventaire n'est pas plein, on regarde s'il y a un déchet sur la case courante
        if not self.inventory_full:
            if (0, 0) in self.knowledge.close_waste:
                return "PICK"
            # Sinon, s'il y a un déchet dans une case adjacente, on se déplace vers cette case
            elif self.knowledge.close_waste:
                return random.choice(list(self.knowledge.close_waste.keys()))
        
        # Si aucune de ces conditions n'est remplie, appliquer la politique déterministe par défaut
        return self.__policy__()

    def step(self):
        # Exécute une étape : perception, délibération et action
        self.perceive()
        action = self.deliberate()
        self.model.perform_action(self, action)

class GreenRobotAgent(RobotAgent):
    def __init__(self, model):
        # Robot vert : niveau de toxicité 1
        super().__init__(model)
        self.level = 1

class YellowRobotAgent(RobotAgent):
    def __init__(self, model):
        # Robot jaune : niveau de toxicité 2
        super().__init__(model)
        self.level = 2

class RedRobotAgent(RobotAgent):
    def __init__(self, model):
        # Robot rouge : niveau de toxicité 3
        super().__init__(model)
        self.level = 3
