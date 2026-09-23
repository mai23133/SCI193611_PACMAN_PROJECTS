"""Load each project's independent pacman_module without name collisions."""

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def project(monkeypatch):
    """Return a loader; import only one project per test."""
    before = set(sys.modules)

    def load(number, agent=None, text=None, ghosts=0, args=None):
        """Return (agent module, initialized state) from a project fixture."""
        directory = ROOT / f'project{number}'
        monkeypatch.syspath_prepend(str(directory))
        pacman = importlib.import_module('pacman_module.pacman')
        layout = importlib.import_module('pacman_module.layout')
        module = importlib.import_module(agent) if agent else None
        if text is None:
            name = {0: 'small', 1: 'small_adv', 2: 'large_filter'}[number]
            text = (directory / 'pacman_module/layouts' / f'{name}.lay')
            text = text.read_text().splitlines()
        state = pacman.GameState()
        if number == 2:
            state.initialize(layout.Layout(text), ghosts,
                             edibleGhosts=True, beliefStateAgent=object())
        else:
            state.initialize(layout.Layout(text), ghosts)
        return module, state

    yield load
    for name in set(sys.modules) - before:
        module = sys.modules.get(name)
        filename = str(getattr(module, '__file__', ''))
        if any(str(ROOT / f'project{i}') in filename for i in range(3)):
            del sys.modules[name]
