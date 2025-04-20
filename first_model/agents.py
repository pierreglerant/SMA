"""
Groupe 20 - 11/03/2025 - Vogels Arthur, Pierre Glerant
"""

from mesa import Agent
import random
from .utils import get_pos_delta, get_new_pos
from .objects import Radioactivity, Waste
import sys
import os
import re
import bisect
import numpy as np

# Chemin vers la solution d'interaction
solution_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Solution_Interaction_Mesa', 'mesa')
if solution_path not in sys.path:
    sys.path.append(solution_path)

# Importer les classes de communication
from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative

class Knowledge:
    """Classe pour stocker les connaissances du robot"""
    def __init__(self):
        self.neighbors = []
        self.close_contents = {}
        self.possible_moves = []
        self.close_waste = {}
        self.target_waste = []  # Pour stocker la position d'un déchet signalé
        self.potential_wastes = None
        self.going_to_signaled_waste = False  # Pour indiquer si le robot se dirige vers un déchet signalé
        self.zone_is_clean = False

class RobotAgent(CommunicatingAgent):
    """
    Agent de base pour la simulation de collecte et traitement de déchets.
    """
    
    def __init__(self, model):
        # Initialisation de l'agent et de ses attributs
        # Générer un identifiant unique à partir du compteur du modèle         
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
        self.step_num = 0
        self.n_robots = -1
        self.pos_list = []

        self.trade_position = None
        self.drop_for_trade = False
        self.proposed_trade = False

        self.is_done = False
        self.lower_done = 0
    
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

    def broadcast_position(self):
        same_level_robots = [a for a in self.model.agents if (isinstance(a, type(self)) and a is not self)]
        self.n_robots = len(same_level_robots)
        
        # Broadcast position
        for a in same_level_robots:
            self.send_message(Message(self.get_name(), a.get_name(), MessagePerformative.INFORM_REF, f"posY:{self.pos[1]}"))

    def assign_vertical_zone(self):
        """Assigne une zone verticale au robot en fonction des autres robots de même niveau"""
        # Trouver tous les robots du même niveau
            
        # Receive_positions
        message_list = self.get_new_messages()
        for m in message_list:
            m_content = m.get_content()
            if "posY" in m_content:
                match = re.search(r'\d+', m_content)
                self.pos_list.append(int(match.group()))

        if len(self.pos_list) == self.n_robots:
            # Trier les robots par position y
            self.pos_list.sort()
            
            # Trouver l'index de ce robot dans la liste triée
            my_index = bisect.bisect_left(self.pos_list, self.pos[1])
            
            # Calculer la taille de chaque division
            zone_height = self.model.h
            division_size = zone_height / (self.n_robots+1)
            
            # Le robot le plus bas aura la zone la plus basse
            self.zone_h_min = int(my_index * division_size)
            self.zone_h_max = int((my_index + 1) * division_size)
            
            # Calculer le centre de la zone attribuée
            self.target_y = int((self.zone_h_min + self.zone_h_max) / 2)

            # Create potential wastes zone
            self.knowledge.potential_wastes = np.ones([self.model.w//3, (self.zone_h_max-self.zone_h_min)])


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
        """Signale un déchet aux robots du niveau supérieur en utilisant le service de messagerie"""
        # Trouver tous les robots du niveau supérieur
        next_level_robots = [agent for agent in self.model.agents 
                           if isinstance(agent, RobotAgent) 
                           and agent.level == self.level + 1]
        
        for r in next_level_robots:
            message_content = {"waste_pos": waste_pos}
            self.send_message(Message(
                    self.get_name(),
                    r.get_name(),
                    MessagePerformative.INFORM_REF,
                    message_content
                ))
    
    def propose_trade(self):
        same_level_robots = [agent for agent in self.model.agents 
                           if isinstance(agent, RobotAgent) 
                           and agent.level == self.level and agent is not self]
        
        for r in same_level_robots:
            message_content = {"Trade": self.pos}
            self.send_message(Message(
                self.get_name(),
                r.get_name(),
                MessagePerformative.PROPOSE,
                message_content
            ))
        self.proposed_trade = True
    def accept_trade(self, receiver, trade_pos):
        message_content = {"Trade": trade_pos}
        self.send_message(Message(
            self.get_name(),
            receiver,
            MessagePerformative.ACCEPT,
            message_content
        ))

    def broadcast_done(self):
        next_level_robots = [agent for agent in self.model.agents 
                           if isinstance(agent, RobotAgent) 
                           and agent.level == self.level+1 and agent is not self]
        
        for r in next_level_robots:
            self.send_message(Message(
                self.get_name(),
                r.get_name(),
                MessagePerformative.INFORM_REF,
                "DONE"
            ))

        
    def handle_messages(self):
        """Traite les messages reçus dans la boîte aux lettres"""
        messages = self.get_new_messages()
        for message in messages:
            if message.get_performative() == MessagePerformative.INFORM_REF:
                content = message.get_content()
                if isinstance(content, dict) and "waste_pos" in content:
                    waste_pos = content["waste_pos"]
                    if waste_pos[1]>= self.zone_h_min and waste_pos[1] < self.zone_h_max:
                        self.knowledge.target_waste.append(content["waste_pos"])
                        self.knowledge.going_to_signaled_waste = True
                if "DONE" in content:
                    self.lower_done += 1
                
            if message.get_performative() == MessagePerformative.PROPOSE:
                if np.sum(self.knowledge.potential_wastes) == 0 and len(self.inventory) > 0 and not self.trade_position:
                    content = message.get_content()
                    offer_pos = content["Trade"]
                    #trade_pos = (offer_pos[0]+self.pos[0])//2, (offer_pos[1]+self.pos[1])//2
                    trade_pos = offer_pos
                    self.trade_position = trade_pos
                    self.drop_for_trade = True
                    self.accept_trade(message.get_exp(), trade_pos)

            if message.get_performative() == MessagePerformative.ACCEPT:
                if len(self.inventory) > 0 and self.trade_position is None:
                    content = message.get_content()
                    self.trade_position = content["Trade"]

    def move_to_target_waste(self):
        """Calcule le mouvement vers un déchet signalé"""
        if len(self.knowledge.target_waste) == 0:
            return None

        if self.inventory_full:
            return None
        
        targ = self.knowledge.target_waste[0]
        # Calculer la direction pour atteindre le déchet
        dx = targ[0] - self.pos[0]
        dy = targ[1] - self.pos[1]
        
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
            self.knowledge.target_waste.pop(0)
            
        return None
    
    def move_to_trade_position(self):

        if not self.trade_position:
            return None
        
        dx = self.trade_position[0] - self.pos[0]
        dy = self.trade_position[1] - self.pos[1]

        return np.sign(dx), np.sign(dy)

    def perceive(self):
        
        self.inventory_full = len(self.inventory) > 1

        if self.pos in self.knowledge.target_waste:
            self.knowledge.target_waste.remove(self.pos)
            
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
            if (self.zone_h_min <= new_pos[1] < self.zone_h_max) or possible_step == (0,0):
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
        
        for k in self.knowledge.possible_moves:
            if k in self.knowledge.close_contents:
                waste_list = [w for w in self.knowledge.close_contents[k] 
                            if isinstance(w, Waste) and w.get_level() == self.get_level()]
                if not len(waste_list) and np.sum(self.knowledge.potential_wastes) > 0:
                    x_no_waste = self.pos[0]+k[0]-(self.level-1)*(self.model.w//3)
                    if x_no_waste < self.model.w//3 and x_no_waste >= 0:
                        self.knowledge.potential_wastes[x_no_waste, self.pos[1]-self.zone_h_min+k[1]] = 0

    def check_if_done(self):
        if np.sum(self.knowledge.potential_wastes) == 0 and not len(self.inventory) and not len(self.ready_to_deliver):
            if self.level == 1:
                self.broadcast_done()
                self.is_done = True
            elif self.level == 2:
                if self.lower_done == self.model.n_agents_g and not len(self.knowledge.target_waste):
                    self.broadcast_done()
                    self.is_done = True
            else:
                if self.lower_done == self.model.n_agents_y and not len(self.knowledge.target_waste):
                    self.is_done = True

    def deliberate(self): 

        if self.is_done:
            return (0,0)
        
        self.check_if_done()
        # Traiter d'abord les messages reçus
        self.handle_messages()
        
        # Phase initiale : se déplacer vers sa zone
        if self.initial_positioning:
            move = self.move_to_zone()
            if move is not None:
                return move

        # Si on a un déchet signalé à récupérer
        if np.sum(self.knowledge.potential_wastes) == 0 and self.knowledge.going_to_signaled_waste and not self.inventory_full and not self.ready_to_deliver:
            move = self.move_to_target_waste()
            if move is not None and move != (0,0):
                return move
            
        if (not self.knowledge.going_to_signaled_waste) and self.trade_position:
            if self.pos[0] != self.trade_position[0] or self.pos[1] != self.trade_position[1]:
                return self.move_to_trade_position()
            
            if self.drop_for_trade:
                self.trade_position = None
                self.drop_for_trade = False
                self.broadcast_done()
                self.is_done = True
                return "TRADE"
            
            if any([isinstance(x,Waste) for x in self.knowledge.close_contents[(0,0)]]):
                self.trade_position = None
                print("Picked trash")
                return "PICK"
            else:
                return (0,0)

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
                print("Dropping a waste")
                return "DROP"
        
        if not np.sum(self.knowledge.potential_wastes) and not self.trade_position:
            if len(self.inventory) > 0:
                self.propose_trade()
            return (0,0)
        
        
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
                print("picking a waste")
                return "PICK"
            elif self.knowledge.close_waste:
                return random.choice(list(self.knowledge.close_waste.keys()))
        
        return self.__policy__()

    def step(self):
        if self.step_num == 0:
            self.broadcast_position()
            self.step_num += 1
        elif self.step_num == 1:
            self.assign_vertical_zone()
            self.step_num += 1
        if self.step_num >1:
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
        # Traiter d'abord les messages reçus
        self.handle_messages()
        
        # Phase initiale : se déplacer vers sa zone
        if self.initial_positioning:
            move = self.move_to_zone()
            if move is not None:
                return move

        if np.sum(self.knowledge.potential_wastes) == 0 and self.knowledge.going_to_signaled_waste and not self.inventory_full and not self.ready_to_deliver:
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
