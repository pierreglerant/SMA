"""
Groupe 20 - 11/03/2025 - Vogels Arthur, Pierre Glerant
"""

import solara
from .visualization import Page

# Définition des routes pour accéder à la page principale de la simulation
routes = [solara.Route(path="/", component=Page)]
