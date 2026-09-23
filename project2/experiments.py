"""Reproducible, fixed-duration tracking experiments without ghost capture.

Ground-truth motion uses the supplied ghost policies on a geometric observation
adapter. Pacman stays at its initial position; capture is disabled to give
equal trial durations. The filter and metrics use the submitted implementation.
"""

import argparse
import json
import os
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from scipy.stats import t as student_t

from bayesfilter import BeliefStateAgent
from pacman_module.game import Actions, Directions
from pacman_module.ghostAgents import AfraidGhost, ConfusedGhost, ScaredGhost
from pacman_module.layout import Layout

POLICIES = {'confused': ConfusedGhost, 'afraid': AfraidGhost,
            'scared': ScaredGhost}
METRICS = ('entropy', 'brier', 'expected_distance')


class TrackingObservation:
    """Expose geometric moves to original policies, without collisions."""

    def __init__(self, walls, pacman, positions):
        """Store walls, a fixed Pacman position and ghost coordinates."""
        self.walls, self.pacman, self.positions = walls, pacman, positions

    def getPacmanPosition(self):
        """Return the controller position used by the ghost's policy."""
        return self.pacman

    def getGhostPosition(self, index):
        """Return one ghost position using the engine's one-based indexing."""
        return self.positions[index-1]

    def getGhostPositions(self):
        """Return ground truth exclusively for metric recording."""
        return self.positions

    def getLegalActions(self, index):
        """Return all geometric cardinal moves, including reverse moves."""
        x, y = self.getGhostPosition(index)
        legal = [Directions.STOP]
        for action in (Directions.NORTH, Directions.SOUTH,
                       Directions.EAST, Directions.WEST):
            dx, dy = Actions.directionToVector(action)
            if not self.walls[int(x+dx)][int(y+dy)]:
                legal.append(action)
        return legal

    def generateSuccessor(self, index, action):
        """Return a geometric successor without applying capture or scoring."""
        positions = list(self.positions)
        x, y = positions[index-1]
        dx, dy = Actions.directionToVector(action)
        positions[index-1] = (int(x+dx), int(y+dy))
        return TrackingObservation(self.walls, self.pacman, positions)


def interval(samples):
    """Return mean and 95% Student-t half-width over independent trials."""
    samples = np.asarray(samples)
    half = student_t.ppf(0.975, len(samples)-1) * samples.std(
        axis=0, ddof=1) / np.sqrt(len(samples))
    return samples.mean(axis=0), half


def run_case(layout_name, policy, variance, trials, steps, ghosts, seed):
    """Return trial curves, tail statistics and convergence diagnostics."""
    path = (Path(__file__).parent / 'pacman_module/layouts'
            / f'{layout_name}.lay')
    layout = Layout(path.read_text().splitlines())
    pacman = next(pos for kind, pos in layout.agentPositions if kind == 0)
    args = SimpleNamespace(ghostagent=policy, sensorvariance=variance)
    agent = BeliefStateAgent(args)
    agent.walls = layout.walls
    free = [(x, y) for x in range(layout.width) for y in range(layout.height)
            if not layout.walls[x][y]]
    indices = {point: i for i, point in enumerate(free)}
    destinations = np.zeros((len(free), 4), dtype=int)
    cumulative = np.ones((len(free), 4))
    ghost_agent = POLICIES[policy](1, args)
    # These transition probabilities come from the original ghost code.
    for i, point in enumerate(free):
        observation = TrackingObservation(layout.walls, pacman, [point])
        distribution = ghost_agent.getDistribution(observation)
        total = 0
        for j, (action, probability) in enumerate(distribution.items()):
            target = observation.generateSuccessor(1, action).positions[0]
            destinations[i, j] = indices[target]
            total += probability
            cumulative[i, j] = total
    motion = np.random.default_rng(seed)
    sensor = np.random.default_rng(seed + 100000)
    initial = [indices[point] for point in free if point != pacman]
    positions = motion.choice(initial, size=trials*ghosts)
    prior = np.logical_not(layout.walls.data).astype(float)
    prior /= prior.sum()
    beliefs = [prior.copy() for _ in positions]
    curves = np.empty((trials, steps, len(METRICS)))
    points = np.array(free)
    for step in range(steps):
        choice = (motion.random(len(positions))[:, None]
                  > cumulative[positions]).sum(axis=1)
        positions = destinations[positions, choice]
        coordinates = points[positions]
        distances = np.abs(coordinates - np.array(pacman)).sum(axis=1)
        evidence = distances + sensor.binomial(agent.n, agent.p,
                                               len(positions)) - agent.n/2
        beliefs = agent._get_updated_belief(
            beliefs, evidence, pacman, [False]*len(positions))
        observation = TrackingObservation(layout.walls, pacman, coordinates)
        agent._record_metrics(beliefs, observation)
        records = agent.metrics.pop()
        values = np.array([[row[name] for name in METRICS] for row in records])
        curves[:, step, :] = values.reshape(trials, ghosts, -1).mean(axis=1)
    window = steps // 3
    tail = curves[:, -window:, :].mean(axis=1)
    previous = curves[:, -2*window:-window, :].mean(axis=1)
    means, errors = interval(tail)
    delta, delta_error = interval(tail-previous)
    summary = {name: {'mean': float(means[i]), 'ci95': float(errors[i]),
                      'tail_change': float(delta[i]),
                      'tail_change_ci95': float(delta_error[i])}
               for i, name in enumerate(METRICS)}
    return curves, summary


def plot_results(curves, summaries, variances, output):
    """Save convergence/variance figures with trial confidence bars."""
    os.environ.setdefault('MPLCONFIGDIR',
                          str(Path(__file__).parent / '.mplconfig'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    layouts = ('large_filter', 'large_filter_walls')
    colors = {'confused': '#2563eb', 'afraid': '#d97706', 'scared': '#16a34a'}
    figure, axes = plt.subplots(2, 2, figsize=(10, 5.8),
                                constrained_layout=True)
    for row, layout in enumerate(layouts):
        for policy in POLICIES:
            values = curves[f'{layout}__{policy}__1']
            mean, error = interval(values)
            x = np.arange(1, values.shape[1]+1)
            for column, metric in enumerate(METRICS[:2]):
                ax = axes[row, column]
                ax.plot(x, mean[:, column], label=policy, color=colors[policy],
                        linewidth=1)
                every = max(1, len(x)//12)
                ax.errorbar(x[::every], mean[::every, column],
                            yerr=error[::every, column], fmt='none',
                            color=colors[policy], alpha=0.7, capsize=2)
                ax.set(title=f'{layout}: {metric}', xlabel='Step',
                       ylabel='bits' if column == 0 else 'Brier score')
                ax.grid(alpha=0.2)
        axes[row, 0].legend(fontsize=8)
    figure.savefig(output / 'convergence.pdf')
    figure.savefig(output / 'convergence.png', dpi=160)
    plt.close(figure)
    figure, axes = plt.subplots(1, 2, figsize=(10, 3), constrained_layout=True)
    for ax, layout in zip(axes, layouts):
        for policy in POLICIES:
            rows = [summaries[f'{layout}__{policy}__{v:g}']['entropy']
                    for v in variances]
            ax.errorbar(variances, [r['mean'] for r in rows],
                        yerr=[r['ci95'] for r in rows], marker='o', capsize=3,
                        label=policy, color=colors[policy])
        ax.set(title=layout, xlabel='Requested sensor variance',
               ylabel='Mean tail entropy (bits)')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.2)
    figure.savefig(output / 'variance.pdf')
    figure.savefig(output / 'variance.png', dpi=160)
    plt.close(figure)


def main():
    """Save raw curves, statistical summaries and plots for all scenarios."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trials', type=int, default=30)
    parser.add_argument('--steps', type=int, default=1800)
    parser.add_argument('--high-noise-steps', type=int, default=9000)
    parser.add_argument('--resume', action='store_true',
                        help='Reuse matching completed trial arrays')
    parser.add_argument('--ghosts', type=int, default=3)
    parser.add_argument('--seed', type=int, default=193611)
    parser.add_argument('--output', type=Path,
                        default=Path(__file__).parent / 'results')
    args = parser.parse_args()
    if (args.trials < 2 or args.steps < 6 or args.ghosts < 1
            or args.high_noise_steps < args.steps):
        parser.error('Require trials >= 2, steps >= 6, ghosts >= 1, '
                     'and high-noise-steps >= steps')
    args.output.mkdir(parents=True, exist_ok=True)
    variances = (0.25, 1.0, 4.0)
    curves, summaries = {}, {}
    cached = None
    previous = {}
    if args.resume and (args.output / 'summary.json').exists():
        previous = json.loads((args.output / 'summary.json').read_text())
        settings = previous['configuration']
        if all(settings[name] == getattr(args, name)
               for name in ('trials', 'ghosts', 'seed')):
            cached = np.load(args.output / 'trials.npz')
    for layout in ('large_filter', 'large_filter_walls'):
        for policy in POLICIES:
            for variance in variances:
                name = f'{layout}__{policy}__{variance:g}'
                steps = args.high_noise_steps if variance == 4 else args.steps
                if (cached is not None and name in cached
                        and cached[name].shape == (args.trials, steps, 3)):
                    curves[name] = cached[name]
                    summaries[name] = previous['scenarios'][name]
                    print(f'Reusing {name}', flush=True)
                    continue
                print(f'Running {name}', flush=True)
                curves[name], summaries[name] = run_case(
                    layout, policy, variance, args.trials, steps,
                    args.ghosts, args.seed)
    if cached is not None:
        cached.close()
    np.savez_compressed(args.output / 'trials.npz', **curves)
    metadata = {key: value for key, value in vars(args).items()
                if key not in ('output', 'resume')}
    metadata.update({'capture': False, 'pacman': 'stationary',
                     'metrics': METRICS, 'variances': variances,
                     'tail_window': args.steps//3,
                     'high_noise_tail_window': args.high_noise_steps//3})
    (args.output / 'summary.json').write_text(
        json.dumps({'configuration': metadata, 'scenarios': summaries},
                   indent=2) + '\n')
    plot_results(curves, summaries, variances, args.output)
    print(f'Results saved to {args.output}', flush=True)


if __name__ == '__main__':
    main()
