# demo_qubo_viz.py
import argparse
import networkx as nx
import matplotlib.pyplot as plt
from qubo_graph_strict import generate_qubo_graph

def draw_graph_and_degree_hist(G, title, ax_graph, ax_hist, seed=42):
    
    pos = nx.spring_layout(G, seed=seed)
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color="skyblue",
                           edgecolors="black", ax=ax_graph)
    nx.draw_networkx_edges(G, pos, width=1.8, edge_color="#666", ax=ax_graph)
    nx.draw_networkx_labels(G, pos, font_size=10, ax=ax_graph)
    ax_graph.set_title(title)
    ax_graph.axis("off")

    
    degrees = [deg for _, deg in G.degree()]
    ax_hist.hist(degrees, bins=range(0, max(degrees)+2), align="left")
    ax_hist.set_xlabel("degree")
    ax_hist.set_ylabel("count")
    ax_hist.set_title(f"degree histogram (avg={sum(degrees)/len(degrees):.2f})")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--N", type=int, default=20, help="number of variables (nodes)")
    p.add_argument("--d", type=float, default=0.4, help="density in [0,1]")
    p.add_argument("--mode", choices=["deterministic","probabilistic","compare"], default="deterministic")
    p.add_argument("--dist", choices=["uniform","normal"], default="uniform",
                   help="used only in probabilistic/compare")
    p.add_argument("--sigma", type=float, default=0.1, help="std for probabilistic mode")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--save", type=str, default="", help="path to save PNG (optional)")
    args = p.parse_args()

    if args.mode != "compare":
        G = generate_qubo_graph(
            N=args.N, d=args.d, mode=args.mode, dist=args.dist,
            sigma=args.sigma, seed=args.seed
        )
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        draw_graph_and_degree_hist(
            G, f"{args.mode} (N={args.N}, d={args.d}, dist={args.dist}, sigma={args.sigma})",
            axes[0], axes[1], seed=args.seed
        )
    else:
        
        Gd = generate_qubo_graph(N=args.N, d=args.d, mode="deterministic", seed=args.seed)
        Gp = generate_qubo_graph(
            N=args.N, d=args.d, mode="probabilistic", dist=args.dist,
            sigma=args.sigma, seed=args.seed
        )
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        draw_graph_and_degree_hist(
            Gd, f"deterministic (N={args.N}, d={args.d})",
            axes[0][0], axes[0][1], seed=args.seed
        )
        draw_graph_and_degree_hist(
            Gp, f"probabilistic (N={args.N}, d={args.d}, dist={args.dist}, sigma={args.sigma})",
            axes[1][0], axes[1][1], seed=args.seed
        )
        plt.tight_layout()

    if args.save:
        plt.savefig(args.save, dpi=200, bbox_inches="tight")
    plt.show()

if __name__ == "__main__":
    main()
