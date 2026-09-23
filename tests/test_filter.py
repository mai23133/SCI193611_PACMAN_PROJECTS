"""Validate probability models, multiple ghosts, recovery and API isolation."""

import ast
import hashlib
import json
import importlib
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def make_filter(project, policy='scared', variance=1):
    """Create an agent with a small real game grid and explicit arguments."""
    module, state = project(2, 'bayesfilter',
                            ['%%%%%%%', '%P    %', '%     %', '%    G%',
                             '%%%%%%%'], ghosts=1)
    agent = module.BeliefStateAgent(SimpleNamespace(
        ghostagent=policy, sensorvariance=variance))
    agent.walls = state.getWalls()
    return agent, state


@pytest.mark.parametrize('policy,bias', [
    ('confused', 1), ('afraid', 2), ('scared', 8),
])
def test_transition_normalization_and_bias(project, policy, bias):
    agent, state = make_filter(project, policy)
    transition = agent._get_transition_model((1, 3))
    for x in range(agent.walls.width):
        for y in range(agent.walls.height):
            total = transition[:, :, x, y].sum()
            assert total == pytest.approx(0 if agent.walls[x][y] else 1)
    assert transition[4, 2, 3, 2] / transition[2, 2, 3, 2] == bias
    assert transition[3, 2, 3, 2] == 0
    assert not np.allclose(transition, agent._get_transition_model((5, 1))) \
        or policy == 'confused'


@pytest.mark.parametrize('variance', [0, 0.25, 1, 4])
def test_sensor_distribution(project, variance):
    agent, state = make_filter(project, variance=variance)
    distance = 4
    values = [agent._get_sensor_model((1, 3), distance+k-agent.n/2)[3, 1]
              for k in range(agent.n+1)]
    assert sum(values) == pytest.approx(1)
    readings = np.arange(agent.n+1) + distance - agent.n/2
    assert np.dot(values, readings) == pytest.approx(distance)
    assert np.dot(values, (readings-distance)**2) == pytest.approx(agent.n/4)


def test_update_matches_dense_formula_and_eaten(project):
    agent, state = make_filter(project)
    free = np.logical_not(agent.walls.data).astype(float)
    prior = free/free.sum()
    transition = agent._get_transition_model((1, 3))
    expected = np.einsum('xyij,ij->xy', transition, prior)
    expected *= agent._get_sensor_model((1, 3), 4)
    expected /= expected.sum()
    beliefs = agent._get_updated_belief(
        [prior, prior], [4, 3], (1, 3), [False, True])
    np.testing.assert_allclose(beliefs[0], expected)
    assert beliefs[1].sum() == 0
    assert np.all(prior == free/free.sum())


def test_zero_prior_and_impossible_evidence(project):
    agent, state = make_filter(project)
    zero = np.zeros((agent.walls.width, agent.walls.height))
    for evidence in (3, 10000):
        result = agent._get_updated_belief([zero], [evidence], (1, 3), [False])
        assert result[0].sum() == pytest.approx(1)
        assert np.all(np.isfinite(result[0]))
        assert np.all(result[0][np.array(agent.walls.data)] == 0)


def test_bonus_uses_only_permitted_observations(project):
    agent, state = make_filter(project)
    controller = importlib.import_module('pacmanagent').PacmanAgent(None)

    class Observation:
        """Expose only the two permitted game-state queries."""

        def getPacmanPosition(self):
            return state.getPacmanPosition()

        def getLegalActions(self, index):
            return state.getLegalActions(index)

    belief = np.logical_not(agent.walls.data).astype(float)
    belief /= belief.sum()
    move = controller.get_action(Observation(), [belief])
    assert move in state.getLegalActions(0)


def test_protected_functions_unchanged():
    baseline = json.loads(
        (ROOT / 'tests/fixtures/protected_functions.json').read_text())
    edited = (ROOT / 'project2/bayesfilter.py').read_text()
    hashes = {}
    for node in ast.walk(ast.parse(edited)):
        if isinstance(node, ast.FunctionDef) and node.name in baseline:
            body = ast.dump(node, include_attributes=False).encode()
            hashes[node.name] = hashlib.sha256(body).hexdigest()
    assert hashes == baseline
