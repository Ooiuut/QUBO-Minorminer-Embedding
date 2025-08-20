# grid_of_cliques_2d.py
import math
import argparse
import networkx as nx
import matplotlib.pyplot as plt


def regular_polygon_offsets(k: int, radius: float, rotation: float = 0.0):
    """Return k points on a circle (radius), optionally rotated (radians)."""
    offs = []
    for i in range(k):
        ang = rotation + 2.0 * math.pi * i / k
        offs.append((radius * math.cos(ang), radius * math.sin(ang)))
    return offs


def build_grid_of_cliques(n: int, group_size: int = 3) -> nx.Graph:
    """
    Build an n×n grid of groups (tiles). Each group has `group_size` nodes forming a clique.
    Each group is fully bipartite-connected (k×k) to its 4-neighbors (up/down/left/right).
    Node format: ('g', gx, gy, i) with gx,gy in [0..n-1], i in [0..group_size-1].
    """
    G = nx.Graph()
    # add nodes
    for gx in range(n):
        for gy in range(n):
            for i in range(group_size):
                G.add_node(('g', gx, gy, i), gx=gx, gy=gy, idx=i)

    # intra-group clique
    for gx in range(n):
        for gy in range(n):
            nodes = [('g', gx, gy, i) for i in range(group_size)]
            for a in range(group_size):
                for b in range(a + 1, group_size):
                    G.add_edge(nodes[a], nodes[b], kind='intra')

    # inter-group (4-neighbor) full bipartite
    def neighbors(gx, gy):
        if gx + 1 < n:  # right
            yield (gx + 1, gy)
        if gy + 1 < n:  # down
            yield (gx, gy + 1)
        if gx - 1 >= 0:  # left
            yield (gx - 1, gy)
        if gy - 1 >= 0:  # up
            yield (gx, gy - 1)

    for gx in range(n):
        for gy in range(n):
            A = [('g', gx, gy, i) for i in range(group_size)]
            for ngx, ngy in neighbors(gx, gy):
                # avoid duplicates (undirected)
                if (ngx, ngy) <= (gx, gy):
                    continue
                B = [('g', ngx, ngy, j) for j in range(group_size)]
                for i in range(group_size):
                    for j in range(group_size):
                        G.add_edge(A[i], B[j], kind='inter')

    return G


def layout_grid_polygon(
    n: int,
    group_size: int,
    x_gap: float = 3.2,
    y_gap: float = 3.0,
    radius: float = 0.75,
    rotation_deg: float = -90.0,
):
    """
    Place each group at grid (gx*x_gap, -gy*y_gap).
    Inside a group, arrange k nodes on a regular k-gon of `radius`.
    Returns (pos, centers).
    """
    pos, centers = {}, {}
    rotation = math.radians(rotation_deg)
    offs = regular_polygon_offsets(group_size, radius, rotation)
    for gx in range(n):
        for gy in range(n):
            cx, cy = gx * x_gap, -gy * y_gap
            centers[(gx, gy)] = (cx, cy)
            for i, (dx, dy) in enumerate(offs):
                pos[('g', gx, gy, i)] = (cx + dx, cy + dy)
    return pos, centers


# --- CLI demo (optional) ---
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Draw an n×n grid of cliques with arbitrary group_size.")
    ap.add_argument("--n", type=int, default=5, help="grid size (n×n)")
    ap.add_argument("--group_size", type=int, default=3, help="nodes per group (clique size)")
    ap.add_argument("--x_gap", type=float, default=3.2)
    ap.add_argument("--y_gap", type=float, default=3.0)
    ap.add_argument("--radius", type=float, default=0.85)
    ap.add_argument("--save", type=str, default="")
    args = ap.parse_args()

    G = build_grid_of_cliques(args.n, group_size=args.group_size)
    pos, centers = layout_grid_polygon(args.n, args.group_size, args.x_gap, args.y_gap, args.radius)

    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, node_size=180, node_color="#e6f2ff", edge_color="#c0c0c0", with_labels=False)
    plt.title(f"Grid of cliques: n={args.n}, group_size={args.group_size}")
    plt.axis("off")
    if args.save:
        plt.savefig(args.save, dpi=220, bbox_inches="tight")
    plt.show()