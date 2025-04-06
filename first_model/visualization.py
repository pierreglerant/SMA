"""
Groupe 20 - 11/03/2025 - Vogels Arthur, Pierre Glerant
"""

import solara
from mesa import Model
from mesa.visualization import SolaraViz, make_space_component, make_plot_component
from mesa.visualization.utils import update_counter
from .model import RobotMission
from .agents import RobotAgent
from .objects import Radioactivity, Waste, DisposalZone
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

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
        "n_agents_g": {
            "type": "SliderInt",
            "value": 1,
            "label": "Number of green agents:",
            "min": 1,
            "max": 10,
            "step": 1
        },
        "n_agents_y": {
            "type": "SliderInt",
            "value": 1,
            "label": "Number of yellow agents:",
            "min": 1,
            "max": 10,
            "step": 1
        },
        "n_agents_r": {
            "type": "SliderInt",
            "value": 1,
            "label": "Number of red agents:",
            "min": 1,
            "max": 10,
            "step": 1
        },
        "n_waste_g": {
            "type": "SliderInt",
            "value": 4,
            "label": "Number of green wastes:",
            "min": 4,
            "max": 16,
            "step": 4
        },
        "n_waste_y": {
            "type": "SliderInt",
            "value": 4,
            "label": "Number of yellow wastes:",
            "min": 4,
            "max": 16,
            "step": 4
        },
        "n_waste_r": {
            "type": "SliderInt",
            "value": 4,
            "label": "Number of red wastes:",
            "min": 4,
            "max": 16,
            "step": 4
        },
    }
    # Création d'une instance du modèle RobotMission
    mod = RobotMission()
    # Création du composant de visualisation de la grille
    SpaceGraph = make_space_component(agent_portrayal)
    
    def post_process(ax):
        # Configure l'axe des ordonnées pour n'afficher que des entiers positifs
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.set_ylim(bottom=0)
    
    # Création du composant de graphique
    WastePlot = make_plot_component(
        "Number of wastes",
        post_process=post_process
    )

    # Retourne la visualisation Solara pour l'interface utilisateur
    return SolaraViz(
        mod,
        components=[SpaceGraph, WastePlot],
        model_params=model_params
    )
