"""Run the actual CLI entry points and record scores, timings and failures."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def cases():
    """Yield representative public layouts, all required policies and seeds."""
    for agent in ('bfs', 'astar', 'dfs'):
        for layout in ('small', 'medium', 'large'):
            yield 0, agent, layout, None, 1, [
                '--agentfile', f'{agent}.py', '--layout', layout,
                '--silentdisplay']
    for agent in ('minimax', 'hminimax'):
        layouts = ('small_adv',) if agent == 'minimax' else (
            'small_adv', 'medium_adv', 'large_adv')
        for layout in layouts:
            for ghost in ('dumby', 'greedy', 'smarty'):
                for seed in (1, 42):
                    yield 1, agent, layout, ghost, seed, [
                        '--agent', agent, '--layout', layout, '--ghost', ghost,
                        '--seed', str(seed), '--nographics']
    for layout in ('large_filter', 'large_filter_walls'):
        for ghost in ('confused', 'afraid', 'scared'):
            for seed in (1, 42):
                yield 2, 'pacmanagent', layout, ghost, seed, [
                    '--agentfile', 'pacmanagent.py', '--bsagentfile',
                    'bayesfilter.py', '--layout', layout,
                    '--ghostagent', ghost,
                    '--nghosts', '3', '--seed', str(seed), '--silentdisplay']


def run(case):
    """Execute one game under a timeout; return a JSON-compatible record."""
    project, agent, layout, ghost, seed, arguments = case
    command = [sys.executable, 'run.py', *arguments]
    row = dict(project=project, agent=agent, layout=layout, ghost=ghost,
               seed=seed, command=command)
    try:
        result = subprocess.run(command, cwd=ROOT / f'project{project}',
                                capture_output=True, text=True, timeout=90)
        output = result.stdout + result.stderr
        row.update(returncode=result.returncode, won='victorious' in output,
                   output=output)
        for name, pattern in {
            'score': r'(?:Total score|Score)\s*:\s*([-\d.]+)',
            'seconds': (r'(?:Total computation time \(seconds\)|'
                        r'Computation time)\s*:\s*([\d.e+-]+)'),
            'expanded': r'(?:Total expanded nodes|Expanded nodes)\s*:\s*(\d+)',
        }.items():
            match = re.search(pattern, output)
            if match:
                row[name] = float(match.group(1))
    except subprocess.TimeoutExpired:
        row.update(returncode=-1, won=False, output='90 second timeout')
    print(f"P{project} {agent} {layout} {ghost} seed={seed}: "
          f"{'WIN' if row['won'] else 'FAIL'} {row.get('score')}", flush=True)
    return row


def main():
    """Run the matrix with bounded process concurrency and save results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'docs/benchmark.json')
    args = parser.parse_args()
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(run, cases()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + '\n')
    if any(row['returncode'] != 0 or not row['won'] for row in results):
        raise SystemExit('At least one game failed; inspect the JSON report')


if __name__ == '__main__':
    main()
