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

class RobotMission(Model):
    # Modèle
    def __init__(self, n_agents=1, n_zone=3, n_waste=2, w=16, h=10, seed=None):
        super().__init__(seed=seed)
        
        self.n_agents = n_agents  # Nombre d'agents par couleur
        self.n_zone = n_zone      # Nombre de zones de dépôt
        self.n_waste = n_waste    # Nombre de déchets par niveau
        self.w = w              # Nombre de colonnes
        self.h = h              # Nombre de lignes

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
        GreenRobotAgent.create_agents(self, n=self.n_agents)
        YellowRobotAgent.create_agents(self, n=self.n_agents)
        RedRobotAgent.create_agents(self, n=self.n_agents)

        # Placement des agents robots sur la grille selon leur niveau
        for agent in self.agents:
            if isinstance(agent, RobotAgent):
                lvl = agent.get_level()
                w_r = random.randint((lvl - 1) * (w // 3), lvl * (w // 3) - 1)
                h_r = random.randint(0, h - 1)
                self.grid.place_agent(agent, (w_r, h_r))

        # Création des déchets pour chaque niveau
        Waste.create_agents(self, n=self.n_waste, level=1)
        Waste.create_agents(self, n=self.n_waste, level=2)
        Waste.create_agents(self, n=self.n_waste, level=3)

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
            agent.inventory.append(waste)
            self.grid.remove_agent(waste)
        
        elif action == "DROP":
            # Déposer le déchet traité
            waste = agent.ready_to_deliver.pop()
            self.grid.place_agent(waste, agent.pos)

        else:
            # Déplacer l'agent vers une nouvelle position
            self.grid.move_agent(agent, get_new_pos(agent.pos, action))
    
    def process_waste(self, waste1, waste2):
        # Traiter deux déchets de même niveau pour créer un déchet de niveau supérieur
        if waste1.get_level() == waste2.get_level():
            w = Waste.create_agents(self, 1, level=(waste1.get_level() + 1))
        return w[0]
    
    def step(self):
        # Avancer d'une étape pour tous les agents
        self.agents.shuffle_do("step")
