
from typing import Literal, Optional, List
import numpy as np
import networkx as nx
from networkx.algorithms.graphical import is_graphical
from networkx.generators.degree_seq import havel_hakimi_graph

def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))

def _clamp_int_degs(degs: List[float], N: int) -> List[int]:
    return [int(max(0, min(N - 1, k))) for k in degs]

def _make_even_sum(degs: List[int], N: int) -> List[int]:
    d = degs[:]
    if sum(d) % 2 == 1:
        idx = int(np.argmax(d))
        if d[idx] > 0:
            d[idx] -= 1
        else:
            j = int(np.argmin(d))
            if d[j] < N - 1:
                d[j] += 1
    return d

def generate_qubo_graph(
    N: int,
    d: float,
    mode: Literal["deterministic", "probabilistic"] = "deterministic",
    dist: Literal["uniform", "normal"] = "uniform",
    sigma: float = 0.1,
    seed: Optional[int] = None,
    max_tries: int = 2000,
) -> nx.Graph:

    rng = np.random.default_rng(seed)

    if mode == "deterministic":
        k = int(round(_clip01(d) * (N - 1)))
        k = max(0, min(k, N - 1))
        if (N * k) % 2 == 1 or k >= N:
            raise ValueError(
                f"k-regular graph impossible for N={N}, k={k}. "
                f"Ensure 0<=k<=N-1 and N*k is even."
            )
        G = nx.random_regular_graph(k, N, seed=seed)
        return nx.Graph(G)

    elif mode == "probabilistic":
        for _ in range(max_tries):
            if dist == "uniform":
                a = sigma
                p_low, p_high = _clip01(d - a), _clip01(d + a)
                p_i = rng.uniform(p_low, p_high, size=N)
            elif dist == "normal":
                p_i = np.clip(rng.normal(loc=d, scale=sigma, size=N), 0.0, 1.0)
            else:
                raise ValueError("dist must be 'uniform' or 'normal'")

            k_i = _clamp_int_degs(np.rint(p_i * (N - 1)), N)
            k_i = _make_even_sum(k_i, N)

            if is_graphical(k_i, method="eg"):
                G = havel_hakimi_graph(k_i, create_using=nx.Graph)
                return nx.Graph(G)

        
        '''k_fix = _clamp_int_degs(k_i, N)
        k_fix = _make_even_sum(k_fix, N)
        attempts = 0
        while not is_graphical(k_fix, method="eg") and sum(k_fix) > 0 and attempts < N * (N - 1):
            idx = list(np.argsort(k_fix))[::-1]
            i = idx[0]
            j = idx[1] if len(idx) > 1 else idx[0]
            if k_fix[i] > 0: k_fix[i] -= 1
            if k_fix[j] > 0: k_fix[j] -= 1
            attempts += 1

        if is_graphical(k_fix, method="eg"):
            G = havel_hakimi_graph(k_fix, create_using=nx.Graph)
            return nx.Graph(G)

        raise RuntimeError("Failed to generate a graphical degree sequence after retries and repair.")'''

    else:
        raise ValueError("mode must be 'deterministic' or 'probabilistic'")