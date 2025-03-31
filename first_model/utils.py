"""
Groupe 20 - 11/03/2025 - Vogels Arthur, Pierre Glerant
"""

def get_pos_delta(curr_pos, next_pos):
    return (next_pos[0] - curr_pos[0], next_pos[1] - curr_pos[1])

def get_new_pos(curr_pos, delta):
    return (curr_pos[0] + delta[0], curr_pos[1] + delta[1]) 