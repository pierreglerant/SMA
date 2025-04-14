"""
Groupe 20 - 11/03/2025 - Vogels Arthur, Pierre Glerant
"""

from mesa import Agent
import random
from .utils import get_pos_delta, get_new_pos
from .objects import Radioactivity, Waste

class Knowledge:
    """Classe pour stocker les connaissances du robot"""
    def __init__(self):
        self.neighbors = []
        self.close_contents = {}
        self.possible_moves = []
        self.close_waste = {}
        self.target_waste = None  # Pour stocker la position d'un déchet signalé
        self.going_to_signaled_waste = False  # Pour indiquer si le robot se dirige vers un déchet signalé

class RobotAgent(Agent):
    """
    Agent de base pour la simulation de collecte et traitement de déchets.
    """
    
    def __init__(self, model):
        # Initialisation de l'agent et de ses attributs
        super().__init__(model)
        self.knowledge = Knowledge()  # Initialiser avec une instance de Knowledge au lieu de lambda
        self.inventory = []         # Inventaire des déchets collectés
        self.ready_to_deliver = []  # Déchets traités prêts à être déposés
        self.inventory_full = False # Statut de remplissage de l'inventaire
        self.level = 0              # Niveau de toxicité
        self.dir_w = random.choice([-1,1])              # Direction horizontale pour la politique
        self.dir_h = random.choice([-1,1])              # Direction verticale pour la politique
        self.vertical_moves_count = 0  # Compteur de déplacements verticaux consécutifs
        
        # Nouvelles variables pour la division de zone
        self.zone_h_min = 0  # Limite basse de la zone du robot
        self.zone_h_max = 0  # Limite haute de la zone du robot
        self.initial_positioning = True  # Nouveau flag pour la phase initiale
        self.target_y = 0  # Nouveau attribut pour le centre de la zone attribuée
    
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

    def assign_vertical_zone(self, robots_same_level):
        """Assigne une zone verticale au robot en fonction des autres robots de même niveau"""
        # Trouver tous les robots du même niveau
        same_level_robots = [r for r in robots_same_level if r.level == self.level]
        n_robots = len(same_level_robots)
        
        # Trier les robots par position y
        sorted_robots = sorted(same_level_robots, key=lambda r: r.pos[1])
        
        # Trouver l'index de ce robot dans la liste triée
        my_index = sorted_robots.index(self)
        
        # Calculer la taille de chaque division
        zone_height = self.model.h
        division_size = zone_height / n_robots
        
        # Le robot le plus bas aura la zone la plus basse
        self.zone_h_min = int(my_index * division_size)
        self.zone_h_max = int((my_index + 1) * division_size)
        
        # Calculer le centre de la zone attribuée
        self.target_y = int((self.zone_h_min + self.zone_h_max) / 2)

    def move_to_zone(self):
        """Déplace le robot vers le centre de sa zone attribuée"""
        current_y = self.pos[1]
        if current_y < self.target_y:
            return (0, 1)  # Monter
        elif current_y > self.target_y:
            return (0, -1)  # Descendre
        else:
            self.initial_positioning = False  # Le robot est arrivé dans sa zone
            return None

    def signal_waste(self, waste_pos):
        """Signale un déchet aux robots du niveau supérieur"""
        # Trouver tous les robots du niveau supérieur
        next_level_robots = [agent for agent in self.model.agents 
                           if isinstance(agent, RobotAgent) 
                           and agent.level == self.level + 1
                           and not agent.inventory_full]
        
        if next_level_robots:
            # Trouver le robot le plus proche qui n'est pas plein
            closest_robot = min(next_level_robots, 
                              key=lambda r: abs(r.pos[0] - waste_pos[0]) + abs(r.pos[1] - waste_pos[1]))
            closest_robot.knowledge.target_waste = waste_pos
            closest_robot.knowledge.going_to_signaled_waste = True

    def move_to_target_waste(self):
        """Calcule le mouvement vers un déchet signalé"""
        if not self.knowledge.target_waste:
            return None

        # Calculer la direction pour atteindre le déchet
        dx = self.knowledge.target_waste[0] - self.pos[0]
        dy = self.knowledge.target_waste[1] - self.pos[1]
        
        # Choisir le mouvement prioritaire (horizontal ou vertical)
        if abs(dx) > 0:
            move_x = (1 if dx > 0 else -1, 0)
            if move_x in self.knowledge.possible_moves:
                return move_x
        if abs(dy) > 0:
            move_y = (0, 1 if dy > 0 else -1)
            if move_y in self.knowledge.possible_moves:
                return move_y

        # Si on est arrivé au déchet
        if dx == 0 and dy == 0:
            self.knowledge.going_to_signaled_waste = False
            self.knowledge.target_waste = None
            
        return None

    def perceive(self):
        self.inventory_full = len(self.inventory) > 1
            
        # Si en phase initiale, obtenir tous les mouvements possibles
        if self.initial_positioning:
            possible_moves = self.model.grid.get_neighborhood(
                self.pos, moore=False, include_center=True
            )
            self.knowledge.neighbors = [get_pos_delta(self.pos, possible_step) for possible_step in possible_moves]
            self.knowledge.possible_moves = self.knowledge.neighbors
            self.knowledge.close_contents = {}  # Initialiser close_contents même en phase initiale
            for move in self.knowledge.possible_moves:
                new_pos = get_new_pos(self.pos, move)
                self.knowledge.close_contents[move] = self.model.grid.get_cell_list_contents([new_pos])
            return

        # Perception normale une fois dans la zone
        possible_moves = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=True
        )
        
        self.knowledge.neighbors = [get_pos_delta(self.pos, possible_step) for possible_step in possible_moves]
        
        # Réinitialiser close_contents
        self.knowledge.close_contents = {}
        
        # Remplir close_contents pour tous les mouvements possibles
        for possible_step in self.knowledge.neighbors:
            new_pos = get_new_pos(self.pos, possible_step)
            # Vérifier si le mouvement reste dans la zone verticale assignée
            if self.zone_h_min <= new_pos[1] < self.zone_h_max:
                self.knowledge.close_contents[possible_step] = self.model.grid.get_cell_list_contents([new_pos])

        # Mettre à jour possible_moves en fonction des positions valides
        self.knowledge.possible_moves = [
            move for move in self.knowledge.neighbors
            if move in self.knowledge.close_contents
        ]

        # Vérifications de radioactivité
        if (1, 0) in self.knowledge.close_contents:
            for a in self.knowledge.close_contents[(1, 0)]:
                if isinstance(a, Radioactivity) and a.get_radioactivity_level() > self.level:
                    moves_to_remove = [(1, 0), (1, -1), (1, 1)]
                    self.knowledge.possible_moves = [
                        move for move in self.knowledge.possible_moves 
                        if move not in moves_to_remove
                    ]

        if (0, 0) in self.knowledge.close_contents:
            for a in self.knowledge.close_contents[(0, 0)]:
                if isinstance(a, Radioactivity) and a.get_radioactivity_level() < self.level:
                    moves_to_remove = [(-1, 0), (-1, -1), (-1, 1)]
                    self.knowledge.possible_moves = [
                        move for move in self.knowledge.possible_moves 
                        if move not in moves_to_remove
                    ]

    def deliberate(self):
        # Phase initiale : se déplacer vers sa zone
        if self.initial_positioning:
            move = self.move_to_zone()
            if move is not None:
                return move

        # Si on a un déchet signalé à récupérer
        if self.knowledge.going_to_signaled_waste:
            move = self.move_to_target_waste()
            if move is not None:
                return move

        # Comportement normal
        if self.inventory_full:
            self.process_waste()

        if len(self.ready_to_deliver):
            if (1, 0) in self.knowledge.possible_moves:
                return (1, 0)
            else:
                # Signaler le déchet aux robots du niveau supérieur avant de le déposer
                if self.level < 3:  # Seulement pour les robots verts et jaunes
                    self.signal_waste(self.pos)
                return "DROP"
        
        # Recherche de déchets compatibles dans l'environnement
        self.knowledge.close_waste = {}
        for k in self.knowledge.possible_moves:
            if k in self.knowledge.close_contents:
                waste_list = [w for w in self.knowledge.close_contents[k] 
                            if isinstance(w, Waste) and w.get_level() == self.get_level()]
                if waste_list:
                    self.knowledge.close_waste[k] = waste_list
        
        if not self.inventory_full:
            if (0, 0) in self.knowledge.close_waste:
                return "PICK"
            elif self.knowledge.close_waste:
                return random.choice(list(self.knowledge.close_waste.keys()))
        
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

    def deliberate(self):
        # Phase initiale : se déplacer vers sa zone
        if self.initial_positioning:
            move = self.move_to_zone()
            if move is not None:
                return move

        # Donner la priorité absolue aux déchets signalés
        if self.knowledge.going_to_signaled_waste and not self.inventory_full:
            move = self.move_to_target_waste()
            if move is not None:
                return move

        # Si l'inventaire est plein, traiter les déchets
        if self.inventory_full:
            self.process_waste()

        # Si des déchets sont prêts à être livrés
        if len(self.ready_to_deliver):
            if (1, 0) in self.knowledge.possible_moves:
                return (1, 0)
            else:
                return "DROP"
        
        # Recherche de déchets compatibles dans l'environnement
        self.knowledge.close_waste = {}
        for k in self.knowledge.possible_moves:
            if k in self.knowledge.close_contents:
                waste_list = [w for w in self.knowledge.close_contents[k] 
                            if isinstance(w, Waste) and w.get_level() == self.get_level()]
                if waste_list:
                    self.knowledge.close_waste[k] = waste_list
        
        # Ramasser ou se déplacer vers un déchet si l'inventaire n'est pas plein
        if not self.inventory_full:
            if (0, 0) in self.knowledge.close_waste:
                return "PICK"
            elif self.knowledge.close_waste:
                return random.choice(list(self.knowledge.close_waste.keys()))
            
        # Si aucune action prioritaire n'est possible, utiliser la politique de déplacement standard
        return self.__policy__()
