"""Independent shortest-cost references and real layout regressions."""

import importlib
from heapq import heappop, heappush
from itertools import count

import pytest


def reference(state, weighted):
    """Solve using coordinate transitions, independently of agent code."""
    start = (state.getPacmanPosition(), frozenset(state.getFood().asList()),
             frozenset(state.getCapsules()))
    walls = state.getWalls()
    serial = count()
    heap = [(0, next(serial), start)]
    best = {start: 0}
    while heap:
        cost, _, node = heappop(heap)
        position, food, capsules = node
        if not food:
            return cost
        if cost != best[node]:
            continue
        x, y = position
        for point in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            px, py = point
            if walls[px][py]:
                continue
            child = (point, food - {point}, capsules - {point})
            new_cost = cost + 1 + (5 if weighted and point in capsules else 0)
            if new_cost < best.get(child, float('inf')):
                best[child] = new_cost
                heappush(heap, (new_cost, next(serial), child))
    return float('inf')


@pytest.mark.parametrize('agent_name', ['bfs', 'astar'])
@pytest.mark.parametrize('text', [
    ['%%%%%%%', '%P o .%', '%     %', '%%%%%%%'],
    ['%%%%%%%', '%P . .%', '% %%% %', '% .   %', '%%%%%%%'],
    ['%%%%%', '%P .%', '%%%%%'],
])
def test_optimal_against_independent_reference(project, agent_name, text):
    module, state = project(0, agent_name, text)
    weighted = agent_name == 'astar'
    optimum = reference(state, weighted)
    actions = module.PacmanAgent().search(state)
    cost = 0
    for action in actions:
        assert action in state.getLegalActions(0)
        successor = state.generateSuccessor(0, action)
        capsules = len(state.getCapsules()) - len(successor.getCapsules())
        cost += 1 + (5*capsules if weighted else 0)
        state = successor
    assert state.isWin()
    assert cost == optimum


def test_capsule_cost_changes_optimal_route(project):
    bfs, state = project(
        0, 'bfs', ['%%%%%%%', '%P o .%', '%     %', '%%%%%%%'])
    astar = importlib.import_module('astar')
    assert len(bfs.PacmanAgent().search(state)) == 4
    assert len(astar.PacmanAgent().search(state)) == 6


@pytest.mark.parametrize('agent_name', ['bfs', 'astar', 'dfs'])
def test_unreachable_food(project, agent_name):
    module, state = project(0, agent_name,
                            ['%%%%%%%', '%P% . %', '%%%%%%%'])
    agent = module.PacmanAgent(None)
    with pytest.raises(ValueError, match='No route'):
        agent.get_action(state)


def test_astar_bound(project):
    module, state = project(0, 'astar')
    agent = module.PacmanAgent()
    agent.prepare(state)
    assert 0 <= agent.heuristic(state) <= reference(state, True)
    for successor, _ in state.generatePacmanSuccessors():
        cost = 1 + 5*(len(state.getCapsules())-len(successor.getCapsules()))
        assert agent.heuristic(state) <= cost + agent.heuristic(successor)
