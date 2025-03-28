import solara
import mesa
from mesa.visualization import SolaraViz, make_space_component
from model import RobotMission
from agents import RobotAgent
from objects import WasteAgent

def robot_agent_portrayal(agent):
    return {
        "color": "tab:blue",
        "size":50,
    }

model_params = {
    "n_agents": {
        "type": "SliderInt",
        "value": 50,
        "label": "Number of agents",
        "min": 1,
        "max": 5,
        "step": 1,
    },
    "width": 10,
    "height": 10
}

mod = RobotMission(1,1,1,10,10)

SpaceGraph = make_space_component(robot_agent_portrayal)

page = SolaraViz(
    mod,
    components=[SpaceGraph],
    model_params=model_params)