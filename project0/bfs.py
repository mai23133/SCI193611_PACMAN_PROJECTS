"""Breadth-first graph search: minimize the number of Pacman moves."""

from collections import deque

from pacman_module.game import Agent, Directions


def key(state):
    """Return immutable position, food and capsule data for a game state."""
    return (state.getPacmanPosition(), tuple(state.getFood().asList()),
            tuple(sorted(state.getCapsules())))


class PacmanAgent(Agent):
    """Plan once with a FIFO frontier, then execute the recovered path."""

    def __init__(self, args=None):
        """Initialize an empty plan; args is accepted by the runner."""
        super().__init__()
        self.moves = deque()
        self.planned = False

    def search(self, state):
        """Return shortest legal actions, or raise for unreachable food."""
        start = key(state)
        parents = {start: None}
        frontier = deque([(state, start)])
        while frontier:
            current, current_key = frontier.popleft()
            if current.isWin() or current.getNumFood() == 0:
                path = []
                while parents[current_key] is not None:
                    current_key, action = parents[current_key]
                    path.append(action)
                return path[::-1]
            for successor, action in current.generatePacmanSuccessors():
                successor_key = key(successor)
                if successor_key not in parents and not successor.isLose():
                    parents[successor_key] = (current_key, action)
                    frontier.append((successor, successor_key))
        raise ValueError("No route can collect all food")

    def get_action(self, state):
        """Return the next planned action, or STOP after the plan finishes."""
        if not self.planned:
            self.moves.extend(self.search(state))
            self.planned = True
        return self.moves.popleft() if self.moves else Directions.STOP
