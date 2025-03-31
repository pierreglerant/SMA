from mesa import Agent

class Radioactivity(Agent):
    def __init__(self,model, level = 1):
        super().__init__(model)
        self.level = level

    def get_radioactivity_level(self):
        return self.level
    
    def step(self):
        pass

class Waste(Agent):
    def __init__(self, model, level = 1):
        super().__init__(model)
        self.level = level
    
    def get_level(self):
        return self.level
    
    def step(self):
        pass

class DisposalZone(Agent):
    def __init__(self,model):
        super().__init__(model)
    
    def step(self):
        pass 