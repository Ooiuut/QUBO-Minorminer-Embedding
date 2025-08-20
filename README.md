# QUBO → 2D Grid-of-Cliques Embedding (with Visualization)

This repository provides tools to:
1. Generate & visualize random QUBO graphs  
2. Build **2D hardware graphs** (grid of cliques / tiles)  
3. Embed QUBOs onto the hardware using **minorminer**  
4. Visualize both logical graphs and embeddings (chains, legend, labels)

> **Note:** minorminer only uses graph topology (edges). Layout coordinates are **only for plotting**.

---

## Installation

```bash
# Optional: create a venv
# python3 -m venv .venv && source .venv/bin/activate

pip install -U networkx matplotlib minorminer dwave-networkx
```

---

## Files

- `qubo_graph_strict.py` – generate random QUBO graphs with degree-density control  
- `grid_of_cliques_2d.py` – build & draw the **n×n grid-of-cliques** hardware  
- `embed_qubo_on_grid2d.py` – embed QUBOs into the 2D hardware and visualize them  
- `line_of_cliques_linear.py` – build & draw a **1D chain of cliques**  
- `demo_qubo_viz.py` – visualize a QUBO only (no embedding)

---

## Usage Examples

### 1. 1D line of cliques
```bash
# 8 groups, each group = clique of size 3
python3 line_of_cliques_linear.py --groups 8 --size 3
```

### 2. 2D grid-of-cliques (hardware only)
```bash
# Default: 5×5 grid, 3 nodes per group
python3 grid_of_cliques_2d.py

# 8×8 grid, 4 nodes per group; adjust layout for clarity
python3 grid_of_cliques_2d.py --n 8 --group_size 4 --x_gap 3.8 --y_gap 3.4 --radius 0.9

# Save the hardware figure
python3 grid_of_cliques_2d.py --n 6 --group_size 3 --save grid6.png
```

### 3. Embedding QUBO → 2D hardware
```bash
# Fixed 6×6 hardware, 3 nodes per group
python3 embed_qubo_on_grid2d.py --N 12 --d 0.35 --n 6 --group_size 3

# Start with 5×5 hardware, auto-expand until embedding succeeds
python3 embed_qubo_on_grid2d.py --N 14 --d 0.4 --n 5 --group_size 3 --auto_expand

# Customized plotting (wider figure, legend outside, bigger triangles)
python3 embed_qubo_on_grid2d.py --N 12 --d 0.35 --n 8 --group_size 4   --x_gap 3.8 --y_gap 3.4 --radius 0.9 --fig_w 20 --fig_h 8
```

---

## Parameters

### `grid_of_cliques_2d.py`
- `--n` (default 5) : grid size (n×n groups)  
- `--group_size` (default 3) : clique size per group  
- `--x_gap` (default 3.2) : horizontal spacing (plot only)  
- `--y_gap` (default 3.0) : vertical spacing (plot only)  
- `--radius` (default 0.85) : radius of polygon inside each group (plot only)  
- `--save` : filename to save the figure  

💡 **Tips:** Larger `group_size` = denser hardware = harder embedding. Increase gaps/radius if nodes overlap.

---

### `embed_qubo_on_grid2d.py`
**QUBO generation**
- `--N` (default 12) : number of logical variables  
- `--d` (default 0.35) : edge density (0–1)  
- `--mode` (`deterministic` or `probabilistic`, default probabilistic) : degree sampling mode  
- `--dist` (`uniform` or `normal`, default uniform) : distribution for probabilistic mode  
- `--sigma` (default 0.12) : stdev if using normal distribution  
- `--seed` (default 0) : RNG seed  

**Hardware graph**
- `--n` (default 6) : grid size  
- `--group_size` (default 3) : clique size per group  
- `--auto_expand` : flag, expand grid until embedding succeeds  

**Plotting**
- `--fig_w` (default 16) : figure width  
- `--fig_h` (default 8) : figure height  
- `--x_gap` (default 3.2), `--y_gap` (default 3.0) : spacing between groups  
- `--radius` (default 0.85) : polygon radius inside groups  

---

## Tips

- If embedding fails, try:
  - Lowering QUBO density (`--d`)  
  - Increasing grid size (`--n`)  
  - Enabling `--auto_expand`  
- Different seeds produce different random QUBOs (`--seed`).  
- Use `--save` to export figures for papers or debugging.  

---
