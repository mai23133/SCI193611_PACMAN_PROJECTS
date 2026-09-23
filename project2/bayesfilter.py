# Complete this class for all parts of the project

from pacman_module.game import Agent
import numpy as np
from pacman_module import util
from scipy.stats import binom


class BeliefStateAgent(Agent):
    def __init__(self, args):
        """
        Arguments:
        ----------
        - `args`: Namespace of arguments from command-line prompt.
        """
        self.args = args

        """
            Variables to use in 'update_belief_state' method.
            Initialization occurs in 'get_action' method.

            XXX: DO NOT MODIFY THE DEFINITION OF THESE VARIABLES
            # Doing so will result in a 0 grade.
        """

        # Current list of belief states over ghost positions
        self.beliefGhostStates = None

        # Grid of walls (assigned with 'state.getWalls()' method)
        self.walls = None

        # Hyper-parameters
        self.ghost_type = self.args.ghostagent
        self.sensor_variance = self.args.sensorvariance

        self.p = 0.5
        self.n = int(self.sensor_variance/(self.p*(1-self.p)))

        if not np.isfinite(self.sensor_variance) or self.sensor_variance < 0:
            raise ValueError("Sensor variance must be finite and nonnegative")
        if self.ghost_type not in {"confused", "afraid", "scared"}:
            raise ValueError("Unknown ghost policy")
        self.metrics = []
        self._transition_position = None
        self._transition = None

    def _get_sensor_model(self, pacman_position, evidence):
        """
        Arguments:
        ----------
        - `pacman_position`: 2D coordinates position
          of pacman at state x_{t}
          where 't' is the current time step

        Return:
        -------
        The sensor model represented as a 2D numpy array of
        size [width, height].
        The element at position (w, h) is the probability
        P(E_t=evidence | X_t=(w, h))
        """
        distances = np.abs(np.arange(self.walls.width)[:, None]
                           - pacman_position[0])
        distances = distances + np.abs(np.arange(self.walls.height)[None, :]
                                       - pacman_position[1])
        successes = evidence - distances + self.n*self.p
        likelihood = binom.pmf(successes, self.n, self.p)
        return likelihood * np.logical_not(self.walls.data)

    def _get_transition_model(self, pacman_position):
        """
        Arguments:
        ----------
        - `pacman_position`: 2D coordinates position
          of pacman at state x_{t}
          where 't' is the current time step

        Return:
        -------
        The transition model represented as a 4D numpy array of
        size [width, height, width, height].
        The element at position (w1, h1, w2, h2) is the probability
        P(X_t+1=(w1, h1) | X_t=(w2, h2))
        """
        if self._transition_position == tuple(pacman_position):
            return self._transition
        width, height = self.walls.width, self.walls.height
        transition = np.zeros((width, height, width, height))
        bias = {"confused": 1, "afraid": 2, "scared": 8}[self.ghost_type]
        px, py = pacman_position
        for x in range(width):
            for y in range(height):
                if self.walls[x][y]:
                    continue
                neighbors = [(nx, ny) for nx, ny in
                             ((x+1, y), (x-1, y), (x, y+1), (x, y-1))
                             if 0 <= nx < width and 0 <= ny < height
                             and not self.walls[nx][ny]]
                if not neighbors:
                    neighbors = [(x, y)]
                distance = abs(x-px) + abs(y-py)
                weights = [bias if abs(nx-px) + abs(ny-py) >= distance
                           else 1 for nx, ny in neighbors]
                total = sum(weights)
                for (nx, ny), weight in zip(neighbors, weights):
                    transition[nx, ny, x, y] = weight / total
        self._transition_position = tuple(pacman_position)
        self._transition = transition
        return transition

    def _get_updated_belief(
            self, belief, evidences, pacman_position, ghosts_eaten):
        """
        Given a list of (noised) distances from pacman to ghosts,
        and the previous belief states before receiving the evidences,
        returns the updated list of belief states about ghosts positions

        Arguments:
        ----------
        - `belief`: A list of Z belief states at state x_{t-1}
          as N*M numpy mass probability matrices
          where N and M are respectively width and height
          of the maze layout and Z is the number of ghosts.
        - `evidences`: list of distances between
          pacman and ghosts at state x_{t}
          where 't' is the current time step
        - `pacman_position`: 2D coordinates position
          of pacman at state x_{t}
          where 't' is the current time step
        - `ghosts_eaten`: list of booleans indicating
          whether ghosts have been eaten or not

        Return:
        -------
        - A list of Z belief states at state x_{t}
          as N*M numpy mass probability matrices
          where N and M are respectively width and height
          of the maze layout and Z is the number of ghosts.

        N.B. : [0,0] is the bottom left corner of the maze.
               Matrices filled with zeros must be returned for eaten ghosts.
        """

        transition = self._get_transition_model(pacman_position)
        width, height = self.walls.width, self.walls.height
        matrix = transition.reshape(width*height, width*height)
        targets, sources = np.nonzero(matrix)
        weights = matrix[targets, sources]
        updated = []
        sensors = {}
        free = np.logical_not(self.walls.data).astype(float)
        for index, prior in enumerate(belief):
            if ghosts_eaten[index]:
                updated.append(np.zeros((width, height)))
                continue
            prediction = np.bincount(
                targets, weights=weights*np.asarray(prior).ravel()[sources],
                minlength=width*height).reshape(width, height)
            evidence = evidences[index]
            if evidence not in sensors:
                sensors[evidence] = self._get_sensor_model(
                    pacman_position, evidence)
            sensor = sensors[evidence]
            posterior = prediction * sensor
            total = posterior.sum()
            if total <= 0:
                # Recover from an inconsistent/zero prior without NaNs.
                posterior = sensor * free
                total = posterior.sum()
            if total <= 0:
                # An impossible observation carries no usable information.
                posterior = prediction if prediction.sum() > 0 else free
                total = posterior.sum()
            updated.append(posterior / total)
        return updated

    def update_belief_state(self, evidences, pacman_position, ghosts_eaten):
        """
        Given a list of (noised) distances from pacman to ghosts,
        returns a list of belief states about ghosts positions

        Arguments:
        ----------
        - `evidences`: list of distances between
          pacman and ghosts at state x_{t}
          where 't' is the current time step
        - `pacman_position`: 2D coordinates position
          of pacman at state x_{t}
          where 't' is the current time step
        - `ghosts_eaten`: list of booleans indicating
          whether ghosts have been eaten or not

        Return:
        -------
        - A list of Z belief states at state x_{t}
          as N*M numpy mass probability matrices
          where N and M are respectively width and height
          of the maze layout and Z is the number of ghosts.

        XXX: DO NOT MODIFY THIS FUNCTION !!!
        Doing so will result in a 0 grade.
        """
        belief = self._get_updated_belief(self.beliefGhostStates, evidences,
                                          pacman_position, ghosts_eaten)
        self.beliefGhostStates = belief
        return belief

    def _get_evidence(self, state):
        """
        Computes noisy distances between pacman and ghosts.

        Arguments:
        ----------
        - `state`: The current game state s_t
                   where 't' is the current time step.
                   See FAQ and class `pacman.GameState`.


        Return:
        -------
        - A list of Z noised distances in real numbers
          where Z is the number of ghosts.

        XXX: DO NOT MODIFY THIS FUNCTION !!!
        Doing so will result in a 0 grade.
        """
        positions = state.getGhostPositions()
        pacman_position = state.getPacmanPosition()
        noisy_distances = []

        for pos in positions:
            true_distance = util.manhattanDistance(pos, pacman_position)
            noise = binom.rvs(self.n, self.p) - self.n*self.p
            noisy_distances.append(true_distance + noise)

        return noisy_distances

    def _record_metrics(self, belief_states, state):
        """
        Use this function to record your metrics
        related to true and belief states.
        Won't be part of specification grading.

        Arguments:
        ----------
        - `state`: The current game state s_t
                   where 't' is the current time step.
                   See FAQ and class `pacman.GameState`.
        - `belief_states`: A list of Z
           N*M numpy matrices of probabilities
           where N and M are respectively width and height
           of the maze layout and Z is the number of ghosts.

        N.B. : [0,0] is the bottom left corner of the maze
        """
        positions = state.getGhostPositions()
        rows = []
        for index, belief in enumerate(belief_states):
            if np.sum(belief) == 0:
                continue
            x, y = positions[index]
            positive = belief[belief > 0]
            true_mass = float(belief[x, y])
            distances = (np.abs(np.arange(belief.shape[0])[:, None] - x)
                         + np.abs(np.arange(belief.shape[1])[None, :] - y))
            rows.append({
                "ghost": index,
                "entropy": float(-np.sum(positive*np.log2(positive))),
                "brier": float(np.sum(belief**2) - 2*true_mass + 1),
                "true_mass": true_mass,
                "expected_distance": float(np.sum(belief*distances)),
            })
        self.metrics.append(rows)

    def get_action(self, state):
        """
        Given a pacman game state, returns a belief state.

        Arguments:
        ----------
        - `state`: the current game state.
                   See FAQ and class `pacman.GameState`.

        Return:
        -------
        - A belief state.
        """

        """
           XXX: DO NOT MODIFY THAT FUNCTION !!!
                Doing so will result in a 0 grade.
        """
        # Variables are specified in constructor.
        if self.beliefGhostStates is None:
            self.beliefGhostStates = state.getGhostBeliefStates()
        if self.walls is None:
            self.walls = state.getWalls()

        evidence = self._get_evidence(state)
        newBeliefStates = self.update_belief_state(evidence,
                                                   state.getPacmanPosition(),
                                                   state.data._eaten[1:])
        self._record_metrics(self.beliefGhostStates, state)

        return newBeliefStates, evidence
