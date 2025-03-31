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
    def __init__(self,n_agents=1, n_zone=3, n_waste=2, w=16, h=10, seed=None):
        super().__init__(seed=seed)
        
        self.n_agents = n_agents
        self.n_zone = n_zone
        self.n_waste = n_waste
        self.w = w # nombre de colones
        self.h = h # nombre de lignes

        # Mise en place de la MultiGrid
        self.grid = MultiGrid(self.w, self.h, torus = False)

        # Placement de la radioactivité
        Radioactivity.create_agents(model=self, n=(self.w//3*self.h), level=1)
        i = 0
        j = 0
        for agent in self.agents_by_type[type(Radioactivity(Model()))]:
            self.grid.place_agent(agent,(i%w, j%h))
            j += 1
            if j % h == 0:
                i += 1

        Radioactivity.create_agents(model=self, n=(self.w//3*self.h), level=2)
        for agent in self.agents_by_type[type(Radioactivity(Model()))]:
            if agent.get_radioactivity_level() == 2:    
                self.grid.place_agent(agent,(i%w, j%h))
                j += 1
                if j % h == 0:
                    i += 1

        Radioactivity.create_agents(model=self, n=(self.w//3*self.h), level=3)
        for agent in self.agents_by_type[type(Radioactivity(Model()))]:
            if agent.get_radioactivity_level() == 3:    
                self.grid.place_agent(agent,(i%w, j%h))
                j += 1
                if j % h == 0:
                    i += 1

        # Placement des Robots
        GreenRobotAgent.create_agents(self, n=self.n_agents)
        YellowRobotAgent.create_agents(self,n=self.n_agents)
        RedRobotAgent.create_agents(self,n=self.n_agents)

        for agent in self.agents:
            if isinstance(agent,RobotAgent):
                lvl = agent.get_level()
                w_r = random.randint((lvl-1)*(w//3),lvl*(w//3) - 1)
                h_r = random.randint(0,h-1)
                self.grid.place_agent(agent,(w_r,h_r))

        # Placement des déchets
        Waste.create_agents(self,n = self.n_waste, level = 1)
        Waste.create_agents(self,n = self.n_waste, level = 2)
        Waste.create_agents(self,n = self.n_waste, level = 3)

        for agent in self.agents_by_type[type(Waste(Model()))]:
            lvl = agent.get_level()
            w_w = random.randint((lvl-1)*(w//3),lvl*(w//3) - 1)
            h_w = random.randint(0,h-1)
            self.grid.place_agent(agent,(w_w,h_w))

        # Placement de la disposal zone
        DisposalZone.create_agents(self, n = self.h)
        h_dz = 0
        for agent in self.agents_by_type[type(DisposalZone(Model()))]:
            self.grid.place_agent(agent,(w-1,h_dz))
            h_dz += 1

    def perform_action(self, agent, action):
        if action == "PICK":
            waste = [w for w in self.grid.get_cell_list_contents([agent.pos]) if isinstance(w,Waste)][0]
            agent.inventory.append(waste)
            self.grid.remove_agent(waste)
        
        elif action == "DROP":
            waste = agent.ready_to_deliver.pop()
            self.grid.place_agent(waste,agent.pos)

        else:
            self.grid.move_agent(agent,get_new_pos(agent.pos,action))
    
    def process_waste(self,waste1,waste2):
        if waste1.get_level() == waste2.get_level():
            w = Waste.create_agents(self,1,level = (waste1.get_level()+1))
        return w[0]
    
    def step(self):
        self.agents.shuffle_do("step") 