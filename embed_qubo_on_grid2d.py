# embed_qubo_on_grid2d.py
import argparse
import matplotlib.pyplot as plt
import networkx as nx
from minorminer import find_embedding
from matplotlib.lines import Line2D

# reuse your modules
from qubo_graph_strict import generate_qubo_graph
from grid_of_cliques_2d import build_grid_of_cliques, layout_grid_polygon


def try_embed_with_expand(
    H: nx.Graph,
    n0: int,
    group_size: int,
    steps=(0, 1, 2, 3, 4, 6, 8),
    max_n=40,
):
    """Grow the hardware size from n0 until an embedding is found."""
    tried = []
    for inc in steps:
        n = min(max_n, n0 + inc)
        tried.append(n)
        G_hw = build_grid_of_cliques(n, group_size=group_size)
        emb = find_embedding(H.edges, G_hw.edges)
        if emb:
            return emb, G_hw, n
    return None, None, tried


# ---------- simple viz ----------
def draw_logical(G: nx.Graph, ax, title="Logical QUBO"):
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_size=520, node_color="skyblue", edgecolors="black", ax=ax)
    colors = ["green" if d.get("weight", 1) > 0 else "red" for _, _, d in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, edge_color=colors, width=2, ax=ax)
    nx.draw_networkx_labels(G, pos, ax=ax)
    elabs = {(u, v): f'{d.get("weight", 1):.0f}' for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=elabs, font_size=9, ax=ax)
    ax.set_title(title)
    ax.axis("off")


def draw_embedding_on_grid(G_hw: nx.Graph, pos_hw, embedding: dict, ax, title="Embedding on 2D grid"):
    # background nodes
    nx.draw_networkx_nodes(G_hw, pos_hw, nodelist=list(G_hw.nodes()),
                           node_size=110, node_color="#e6e6e6", edgecolors="none", ax=ax)
    # chains
    cmap = plt.cm.get_cmap("tab20", max(1, len(embedding)))
    legend_handles = []
    for idx, (lnode, chain) in enumerate(sorted(embedding.items(), key=lambda x: str(x[0]))):
        col = cmap(idx % 20)
        nx.draw_networkx_nodes(G_hw, pos_hw, nodelist=chain, node_size=180,
                               node_color=[col], edgecolors="black", linewidths=0.6, ax=ax)
        E_chain = [(u, v) for u, v in G_hw.subgraph(chain).edges()]
        nx.draw_networkx_edges(G_hw, pos_hw, edgelist=E_chain, width=2.2, edge_color=[col], ax=ax)

        # label: chain centroid with logical id
        xs = [pos_hw[n][0] for n in chain]
        ys = [pos_hw[n][1] for n in chain]
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        ax.text(cx, cy, str(lnode), fontsize=8, ha='center', va='center', fontweight='bold')

        legend_handles.append(Line2D([0], [0], marker='o', color='w', label=str(lnode),
                                     markerfacecolor=col, markersize=8))

    # put legend outside to the right
    ax.legend(handles=legend_handles, title="Logical node", fontsize=8,
              loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0.,
              frameon=True, facecolor='white', framealpha=0.9)
    ax.set_title(title)
    ax.axis("off")


def main():
    ap = argparse.ArgumentParser(
        description="Embed a QUBO onto a 2D grid-of-cliques (n×n, k-per-group) using minorminer, and visualize."
    )
    # QUBO
    ap.add_argument("--N", type=int, default=12, help="number of logical variables")
    ap.add_argument("--d", type=float, default=0.35, help="density in [0,1]")
    ap.add_argument("--mode", choices=["deterministic", "probabilistic"], default="probabilistic")
    ap.add_argument("--dist", choices=["uniform", "normal"], default="uniform")
    ap.add_argument("--sigma", type=float, default=0.12)
    ap.add_argument("--seed", type=int, default=0)
    # hardware
    ap.add_argument("--n", type=int, default=6, help="hardware grid size (n×n)")
    ap.add_argument("--group_size", type=int, default=3, help="nodes per group (clique size)")
    ap.add_argument("--x_gap", type=float, default=3.2)
    ap.add_argument("--y_gap", type=float, default=3.0)
    ap.add_argument("--radius", type=float, default=0.75)
    # misc
    ap.add_argument("--auto_expand", action="store_true", help="auto-increase n until an embedding is found")
    ap.add_argument("--save", type=str, default="", help="optional PNG path to save")
    ap.add_argument("--fig_w", type=float, default=18.0, help="figure width (inches)")
    ap.add_argument("--fig_h", type=float, default=8.0, help="figure height (inches)")
    args = ap.parse_args()

    # 1) logical QUBO (±1 weights)
    H = generate_qubo_graph(args.N, args.d, mode=args.mode, dist=args.dist, sigma=args.sigma, seed=args.seed)

    # 2) hardware + embedding
    if args.auto_expand:
        embedding, G_hw, n_used = try_embed_with_expand(H, args.n, args.group_size)
        if not embedding:
            raise RuntimeError(f"No embedding found; tried sizes n={n_used}")
        n = n_used
    else:
        n = args.n
        G_hw = build_grid_of_cliques(n, group_size=args.group_size)
        embedding = find_embedding(H.edges, G_hw.edges)
        if not embedding:
            raise RuntimeError("No embedding found; try larger --n or enable --auto_expand")

    # 3) layout & viz
    pos_hw, _ = layout_grid_polygon(
        n, group_size=args.group_size, x_gap=args.x_gap, y_gap=args.y_gap, radius=args.radius
    )

    fig, axes = plt.subplots(1, 2, figsize=(args.fig_w, args.fig_h))
    # leave space for legend on the right of the embedding axis
    plt.subplots_adjust(right=0.82)
    # left: logical graph
    draw_logical(H, axes[0], title=f"Logical QUBO (N={args.N}, d={args.d})")
    # right: embedding
    draw_embedding_on_grid(G_hw, pos_hw, embedding, axes[1], title=f"Embedding on 2D grid (n={n}, k={args.group_size})")
    plt.tight_layout()
    if args.save:
        plt.savefig(args.save, dpi=220, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()