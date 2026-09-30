"""Extend confused-ghost tracking at variance four on both supplied maps."""

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'project2'))

from experiments import run_case  # noqa: E402


def measure(case):
    """Return trial curves and paired tail-window statistics for one map."""
    layout, steps = case
    curves, summary = run_case(layout, 'confused', 4, 30, steps, 3, 193611)
    return layout, curves, summary


def main():
    """Save an independent extension without overwriting the main study."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--steps', type=int, default=27000)
    args = parser.parse_args()
    if args.steps < 9000:
        parser.error('Use at least 9000 steps')
    output = ROOT / 'project2/results'
    layouts = ('large_filter', 'large_filter_walls')
    curves, scenarios = {}, {}
    # Practical tolerances fixed before examining the extended results.
    tolerances = {'entropy': 0.05, 'brier': 0.01}
    with ProcessPoolExecutor(max_workers=2) as pool:
        for layout, values, summary in pool.map(
                measure, [(name, args.steps) for name in layouts]):
            curves[layout] = values
            stable = all(abs(summary[name]['tail_change'])
                         + summary[name]['tail_change_ci95'] <= tolerance
                         for name, tolerance in tolerances.items())
            scenarios[layout] = {'metrics': summary,
                                 'within_tolerance': stable}
            print(f'{layout}: within tolerance = {stable}', flush=True)
    np.savez_compressed(output / 'high-noise-check.npz', **curves)
    data = {'configuration': {
        'steps': args.steps, 'trials': 30, 'ghosts': 3, 'seed': 193611,
        'policy': 'confused', 'variance': 4, 'tail_window': args.steps//3,
        'pacman': 'stationary', 'capture': False,
        'tolerances': tolerances,
        'criterion': 'abs(paired tail change) + CI95 <= tolerance',
    }, 'scenarios': scenarios}
    (output / 'high-noise-check.json').write_text(
        json.dumps(data, indent=2) + '\n')


if __name__ == '__main__':
    main()
