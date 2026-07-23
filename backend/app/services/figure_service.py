import os
import matplotlib.pyplot as plt

from app.ai.workflow_agent import WorkflowAgent
from app.services.diagram_agent import DiagramAgent
from app.services.diagram_renderer import DiagramRenderer


class FigureService:

    @staticmethod
    def generate_all(project_id, topic, knowledge):

        os.makedirs("generated_diagrams", exist_ok=True)

        architecture = FigureService.generate_architecture(
            project_id,
            topic,
            knowledge
        )

        workflow = FigureService.generate_workflow(
            project_id,
            topic,
            knowledge
        )

        accuracy = FigureService.generate_accuracy_chart(
            project_id,
            topic,
            knowledge
        )

        comparison = FigureService.generate_comparison_chart(
            project_id,
            topic,
            knowledge
        )

        return {
            "architecture": architecture,
            "workflow": workflow,
            "accuracy": accuracy,
            "comparison": comparison,
        }

    @staticmethod
    def generate_architecture(project_id, topic, knowledge):

        diagram = DiagramAgent.generate_architecture(
            topic,
            knowledge
        )

        return DiagramRenderer.render(
            diagram,
            project_id
        )

    @staticmethod
    def generate_workflow(project_id, topic, knowledge):

        workflow = WorkflowAgent.generate(
            topic,
            knowledge
        )

        fig, ax = plt.subplots(figsize=(6, 10))

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        ax.axis("off")

        steps = workflow["steps"]

        gap = 0.8 / max(len(steps), 1)

        y = 0.9

        for step in steps:

            ax.text(
                0.5,
                y,
                step,
                ha="center",
                va="center",
                bbox=dict(
                    boxstyle="round",
                    fc="lightblue"
                )
            )

            if y > 0.12:

                ax.annotate(
                    "",
                    xy=(0.5, y-gap+0.02),
                    xytext=(0.5, y-0.03),
                    arrowprops=dict(
                        arrowstyle="->"
                    )
                )

            y -= gap

        output = f"generated_diagrams/{project_id}_workflow.png"

        plt.savefig(
            output,
            bbox_inches="tight"
        )

        plt.close()

        return output

    @staticmethod
    def generate_accuracy_chart(project_id, topic, knowledge):

        labels = [
            "Existing",
            "Improved",
            "Proposed"
        ]

        base = 88

        if "blockchain" in topic.lower():
            base = 90

        elif "alzheimer" in topic.lower():
            base = 92

        elif "federated" in topic.lower():
            base = 91

        elif "iot" in topic.lower():
            base = 89

        values = [
            base,
            base + 3,
            base + 6
        ]

        plt.figure(figsize=(6,4))

        plt.bar(labels, values)

        plt.title(f"{topic}\nAccuracy Comparison")

        plt.ylabel("Accuracy (%)")

        output = f"generated_diagrams/{project_id}_accuracy.png"

        plt.savefig(output,bbox_inches="tight")

        plt.close()

        return output

    @staticmethod
    def generate_comparison_chart(project_id, topic, knowledge):

        metrics = [
            "Accuracy",
            "Precision",
            "Recall",
            "F1"
        ]

        if "blockchain" in topic.lower():

            proposed = [98,97,97,98]
            existing = [91,90,90,90]

        elif "alzheimer" in topic.lower():

            proposed = [97,96,95,96]
            existing = [89,88,88,88]

        elif "federated" in topic.lower():

            proposed = [96,95,95,95]
            existing = [88,87,86,87]

        else:

            proposed = [95,94,94,94]
            existing = [88,87,87,87]

        x = range(len(metrics))

        plt.figure(figsize=(7,4))

        plt.plot(
            x,
            existing,
            marker="o",
            label="Existing"
        )

        plt.plot(
            x,
            proposed,
            marker="o",
            label="Proposed"
        )

        plt.xticks(
            x,
            metrics
        )

        plt.ylabel("Score")

        plt.title(topic)

        plt.legend()

        output = f"generated_diagrams/{project_id}_comparison.png"

        plt.savefig(
            output,
            bbox_inches="tight"
        )

        plt.close()

        return output