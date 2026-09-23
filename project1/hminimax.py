"""Depth-limited minimax with alpha-beta pruning and maze-aware evaluation."""

from collections import Counter, deque

from pacman_module.game import Agent, Directions


class PacmanAgent(Agent):
    """Replan against all legal ghost moves using a bounded search horizon."""

    def __init__(self, depth=4):
        """Use depth complete Pacman/ghost rounds (default four)."""
        super().__init__()
        self.depth = depth
        self.distances = {}
        self.visits = Counter()
        self.cache = {}

    def distance_map(self, state, source):
        """Return cached shortest maze distances from source to free cells."""
        if source not in self.distances:
            walls = state.getWalls()
            distances = {source: 0}
            queue = deque([source])
            while queue:
                x, y = queue.popleft()
                for point in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                    px, py = point
                    if (0 <= px < walls.width and 0 <= py < walls.height
                            and not walls[px][py] and point not in distances):
                        distances[point] = distances[x, y] + 1
                        queue.append(point)
            self.distances[source] = distances
        return self.distances[source]

    def evaluate(self, state):
        """Score leaves using food progress, maze distance and ghost danger."""
        score = state.getScore()
        if state.isWin():
            return 100000 + score
        if state.isLose():
            return -100000 + score
        position = state.getPacmanPosition()
        foods = tuple(state.getFood().asList())
        distances = self.distance_map(state, position)
        nearest = min((distances.get(p, 10000) for p in foods), default=0)
        ghost_distance = distances.get(state.getGhostPosition(1), 10000)
        danger = 12.0 / max(ghost_distance, 0.5)
        repeats = self.visits[position, foods]
        return score - 12*len(foods) - 2*nearest - danger - 2*repeats

    def value(self, state, depth, turn, alpha, beta):
        """Return a minimax value or a valid alpha-beta cutoff bound."""
        if state.isWin() or state.isLose() or depth == 0:
            return self.evaluate(state)
        node = (state.getPacmanPosition(), tuple(state.getFood().asList()),
                state.getGhostPosition(1), state.getGhostDirection(1),
                state.getScore(), depth, turn)
        if node in self.cache:
            return self.cache[node]
        successors = (state.generatePacmanSuccessors() if turn == 0
                      else state.generateGhostSuccessors(1))
        if not successors:
            return self.evaluate(state)
        successors.sort(key=lambda pair: self.evaluate(pair[0]),
                        reverse=turn == 0)
        result = -float('inf') if turn == 0 else float('inf')
        original_alpha, original_beta = alpha, beta
        for successor, _ in successors:
            child = self.value(successor, depth-(turn == 1), 1-turn,
                               alpha, beta)
            if turn == 0:
                result = max(result, child)
                alpha = max(alpha, result)
            else:
                result = min(result, child)
                beta = min(beta, result)
            if alpha >= beta:
                break
        # Only exact values may be reused as exact transposition entries.
        if original_alpha < result < original_beta:
            self.cache[node] = result
        return result

    def get_action(self, state):
        """Choose a legal action by searching depth complete rounds."""
        if state.isWin() or state.isLose():
            return Directions.STOP
        self.visits[state.getPacmanPosition(),
                    tuple(state.getFood().asList())] += 1
        self.cache.clear()
        successors = state.generatePacmanSuccessors()
        successors.sort(key=lambda pair: self.evaluate(pair[0]), reverse=True)
        best, action = -float('inf'), Directions.STOP
        for successor, move in successors:
            value = self.value(successor, self.depth, 1,
                               best, float('inf'))
            if value > best:
                best, action = value, move
        return action
