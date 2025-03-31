"""
Groupe 20 - 11/03/2025 - Vogels Arthur, Pierre Glerant
"""

import solara
from mesa.visualization import SolaraViz, make_space_component
from .model import RobotMission
from .agents import RobotAgent
from .objects import Radioactivity, Waste, DisposalZone

def agent_portrayal(agent):
    # Définition de l'apparence de chaque agent selon son type et son niveau
    if isinstance(agent, Radioactivity):
        if agent.get_radioactivity_level() == 1:
            return {
                "color": "#00FF0080",
                "size": 500,
                "marker": "s",
            }
        elif agent.get_radioactivity_level() == 2:
            return {
                "color": "#FFFF0080",
                "size": 500,
                "marker": "s",
            }
        elif agent.get_radioactivity_level() == 3:
            return {
                "color": "#FF000080",
                "size": 500,
                "marker": "s",
            }
    
    if isinstance(agent, RobotAgent):
        if agent.get_level() == 1:
            return {
                "color": "green",
                "size": 100,
            }
        if agent.get_level() == 2:
            return {
                "color": "orange",
                "size": 100,
            }
        if agent.get_level() == 3:
            return {
                "color": "red",
                "size": 100,
            }
    
    if isinstance(agent, Waste):
        if agent.get_level() == 1:
            return {
                "color": "green",
                "size": 50,
                "marker": "X"
            }
        
        if agent.get_level() == 2:
            return {
                "color": "orange",
                "size": 50,
                "marker": "X"
            }
        
        if agent.get_level() == 3:
            return {
                "color": "red",
                "size": 50,
                "marker": "X"
            }
        
        if agent.get_level() == 4:
            return {
                "color": "black",
                "size": 50,
                "marker": "X"
            }
    
    if isinstance(agent, DisposalZone):
        return {
            "color": "#80808080",
            "size": 500,
            "marker": "s"
        }

@solara.component
def Page():
    # Paramètres du modèle configurables via l'interface Solara
    model_params = {
        "n_zone": 1,
        "n_agents": {
            "type": "SliderInt",
            "value": 1,
            "label": "Number of agents:",
            "min": 1,
            "max": 5,
            "step": 1
        },
        "n_waste": 1,
        "w": 10,
        "h": 10,
    }

    # Création d'une instance du modèle RobotMission
    mod = RobotMission()
    # Création du composant de visualisation de la grille
    SpaceGraph = make_space_component(agent_portrayal)

    # Retourne la visualisation Solara pour l'interface utilisateur
    return SolaraViz(
        mod,
        components=[SpaceGraph],
        model_params=model_params
    )
