"""Exact minimax on a finite cyclic game graph, for one ghost, no capsules."""

from collections import defaultdict, deque
from heapq import heappop, heappush
from itertools import count

from pacman_module.game import Agent, Directions


def key(state, turn):
    """Identify a configuration and player, independent of elapsed time."""
    return (state.getPacmanPosition(), tuple(state.getFood().asList()),
            state.getGhostPosition(1), state.getGhostDirection(1), turn,
            state.isWin(), state.isLose())


class PacmanAgent(Agent):
    """Solve the full graph by retrograde minimax, including repeated states.

    Cycles need no arbitrary search depth or recursion-stack cutoff.
    """

    def __init__(self):
        """Initialize a policy cache for the reachable game graph."""
        super().__init__()
        self.policy = {}
        self.values = {}

    def solve(self, initial):
        """Compute exact worst-case cost and actions for all reachable states.

        Cost is moves + 1000 on loss + 10 per food left on loss.
        Maximizing score is equivalent to minimizing this nonnegative cost.
        The ghost maximizes cost. Infinite play has infinite cost.
        """
        if initial.getCapsules():
            raise ValueError("Exact minimax supports the capsule-free task")
        root = key(initial, 0)
        queue = deque([(initial, 0)])
        seen = {root}
        predecessors = defaultdict(list)
        outgoing = {}
        remaining = {}
        worst = defaultdict(float)
        serial = count()
        heap = []
        while queue:
            state, turn = queue.popleft()
            node = key(state, turn)
            if state.isWin() or state.isLose():
                cost = 0 if state.isWin() else 1000 + 10 * state.getNumFood()
                heappush(heap, (cost, next(serial), node))
                outgoing[node] = []
                continue
            successors = (state.generatePacmanSuccessors() if turn == 0
                          else state.generateGhostSuccessors(1))
            outgoing[node] = []
            for successor, action in successors:
                child = key(successor, 1-turn)
                outgoing[node].append((child, action))
                predecessors[child].append((node, 1 if turn == 0 else 0))
                if child not in seen:
                    seen.add(child)
                    queue.append((successor, 1-turn))
            remaining[node] = len(successors)

        values = {}
        while heap:
            value, _, node = heappop(heap)
            if node in values:
                continue
            values[node] = value
            for parent, edge_cost in predecessors[node]:
                if parent in values:
                    continue
                candidate = value + edge_cost
                if parent[4] == 0:
                    heappush(heap, (candidate, next(serial), parent))
                else:
                    remaining[parent] -= 1
                    worst[parent] = max(worst[parent], candidate)
                    if remaining[parent] == 0:
                        heappush(heap, (worst[parent], next(serial), parent))
        self.values = {node: values.get(node, float('inf')) for node in seen}
        self.policy = {}
        for node, edges in outgoing.items():
            if node[4] == 0 and edges:
                self.policy[node] = min(
                    edges, key=lambda edge: self.values[edge[0]])[1]

    def get_action(self, state):
        """Return an exact minimax action for the current observed state."""
        if state.isWin() or state.isLose():
            return Directions.STOP
        node = key(state, 0)
        if node not in self.policy:
            self.solve(state)
        return self.policy.get(node, Directions.STOP)
