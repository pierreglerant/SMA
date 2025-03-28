"""
Groupe 20 - 11/03/2025 - Vogels Arthur, Pierre Glerant
Module contenant la classe Object.
"""

# Importation des modules
from mesa import Agent

# Définition de la classe Object
class WasteAgent(Agent):
    """
    Agent représentant un déchet (waste) dans le modèle.
    Par défaut, la couleur est "green".
    """
    def __init__(self, model, color="green"):
        super().__init__(model)
        self.color = color

    def step(self):
        """
        Méthode exécutée à chaque pas de temps.
        Pour cet agent statique, aucune action n'est effectuée.
        """
        pass

    def __repr__(self):
        return f"WasteAgent(id={self.unique_id}, color={self.color})"
    
class RadioactivityAgent(Agent):
    def __init__(self, model):
        super().__init__(model)

        self.radioactivity = 1

class WasteDisposalZone(Agent):
    def __init__(self, model):
        super().__init__(model)