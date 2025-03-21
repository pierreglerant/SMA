import mesa
from mesa import Agent, Model
from mesa.space import MultiGrid
import random
from agents import WasteAgent, Radioactivity, WasteDisposalZone, GreenAgent

class RobotMission(Model):
    def __init__(self,n_zone,n_agents,n_waste,h,w,seed=None):
        super().__init__(seed=seed)

        # Initialisation des veriables d'environnement
        self.n_agents = n_agents
        self.n_zone = n_zone
        self.n_waste = n_waste
        self.h = h
        self.w = w

        # Creation de la grid
        self.grid = MultiGrid(self.h, self.w, torus = False)
        
        # Creation des agents robots
        GreenAgent.create_agents(model=self,n=self.n_agents)
        for agent in self.agents:
            x = random.randint(0,w-1)
            y = random.randint(0,h-1)
            
            self.grid.place_agent(agent, (y,x))
        
        # Creation des agents déchets
        WasteAgent.create_agents(model=self,n = self.n_waste)
        for agent in self.agents:
            if isinstance(agent,WasteAgent):
                x = random.randint(0,w-1)
                y = random.randint(0,h-1)
            
                self.grid.place_agent(agent, (y,x))

        # Creation des agents zone de dépot
        WasteDisposalZone.create_agents(model=self,n = self.h)
        i = 0
        for agent in self.agents:
            if isinstance(agent, WasteDisposalZone):
                self.grid.place_agent(agent,(i,w-1))
                i += 1
        
        # Creation des agents radioactivité
        Radioactivity.create_agents(model=self,n=self.w * self.h)
        i = 0
        j = 0
        for agent in self.agents:
            if isinstance(agent,Radioactivity):
                self.grid.place_agent(agent,(i%h,j%w))
                i += 1
                if i % h == 0:
                    j += 1

# move_agent_direction
# get_possible_move