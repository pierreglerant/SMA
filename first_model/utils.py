"""
Groupe 20 - 11/03/2025 - Vogels Arthur, Pierre Glerant
"""

def get_pos_delta(curr_pos, next_pos):
    # Calcule la différence (delta) entre la position actuelle et la prochaine position
    return (next_pos[0] - curr_pos[0], next_pos[1] - curr_pos[1])

def get_new_pos(curr_pos, delta):
    # Calcule une nouvelle position à partir de la position actuelle et d'un delta
    return (curr_pos[0] + delta[0], curr_pos[1] + delta[1])
