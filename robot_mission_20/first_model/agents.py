"""
Groupe 20 - 11/03/2025 - Vogels Arthur, Pierre Glerant
Module contenant la classe RobotAgent.
"""

# Importation des modules
import random
from mesa import Agent

# Définition de la classe RobotAgent
class RobotAgent(Agent):
    """
    Agent robot qui se déplace selon son inventaire et les directions possibles.
    
    Comportement :
    - Si l'inventaire n'est pas plein (None) : choisit aléatoirement parmi
      la liste des directions possibles.
    - Si l'inventaire est plein (différent de None) : se déplace obligatoirement vers l'Est ("E")
      si cette direction est disponible ; sinon, il ne se déplace pas.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # L'inventaire indique le déchet transporté, None signifie inventaire vide.
        self.inventory = None

    def step(self):
        # Récupère la liste des directions possibles pour le déplacement, par exemple ["E", "NE", ...]
        possible_moves = self.model.get_possible_moves(self)
        
        if self.inventory is None:
            # Inventaire vide : déplacement aléatoire parmi les cases possibles.
            if possible_moves:
                chosen_move = random.choice(possible_moves)
                self.model.move_agent_direction(self, chosen_move)
        else:
            # Inventaire plein : déplacement forcé vers l'Est ("E") si possible.
            if "E" in possible_moves:
                self.model.move_agent_direction(self, "E")
            else:
                # Si "E" n'est pas disponible, l'agent ne se déplace pas.
                pass
