"""
Groupe 20 - 11/03/2025 - Vogels Arthur, Pierre Glerant
"""

from mesa import Agent

class Radioactivity(Agent):
    # Agent représentant une zone de radioactivité
    def __init__(self, model, level=1):
        super().__init__(model)
        self.level = level

    def get_radioactivity_level(self):
        # Retourne le niveau de radioactivité
        return self.level
    
    def step(self):
        # Aucune action définie pour la radioactivité
        pass

class Waste(Agent):
    # Agent représentant un déchet toxique
    def __init__(self, model, level=1):
        super().__init__(model)
        self.level = level
    
    def get_level(self):
        # Retourne le niveau de toxicité du déchet
        return self.level
    
    def step(self):
        # Aucune action définie pour le déchet
        pass

class DisposalZone(Agent):
    # Agent représentant la zone de dépôt des déchets traités
    def __init__(self, model):
        super().__init__(model)
    
    def step(self):
        # Aucune action définie pour la zone de dépôt
        pass
