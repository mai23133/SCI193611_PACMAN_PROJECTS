from pacman_module.game import Agent
from pacman_module.pacman import Directions


def key(state):
    """
    Returns a key that uniquely identifies a Pacman game state.

    Arguments:
    ----------
    - `state`: the current game state. See FAQ and class
               `pacman.GameState`.

    Return:
    -------
    - A hashable key object that uniquely identifies a Pacman game state.
    """

    return (state.getPacmanPosition(), tuple(state.getFood().asList()),
            tuple(sorted(state.getCapsules())))


class PacmanAgent(Agent):
    """
    A Pacman agent based on Depth-First-Search.
    """

    def __init__(self, args):
        """
        Arguments:
        ----------
        - `args`: Namespace of arguments from command-line prompt.
        """
        self.moves = []

    def get_action(self, state):
        """
        Given a pacman game state, returns a legal move.

        Arguments:
        ----------
        - `state`: the current game state. See FAQ and class
                   `pacman.GameState`.

        Return:
        -------
        - A legal move as defined in `game.Directions`.
        """

        if not self.moves:
            self.moves = self.dfs(state)

        try:
            return self.moves.pop(0)

        except IndexError:
            return Directions.STOP

    def dfs(self, state):
        """
        Given a pacman game state,
        returns a list of legal moves to solve the search layout.

        Arguments:
        ----------
        - `state`: the current game state. See FAQ and class
                   `pacman.GameState`.

        Return:
        -------
        - A list of legal moves as defined in `game.Directions`.
        """

        frontier = [(state, [])]
        visited = set()
        while frontier:
            current, path = frontier.pop()
            if current.isWin() or current.getNumFood() == 0:
                return path
            current_key = key(current)
            if current_key in visited:
                continue
            visited.add(current_key)
            for successor, action in current.generatePacmanSuccessors():
                if not successor.isLose():
                    frontier.append((successor, path + [action]))
        raise ValueError("No route can collect all food")
