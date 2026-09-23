"""Check exact cyclic minimax and alpha-beta against independent recursion."""

from functools import lru_cache

import pytest


def test_exact_minimax_bellman_and_worst_case(project):
    module, state = project(1, 'minimax', ghosts=1)
    agent = module.PacmanAgent()
    agent.solve(state)
    assert agent.values[module.key(state, 0)] == 4

    def play(current, rounds):
        """Branch over every legal ghost response to the computed policy."""
        if current.isWin() or current.isLose():
            return current.getScore()
        assert rounds > 0
        action = agent.get_action(current)
        successor = dict((a, s) for s, a in
                         current.generatePacmanSuccessors())[action]
        if successor.isWin() or successor.isLose():
            return successor.getScore()
        return min(play(child, rounds-1) for child, _ in
                   successor.generateGhostSuccessors(1))

    assert play(state, 20) == 516


@pytest.mark.parametrize('text', [
    ['%%%%%%%', '%P . G%', '%%%%%%%'],
    ['%%%%%%%', '%P G .%', '%%%%%%%'],
    ['%%%%%%%', '%P    %', '% %G% %', '% .   %', '%%%%%%%'],
])
def test_exact_matches_finite_horizon_reference(project, text):
    module, state = project(1, 'minimax', text, ghosts=1)
    agent = module.PacmanAgent()
    agent.solve(state)
    states = {module.key(state, 0): state}

    @lru_cache(None)
    def reference(node, horizon):
        """Finite-horizon minimax; unresolved leaves have infinite cost."""
        current = states[node]
        if current.isWin():
            return 0
        if current.isLose():
            return 1000 + 10*current.getNumFood()
        if horizon == 0:
            return float('inf')
        turn = node[4]
        children = (current.generatePacmanSuccessors() if turn == 0
                    else current.generateGhostSuccessors(1))
        costs = []
        for child, _ in children:
            child_key = module.key(child, 1-turn)
            states[child_key] = child
            costs.append((turn == 0) + reference(child_key, horizon-1))
        return (min(costs) if turn == 0 else max(costs))

    root = module.key(state, 0)
    assert agent.values[root] == reference(root, 80)


def test_alpha_beta_matches_unpruned_tree(project):
    module, state = project(1, 'hminimax', ghosts=1)
    agent = module.PacmanAgent(depth=2)

    def reference(current, depth, turn):
        """Evaluate the complete depth-limited tree without pruning/caching."""
        if current.isWin() or current.isLose() or depth == 0:
            return agent.evaluate(current)
        successors = (current.generatePacmanSuccessors() if turn == 0
                      else current.generateGhostSuccessors(1))
        values = [reference(s, depth-(turn == 1), 1-turn)
                  for s, _ in successors]
        return max(values) if turn == 0 else min(values)

    expected = reference(state, 2, 0)
    actual = agent.value(state, 2, 0, -float('inf'), float('inf'))
    assert actual == expected
