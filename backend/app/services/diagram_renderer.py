import matplotlib.pyplot as plt
import networkx as nx
import os


class DiagramRenderer:

    @staticmethod
    def render(diagram, project_id):

        G = nx.DiGraph()

        for node in diagram["nodes"]:
            G.add_node(node)

        for edge in diagram["edges"]:
            G.add_edge(edge[0], edge[1])

        plt.figure(figsize=(12,7))

        pos = nx.spring_layout(
            G,
            seed=42
        )

        nx.draw_networkx(
            G,
            pos,
            node_size=4000,
            arrows=True,
            font_size=10
        )

        os.makedirs("generated_diagrams", exist_ok=True)

        path = f"generated_diagrams/{project_id}_architecture.png"

        plt.savefig(
            path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        return path