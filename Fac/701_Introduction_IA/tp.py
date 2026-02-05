import random
from collections import defaultdict
import math

# ======================================================
#  ENVIRONNEMENT : Labyrinthe 5x5
# ======================================================

FREE, WALL = 0, 1
ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]

MOVES = {
    "UP":    (-1, 0),
    "DOWN":  ( 1, 0),
    "LEFT":  ( 0,-1),
    "RIGHT": ( 0, 1),
}

def in_bounds(pos):
    r, c = pos
    return 0 <= r < 5 and 0 <= c < 5

def add(p, q):
    return (p[0]+q[0], p[1]+q[1])

def manhattan(p, q):
    return abs(p[0]-q[0]) + abs(p[1]-q[1])

def make_maze_5x5():
    """
    Labyrinthe 5x5 :
    E . # . .
    . # . # .
    . # . # .
    . . . # .
    # # . . S
    """
    return [
        [0,0,1,0,0],
        [0,1,0,1,0],
        [0,1,0,1,0],
        [0,0,0,1,0],
        [1,1,0,0,0],
    ]

class GridWorld:
    """
    Grille 5x5 avec obstacles et shaping potentiel.
    Observation : fenêtre 3x3 binaire centrée sur le robot.
    Reward shaping :
      - collision : -10
      - déplacement libre : -1
      - arrivée but : +100
      - shaping : +η(Φ(s') - Φ(s)), avec Φ(s) = -Manhattan(s,goal)
    """
    def __init__(self, grid, start, goal, eta_potential=0.5):
        self.grid = grid
        self.start = start
        self.goal = goal
        self.eta_potential = eta_potential
        self.reset()

    def reset(self):
        self.pos = self.start
        return self.observe()

    def observe(self):
        bits = []
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                p = (self.pos[0]+dr, self.pos[1]+dc)
                if not in_bounds(p):
                    bits.append('1')
                else:
                    bits.append('1' if self.grid[p[0]][p[1]] == WALL else '0')
        return ''.join(bits)

    def step(self, action):
        prev_pos = self.pos
        d = MOVES[action]
        nxt = add(self.pos, d)

        # collision ou bord
        if (not in_bounds(nxt)) or (self.grid[nxt[0]][nxt[1]] == WALL):
            reward = -10
            nxt = self.pos
        else:
            reward = -1

        done = False
        if nxt == self.goal:
            reward = 100
            done = True

        self.pos = nxt
        obs2 = self.observe()

        # --- Potential-based shaping ---
        if self.eta_potential and not done:
            phi_prev = -manhattan(prev_pos, self.goal)
            phi_next = -manhattan(self.pos, self.goal)
            reward += self.eta_potential * (phi_next - phi_prev)
        # --------------------------------

        return reward, obs2, done

# ======================================================
#  XCS MINIMAL : Formules du cours
# ======================================================

def matches(condition, obs):
    return all(c == '#' or c == b for c, b in zip(condition, obs))

class Classifier:
    __slots__ = ("condition","action","p","eps","F","exp")
    def __init__(self, condition, action, p_init=10.0, F_init=0.01):
        self.condition = condition
        self.action = action
        self.p = p_init      # prédiction moyenne
        self.eps = 0.0       # erreur de prédiction
        self.F = F_init      # fitness
        self.exp = 0         # expérience

class XCS:
    """
    Implémente :
      - Match set [M]
      - Tableau de prédiction PS_i (moyenne pondérée par F)
      - Sélection ε-greedy
      - Mises à jour (p, eps, F) dans [A] avec cible TD
      - Covering simple (sans GA)
    """
    def __init__(self, actions, beta=0.2, epsilon=0.2, gamma=0.95,
                 eps0=10.0, alpha=0.1, nu=5.0, p_hash_cover=0.4):
        self.P = []
        self.actions = actions
        self.beta = beta
        self.epsilon = epsilon
        self.gamma = gamma
        self.eps0 = eps0
        self.alpha = alpha
        self.nu = nu
        self.p_hash_cover = p_hash_cover

    def match_set(self, obs):
        M = [cl for cl in self.P if matches(cl.condition, obs)]
        actions_presentes = {cl.action for cl in M}
        for a in self.actions:
            if a not in actions_presentes:
                M.append(self._cover_rule(obs, a))
        return M

    def _cover_rule(self, obs, action):
        cond = ''.join('#' if random.random() < self.p_hash_cover else b for b in obs)
        cl = Classifier(cond, action)
        self.P.append(cl)
        return cl

    def prediction_array(self, M):
        num = defaultdict(float)
        den = defaultdict(float)
        for cl in M:
            num[cl.action] += cl.p * cl.F
            den[cl.action] += cl.F
        PS = {}
        for a in self.actions:
            PS[a] = (num[a] / den[a]) if den[a] > 0 else 0.0
        return PS

    def select_action(self, PS):
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        return max(self.actions, key=lambda a: PS[a])

    def update_action_set(self, A, target):
        # (1) mise à jour p et eps
        for cl in A:
            cl.exp += 1
            cl.p += self.beta * (target - cl.p)
            cl.eps += self.beta * (abs(target - cl.p) - cl.eps)

        # (2) précision κ
        kappas = []
        for cl in A:
            if cl.eps < self.eps0:
                k = 1.0
            else:
                k = self.alpha * ((cl.eps / self.eps0) ** (-self.nu))
            kappas.append(k)

        sum_k = sum(kappas) if kappas else 1.0

        # (3) fitness relative κ' et mise à jour F
        for cl, k in zip(A, kappas):
            k_rel = (k / sum_k) if sum_k > 0 else 0.0
            cl.F += self.beta * (k_rel - cl.F)

# ======================================================
#  BOUCLE D'APPRENTISSAGE
# ======================================================

def run_episode(env, xcs, max_steps=200):
    obs = env.reset()
    total_reward = 0
    steps = 0
    done = False

    while not done and steps < max_steps:
        # [M]
        M = xcs.match_set(obs)
        # PS_i
        PS = xcs.prediction_array(M)
        # ε-greedy
        action = xcs.select_action(PS)
        # [A] = règles qui prônent cette action
        A = [cl for cl in M if cl.action == action]
        # Exécuter
        r, obs2, done = env.step(action)
        total_reward += r

        # Cible TD : P* = r + γ * max PS'(a')
        if not done:
            M2 = xcs.match_set(obs2)
            PS2 = xcs.prediction_array(M2)
            target = r + xcs.gamma * max(PS2[a] for a in ACTIONS)
        else:
            target = r

        # Mise à jour (p, eps, F)
        xcs.update_action_set(A, target)

        obs = obs2
        steps += 1

    return total_reward, steps, done

# ======================================================
#  MAIN : Entraînement du robot dans le labyrinthe
# ======================================================

def main():
    random.seed(0)

    grid = make_maze_5x5()
    start = (0,0)
    goal  = (4,4)

    env = GridWorld(grid, start, goal, eta_potential=0.5)
    xcs = XCS(ACTIONS,
              beta=0.2, epsilon=0.2, gamma=0.95,
              eps0=10.0, alpha=0.1, nu=5.0, p_hash_cover=0.4)

    episodes = 400
    wins = 0

    for ep in range(1, episodes+1):
        R, steps, done = run_episode(env, xcs, max_steps=200)
        if done and env.pos == goal:
            wins += 1
        if ep % 50 == 0:
            print(f"Épisode {ep:3d} | Récompense={R:7.2f} | étapes={steps:3d} | succès={wins}")

    print(f"\nTaux de succès (sortie atteinte) : {wins/episodes:.2%}")

if __name__ == "__main__":
    main()
