import os
import textwrap

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import networkx as nx


# Visual constants — tuned so wrapped labels fit comfortably inside boxes
# without overlapping neighbors, unlike the old spring_layout + giant
# circle-node approach.
BOX_WIDTH = 2.6
BOX_HEIGHT = 0.9
LAYER_GAP_Y = 1.6
NODE_GAP_X = 0.6
WRAP_CHARS = 22
FONT_SIZE = 9


class DiagramRenderer:

    @staticmethod
    def _wrap(label: str) -> str:
        return "\n".join(textwrap.wrap(label, WRAP_CHARS)) or label

    @staticmethod
    def _layered_positions(G: "nx.DiGraph"):
        """
        Assign each node to a horizontal layer based on topological depth,
        then space nodes within each layer evenly. Falls back to a simple
        grid if the graph has a cycle (shouldn't happen for an
        architecture diagram, but better than crashing).
        """
        try:
            generations = list(nx.topological_generations(G))
        except (nx.NetworkXUnfeasible, nx.NetworkXError):
            # Not a DAG — fall back to a plain grid so we still render
            # something legible instead of erroring out.
            nodes = list(G.nodes)
            generations = [nodes[i:i + 4] for i in range(0, len(nodes), 4)]

        positions = {}

        for layer_idx, layer_nodes in enumerate(generations):
            n = len(layer_nodes)
            total_width = n * BOX_WIDTH + (n - 1) * NODE_GAP_X
            start_x = -total_width / 2

            y = -layer_idx * LAYER_GAP_Y

            for i, node in enumerate(layer_nodes):
                x = start_x + i * (BOX_WIDTH + NODE_GAP_X) + BOX_WIDTH / 2
                positions[node] = (x, y)

        return positions

    @staticmethod
    def render(diagram, project_id):

        G = nx.DiGraph()

        for node in diagram["nodes"]:
            G.add_node(node)

        for edge in diagram["edges"]:
            G.add_edge(edge[0], edge[1])

        if len(G.nodes) == 0:
            # Nothing to draw — avoid producing a blank/broken image.
            G.add_node("No architecture data available")

        pos = DiagramRenderer._layered_positions(G)

        num_layers = len({round(y, 3) for _, y in pos.values()}) or 1
        max_layer_width = max(
            (len([1 for p in pos.values() if p[1] == y])
             for y in {p[1] for p in pos.values()}),
            default=1,
        )

        fig_width = max(8, max_layer_width * (BOX_WIDTH + NODE_GAP_X))
        fig_height = max(4, num_layers * LAYER_GAP_Y + 1)

        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.axis("off")
        ax.set_aspect("equal")

        # Draw boxes
        for node, (x, y) in pos.items():
            box = FancyBboxPatch(
                (x - BOX_WIDTH / 2, y - BOX_HEIGHT / 2),
                BOX_WIDTH,
                BOX_HEIGHT,
                boxstyle="round,pad=0.05,rounding_size=0.08",
                linewidth=1.3,
                edgecolor="#2c5f8a",
                facecolor="#cfe6f7",
            )
            ax.add_patch(box)

            ax.text(
                x, y,
                DiagramRenderer._wrap(str(node)),
                ha="center",
                va="center",
                fontsize=FONT_SIZE,
                wrap=True,
            )

        # Draw arrows, clipped to box edges rather than box centers so
        # they don't visually cut through the text.
        for src, dst in G.edges:
            x1, y1 = pos[src]
            x2, y2 = pos[dst]

            arrow = FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                arrowstyle="-|>",
                mutation_scale=14,
                linewidth=1.2,
                color="#444444",
                shrinkA=BOX_HEIGHT * 40,
                shrinkB=BOX_HEIGHT * 40,
                connectionstyle="arc3,rad=0.05",
            )
            ax.add_patch(arrow)

        all_x = [x for x, _ in pos.values()]
        all_y = [y for _, y in pos.values()]
        ax.set_xlim(min(all_x) - BOX_WIDTH, max(all_x) + BOX_WIDTH)
        ax.set_ylim(min(all_y) - BOX_HEIGHT, max(all_y) + BOX_HEIGHT)

        os.makedirs("generated_diagrams", exist_ok=True)

        path = f"generated_diagrams/{project_id}_architecture.png"

        plt.savefig(
            path,
            dpi=300,
            bbox_inches="tight",
        )

        plt.close(fig)

        return path