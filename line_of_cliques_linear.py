import argparse
import networkx as nx
import matplotlib.pyplot as plt

def build_line_of_cliques(num_groups: int, group_size: int = 3) -> nx.Graph:
    G = nx.Graph()
    
    for g in range(num_groups):
        for i in range(group_size):
            G.add_node(('g', g, i), group=g, idx=i)
    
    for g in range(num_groups):
        nodes = [('g', g, i) for i in range(group_size)]
        for a in range(group_size):
            for b in range(a + 1, group_size):
                G.add_edge(nodes[a], nodes[b], kind='intra')
    
    for g in range(num_groups - 1):
        A = [('g', g, i) for i in range(group_size)]
        B = [('g', g + 1, j) for j in range(group_size)]
        for u in A:
            for v in B:
                G.add_edge(u, v, kind='inter')
    return G

def layout_line(num_groups: int, group_size: int = 3, x_gap=2.6, y_gap=1.2, x_jitter=0.5):
    pos = {}
    for g in range(num_groups):
        x = g * x_gap
        y0 = -0.5 * (group_size - 1) * y_gap
        for i in range(group_size):
            offset = (i - (group_size - 1) / 2.0) * x_jitter
            extra = -1.5 if i == 2 else 0.0
            pos[('g', g, i)] = (x + offset + extra, y0 + i * y_gap)
    return pos

def draw_physical_graph(G: nx.Graph, title="Line of cliques", jitter=0.5, curve_short=0.18, curve_long=-0.22):
    groups = sorted(set(g for (_, g, _) in G.nodes()))
    group_size = max(i for (_, _, i) in G.nodes()) + 1 if G.number_of_nodes() else 0
    pos = layout_line(len(groups), group_size, x_jitter=jitter)

    intra = [(u, v) for u, v, d in G.edges(data=True) if d.get('kind') == 'intra']
    inter = [(u, v) for u, v, d in G.edges(data=True) if d.get('kind') == 'inter']

    cmap = plt.cm.get_cmap("tab10", max(1, len(groups)))
    node_colors = [cmap(G.nodes[n]['group'] % 10) for n in G.nodes()]

    plt.figure(figsize=(max(10, len(groups) * 1.6), 4))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=420,
                           edgecolors="black", linewidths=1.0)
    if intra:
        intra_short = []
        intra_long = []
        for u, v in intra:
            du = abs(u[2] - v[2])
            if du == 1:
                intra_short.append((u, v))
            else:
                intra_long.append((u, v))
        if intra_short:
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=intra_short,
                width=1.6,
                edge_color="#444",
                style="solid",
                connectionstyle=f"arc3,rad={curve_short}",
            )
        if intra_long:
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=intra_long,
                width=1.6,
                edge_color="#444",
                style="solid",
                connectionstyle=f"arc3,rad={curve_long}",
            )
    if inter:
        nx.draw_networkx_edges(G, pos, edgelist=inter, width=1.2, edge_color="#666", style="dotted")
    for g in groups:
        xs = [pos[('g', g, i)][0] for i in range(group_size)]
        xcenter = sum(xs) / len(xs)
        plt.text(xcenter, 1.8, f"group {g}", ha="center", fontsize=10)
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

def main():
    ap = argparse.ArgumentParser(description="Line of cliques (linear only)")
    ap.add_argument("--groups", type=int, default=6)
    ap.add_argument("--size", type=int, default=3)
    ap.add_argument("--save", type=str, default="")
    ap.add_argument("--jitter", type=float, default=0.9)
    ap.add_argument("--curve_short", type=float, default=0.28)
    ap.add_argument("--curve_long", type=float, default=-0.32)
    args = ap.parse_args()

    G = build_line_of_cliques(args.groups, args.size)
    draw_physical_graph(
        G,
        title=f"Line of cliques (groups={args.groups}, size={args.size})",
        jitter=args.jitter,
        curve_short=args.curve_short,
        curve_long=args.curve_long,
    )
    if args.save:
        plt.savefig(args.save, dpi=220, bbox_inches="tight")

if __name__ == "__main__":
    main()