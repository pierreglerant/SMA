"""
Groupe 20 - 11/03/2025 - Vogels Arthur, Pierre Glerant
"""

from mesa import Model
from mesa.space import MultiGrid
import random
from .agents import (
    RobotAgent, GreenRobotAgent, YellowRobotAgent, RedRobotAgent
)
from .objects import Radioactivity, Waste, DisposalZone
from .utils import get_new_pos
from mesa.datacollection import DataCollector
import sys
import os

# Chemin vers la solution d'interaction
solution_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Solution_Interaction_Mesa', 'mesa')
if solution_path not in sys.path:
    sys.path.append(solution_path)

# Importer le service de messagerie
from communication.message.MessageService import MessageService
from communication.agent.CommunicatingAgent import CommunicatingAgent

# Créer une classe MessageService personnalisée
class CustomMessageService(MessageService):
    """Version personnalisée du MessageService qui ne considère que les agents communicants"""
    
    def __init__(self, model, instant_delivery=True):
        """Initialise le service de messagerie personnalisé"""
        # Pour éviter le singleton, nous devons réinitialiser l'instance
        MessageService._MessageService__instance = None
        super().__init__(model, instant_delivery)
        self.model = model  # Garder une référence publique au modèle
    
    def find_agent_from_name(self, agent_name):
        """Retourne l'agent correspondant au nom d'agent donné.
        Ne considère que les agents qui sont des instances de CommunicatingAgent.
        """
        for agent in self.model.agents:
            if isinstance(agent, CommunicatingAgent) and agent.get_name() == agent_name:
                return agent
        return None

class RobotMission(Model):
    # Modèle
    def __init__(self, n_agents_g=2, n_agents_y = 2, n_agents_r = 2, n_zone=3, n_waste_g=4, n_waste_y=4, n_waste_r=4, w=16, h=10, seed=None):
        super().__init__(seed=seed)
        
        # Compteur pour générer des ID uniques
        self.next_id = 0
        
        self.n_agents_g = n_agents_g  # Nombre d'agents par couleur
        self.n_agents_y = n_agents_y
        self.n_agents_r = n_agents_r
        self.n_zone = n_zone      # Nombre de zones de dépôt
        self.n_waste_g = n_waste_g    # Nombre de déchets par niveau
        self.n_waste_y = n_waste_y
        self.n_waste_r = n_waste_r
        self.w = w              # Nombre de colonnes
        self.h = h              # Nombre de lignes
        self.datacollector = DataCollector(model_reporters={"Number of wastes":lambda m: len(m.agents_by_type[type(Waste(Model()))])})
        
        # Initialiser le service de messagerie personnalisé
        self.message_service = CustomMessageService(self, instant_delivery=False)

        # Création de la grille (MultiGrid)
        self.grid = MultiGrid(self.w, self.h, torus=False)

        # Placement de la radioactivité niveau 1
        Radioactivity.create_agents(model=self, n=(self.w//3 * self.h), level=1)
        i = 0
        j = 0
        # Positionner les agents de radioactivité de niveau 1 sur la grille
        for agent in self.agents_by_type[type(Radioactivity(Model()))]:
            self.grid.place_agent(agent, (i % w, j % h))
            j += 1
            if j % h == 0:
                i += 1

        # Placement de la radioactivité niveau 2
        Radioactivity.create_agents(model=self, n=(self.w//3 * self.h), level=2)
        for agent in self.agents_by_type[type(Radioactivity(Model()))]:
            if agent.get_radioactivity_level() == 2:    
                self.grid.place_agent(agent, (i % w, j % h))
                j += 1
                if j % h == 0:
                    i += 1

        # Placement de la radioactivité niveau 3
        Radioactivity.create_agents(model=self, n=(self.w//3 * self.h), level=3)
        for agent in self.agents_by_type[type(Radioactivity(Model()))]:
            if agent.get_radioactivity_level() == 3:    
                self.grid.place_agent(agent, (i % w, j % h))
                j += 1
                if j % h == 0:
                    i += 1

        # Création et placement des Robots de différentes couleurs
        GreenRobotAgent.create_agents(self, n=self.n_agents_g)
        YellowRobotAgent.create_agents(self, n=self.n_agents_y)
        RedRobotAgent.create_agents(self, n=self.n_agents_r)

        # Garder une trace des positions déjà occupées
        used_positions = set()
        # Garder une trace des lignes utilisées par niveau
        used_lines_by_level = {1: set(), 2: set(), 3: set()}

        # Regrouper les robots par niveau
        robots_by_level = {1: [], 2: [], 3: []}
        for agent in self.agents:
            if isinstance(agent, RobotAgent):
                robots_by_level[agent.get_level()].append(agent)

        # Placer les robots niveau par niveau
        for level in [1, 2, 3]:
            robots = robots_by_level[level]
            n_robots = len(robots)
            
            # Vérifier qu'il y a assez de lignes disponibles
            if n_robots > h:
                raise ValueError(f"Trop de robots de niveau {level} ({n_robots}) pour la hauteur de la grille ({h})")
            
            # Pré-sélectionner des lignes disponibles pour ce niveau
            available_lines = list(range(h))
            random.shuffle(available_lines)  # Mélanger les lignes disponibles
            selected_lines = available_lines[:n_robots]  # Prendre autant de lignes que de robots
            
            # Placer chaque robot sur une ligne différente
            for i, robot in enumerate(robots):
                h_r = selected_lines[i]  # Utiliser une ligne unique pour chaque robot
                while True:
                    w_r = random.randint((level - 1) * (w // 3), level * (w // 3) - 1)
                    pos = (w_r, h_r)
                    if pos not in used_positions:
                        self.grid.place_agent(robot, pos)
                        used_positions.add(pos)
                        used_lines_by_level[level].add(h_r)
                        break

        # Assigner les zones verticales aux robots

        # Création des déchets pour chaque niveau
        Waste.create_agents(self, n=self.n_waste_g, level=1)
        Waste.create_agents(self, n=self.n_waste_y, level=2)
        Waste.create_agents(self, n=self.n_waste_r, level=3)

        # Placement des déchets sur la grille
        for agent in self.agents_by_type[type(Waste(Model()))]:
            lvl = agent.get_level()
            w_w = random.randint((lvl - 1) * (w // 3), lvl * (w // 3) - 1)
            h_w = random.randint(0, h - 1)
            self.grid.place_agent(agent, (w_w, h_w))

        # Création et placement de la zone de dépôt (disposal zone) sur la dernière colonne
        DisposalZone.create_agents(self, n=self.h)
        h_dz = 0
        for agent in self.agents_by_type[type(DisposalZone(Model()))]:
            self.grid.place_agent(agent, (w - 1, h_dz))
            h_dz += 1

    def perform_action(self, agent, action):
        # Exécute une action donnée pour un agent
        if action == "PICK":
            # Ramasser le déchet présent sur la case
            waste = [w for w in self.grid.get_cell_list_contents([agent.pos]) if isinstance(w, Waste)][0]
            if waste.get_level()<3:
                agent.inventory.append(waste)
            else:
                agent.ready_to_deliver.append(waste)
            self.grid.remove_agent(waste)
        
        elif action == "DROP":
            # Déposer le déchet traité
            waste = agent.ready_to_deliver.pop()
            self.grid.place_agent(waste, agent.pos)
        
        elif action == "TRADE":
            waste = agent.inventory.pop()
            self.grid.place_agent(waste, agent.pos)

        else:
            # Déplacer l'agent vers une nouvelle position
            self.grid.move_agent(agent, get_new_pos(agent.pos, action))
    
    def process_waste(self, waste1, waste2):
        # Traiter deux déchets de même niveau pour créer un déchet de niveau supérieur
        if waste1.get_level() == waste2.get_level():
            w = Waste.create_agents(self, 1, level=(waste1.get_level() + 1))
            waste1.remove()
            waste2.remove()
        return w[0]
    
    def destroy_waste(self):
        for i in range(self.h):
            disposal_zone_contents = self.grid.get_cell_list_contents([(self.w-1,i)])
            for dz_cont in disposal_zone_contents:
                if isinstance(dz_cont,Waste):
                    self.grid.remove_agent(dz_cont)
                    dz_cont.remove()
    
    def step(self):
        # Distribuer les messages en attente
        self.message_service.dispatch_messages()
        
        # Avancer d'une étape pour tous les agents
        if len(self.agents_by_type[type(Waste(Model()))]):
            self.destroy_waste()
            self.agents.shuffle_do("step")
            self.datacollector.collect(self)