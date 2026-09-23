# Complete this class for all parts of the project

from pacman_module.game import Agent
from pacman_module.pacman import Directions
from collections import Counter, deque
import numpy as np


class PacmanAgent(Agent):
    def __init__(self, args):
        """
        Arguments:
        ----------
        - `args`: Namespace of arguments from command-line prompt.
        """
        self.args = args
        self.blocked = set()
        self.visits = Counter()

    def get_action(self, state, belief_state):
        """
        Given a pacman game state and a belief state,
                returns a legal move.

        Arguments:
        ----------
        - `state`: the current game state. See FAQ and class
                   `pacman.GameState`.
        - `belief_state`: a list of probability matrices.

        Return:
        -------
        - A legal move as defined in `game.Directions`.
        """

        position = tuple(map(int, state.getPacmanPosition()))
        legal = state.getLegalActions(0)
        vectors = {Directions.NORTH: (0, 1), Directions.SOUTH: (0, -1),
                   Directions.EAST: (1, 0), Directions.WEST: (-1, 0)}
        self.visits[position] += 1
        for move, (dx, dy) in vectors.items():
            neighbor = (position[0]+dx, position[1]+dy)
            if move not in legal:
                self.blocked.add(neighbor)
        moves = [move for move in legal if move in vectors]
        if not moves or len(belief_state) == 0:
            return Directions.STOP
        mass = np.sum(belief_state, axis=0)
        width, height = mass.shape

        def utility(move):
            """Value a legal move using belief and locally discovered walls."""
            dx, dy = vectors[move]
            start = (position[0]+dx, position[1]+dy)
            distances = {start: 0}
            queue = deque([start])
            attraction = 0.0
            while queue:
                x, y = queue.popleft()
                distance = distances[x, y]
                attraction += mass[x, y] * np.exp(-distance/4)
                for vx, vy in vectors.values():
                    point = (x+vx, y+vy)
                    if (0 <= point[0] < width and 0 <= point[1] < height
                            and point not in self.blocked
                            and point not in distances):
                        distances[point] = distance+1
                        queue.append(point)
            return (attraction + 2*mass[start]
                    - 0.03*self.visits[start])

        return max(moves, key=utility)
