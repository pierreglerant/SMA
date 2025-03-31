from mesa import Agent
import random
from .utils import get_pos_delta, get_new_pos
from .objects import Radioactivity, Waste

class RobotAgent(Agent):
    
    def __init__(self, model):
        super().__init__(model)
        self.knowledge = lambda:0
        self.inventory = []
        self.ready_to_deliver = []
        self.inventory_full = False
        self.level = 0
        self.dir_w = 1
        self.dir_h = 1
    
    def __random_policy__(self):
        # If waste is in range, we move to that position
        if len(self.knowledge.close_waste.keys()) > 0:
            return random.choice(list(self.knowledge.close_waste.keys()))
        
        # Else, we follow a given policy
        return random.choice(self.knowledge.possible_moves)

    def __policy__(self):
        if (self.dir_w,0) in self.knowledge.possible_moves:
            return (self.dir_w,0)
        
        if (0,self.dir_h) in self.knowledge.possible_moves:
            self.dir_w = -self.dir_w
            return (0, self.dir_h)
        
        self.dir_h = -self.dir_h
        self.dir_w = -self.dir_w
        return (self.dir_w,0)

    def get_level(self):
        return self.level
    
    def process_waste(self):
        self.ready_to_deliver.append(self.model.process_waste(self.inventory.pop(), self.inventory.pop()))

    def perceive(self):
        if len(self.inventory) > 1:
            self.inventory_full = True
        else:
            self.inventory_full = False
            
        possible_moves = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=True
        )

        self.knowledge.neighbors = [get_pos_delta(self.pos,possible_step) for possible_step in possible_moves]

        self.knowledge.close_contents = {}
        for possible_step in self.knowledge.neighbors:
            self.knowledge.close_contents[possible_step] = self.model.grid.get_cell_list_contents([get_new_pos(self.pos,possible_step)])

        self.knowledge.possible_moves = list(self.knowledge.neighbors)
        if (1,0) in self.knowledge.neighbors:
            for a in self.knowledge.close_contents[(1,0)]:
                if isinstance(a,Radioactivity) and a.get_radioactivity_level() > self.level:
                    self.knowledge.possible_moves = list(set(self.knowledge.possible_moves) - set([(1,0),(1,-1),(1,1)]))

        for a in self.knowledge.close_contents[(0,0)]:
            if isinstance(a,Radioactivity) and a.get_radioactivity_level() < self.level:
                self.knowledge.possible_moves = list(set(self.knowledge.possible_moves) - set([(-1,0),(-1,-1),(-1,1)]))
                                    

    def deliberate(self):
        # If the inventory is full we process them into a more toxic one
        if self.inventory_full:
            self.process_waste()

        # If we have a toxic waste to deliver, we move to the right as long as we can and then drop
        if len(self.ready_to_deliver):
            if (1,0) in self.knowledge.possible_moves:
                return (1,0)
            
            else:
                return "DROP"
        
        # Detecting waste in range
        self.knowledge.close_waste = {}
        for k in self.knowledge.possible_moves:
            waste_list = [w for w in self.knowledge.close_contents[k] if isinstance(w,Waste) if w.get_level()==self.get_level()]
            if len(waste_list) > 0:
                self.knowledge.close_waste[k] = waste_list
        
        # If on a waste, we pick it up
        if (0,0) in self.knowledge.close_waste.keys() and not self.inventory_full:
            return "PICK"
        
        # Else, we follow a given policy
        return self.__policy__()  

    def step(self):
        self.perceive()
        action = self.deliberate()
        self.model.perform_action(self,action)

class GreenRobotAgent(RobotAgent):
    def __init__(self, model):
        super().__init__(model)
        self.level = 1

class YellowRobotAgent(RobotAgent):
    def __init__(self, model):
        super().__init__(model)
        self.level = 2

class RedRobotAgent(RobotAgent):
    def __init__(self, model):
        super().__init__(model)
        self.level = 3 