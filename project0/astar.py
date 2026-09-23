"""Score-optimal A* using maze distances and a food spanning tree."""

from collections import deque
from heapq import heappop, heappush
from itertools import count

from pacman_module.game import Agent, Directions


def key(state):
    """Return a hashable configuration, excluding accumulated path score."""
    return (state.getPacmanPosition(), tuple(state.getFood().asList()),
            tuple(sorted(state.getCapsules())))


class PacmanAgent(Agent):
    """Minimize moves plus five points per consumed capsule, without ghosts."""

    def __init__(self, args=None):
        """Initialize the plan and per-layout distance/heuristic caches."""
        super().__init__()
        self.moves = deque()
        self.planned = False
        self.distances = {}
        self.trees = {}

    def prepare(self, state):
        """Compute shortest wall-respecting distances from each food cell."""
        self.distances.clear()
        self.trees.clear()
        walls = state.getWalls()
        for food in state.getFood().asList():
            distances = {food: 0}
            queue = deque([food])
            while queue:
                x, y = queue.popleft()
                for target in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                    tx, ty = target
                    if (0 <= tx < walls.width and 0 <= ty < walls.height
                            and not walls[tx][ty] and target not in distances):
                        distances[target] = distances[x, y] + 1
                        queue.append(target)
            self.distances[food] = distances

    def heuristic(self, state):
        """Return nearest-food distance plus the food MST (a lower bound)."""
        foods = tuple(state.getFood().asList())
        if not foods:
            return 0
        if foods not in self.trees:
            remaining = set(foods[1:])
            cheapest = {p: self.distances[foods[0]].get(p, float('inf'))
                        for p in remaining}
            weight = 0
            while remaining:
                nearest = min(remaining, key=cheapest.get)
                weight += cheapest[nearest]
                remaining.remove(nearest)
                for point in remaining:
                    cheapest[point] = min(
                        cheapest[point],
                        self.distances[nearest].get(point, float('inf')))
            self.trees[foods] = weight
        position = state.getPacmanPosition()
        return self.trees[foods] + min(
            self.distances[food].get(position, float('inf')) for food in foods)

    def search(self, state):
        """Return maximum-score winning actions; raise for unreachable food."""
        self.prepare(state)
        start = key(state)
        parents = {start: None}
        best = {start: 0}
        serial = count()
        frontier = [(self.heuristic(state), next(serial), 0, state)]
        while frontier:
            _, _, cost, current = heappop(frontier)
            current_key = key(current)
            if cost != best[current_key]:
                continue
            if current.isWin() or current.getNumFood() == 0:
                path = []
                while parents[current_key] is not None:
                    current_key, action = parents[current_key]
                    path.append(action)
                return path[::-1]
            for successor, action in current.generatePacmanSuccessors():
                if successor.isLose():
                    continue
                successor_key = key(successor)
                capsule_cost = 5 * (len(current.getCapsules())
                                    - len(successor.getCapsules()))
                new_cost = cost + 1 + capsule_cost
                if new_cost < best.get(successor_key, float('inf')):
                    best[successor_key] = new_cost
                    parents[successor_key] = (current_key, action)
                    heappush(frontier, (new_cost + self.heuristic(successor),
                                        next(serial), new_cost, successor))
        raise ValueError("No route can collect all food")

    def get_action(self, state):
        """Plan on the first call and return the next legal action."""
        if not self.planned:
            self.moves.extend(self.search(state))
            self.planned = True
        return self.moves.popleft() if self.moves else Directions.STOP
