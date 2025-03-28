import mesa
from mesa import Agent, Model
from mesa.space import MultiGrid
import random
from agents import RobotAgent
from objects import WasteAgent, RadioactivityAgent, WasteDisposalZone



def compute_delta(old_pos, new_pos):
    return [new_pos[0]-old_pos[0], new_pos[1]-old_pos[1]]

def pos2letter(old_pos, new_pos):
    l2p_dict = {"E": [0,1], "NE": [-1,1], "N": [-1,0], "NW": [-1,-1],
                "W": [0,-1], "SW": [1,-1], "S": [1,0], "SE": [1,1]}
    p2l_dict = {l2p_dict[k]: k for k in l2p_dict.keys()}

    return p2l_dict(compute_delta(old_pos,new_pos))


class RobotMission(Model):
    def __init__(self,n_zone=1,n_agents=1,n_waste=1,h=10,w=10,seed=None):
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
        RobotAgent.create_agents(model=self,n=self.n_agents)
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
        RadioactivityAgent.create_agents(model=self,n=self.w * self.h)
        i = 0
        j = 0
        for agent in self.agents:
            if isinstance(agent,RadioactivityAgent):
                self.grid.place_agent(agent,(i%h,j%w))
                i += 1
                if i % h == 0:
                    j += 1

    def get_possible_move(self,agent):
        possible_steps = self.grid.get_neighborhood(agent.pos, moore=True, include_center=False)

# move_agent_direction
# get_possible_move