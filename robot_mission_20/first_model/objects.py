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
    def __init__(self, unique_id, model, color="green"):
        super().__init__(unique_id, model)
        self.color = color

    def step(self):
        """
        Méthode exécutée à chaque pas de temps.
        Pour cet agent statique, aucune action n'est effectuée.
        """
        pass

    def __repr__(self):
        return f"WasteAgent(id={self.unique_id}, color={self.color})"