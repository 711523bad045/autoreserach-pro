from app.llm.groq_client import GroqClient


class ReportPlannerService:

    def __init__(self):
        self.llm = GroqClient()

    def create_plan(
        self,
        title: str,
        description: str = "",
        objective: str = "",
        requirements: str = "",
        domain: str = "",
    ):

        prompt = f"""
You are an experienced IEEE research paper planner.

Create a structured plan for the following research project.

Project Title:
{title}

Project Description:
{description}

Research Objective:
{objective}

Requirements:
{requirements}

Research Domain:
{domain}

Return ONLY the following format.

SECTION:
Abstract

SECTION:
Keywords

SECTION:
Introduction

SECTION:
Literature Review

SECTION:
Research Gap

SECTION:
Problem Statement

SECTION:
Proposed Methodology

SECTION:
System Architecture

SECTION:
Workflow

SECTION:
Implementation

SECTION:
Experimental Results

SECTION:
Performance Analysis

SECTION:
Future Scope

SECTION:
Conclusion

SECTION:
References

DIAGRAM:
Architecture Diagram

DIAGRAM:
Workflow Diagram

TABLE:
Literature Comparison

TABLE:
Performance Comparison

CHART:
Publication Year Distribution

CHART:
Citation Distribution
"""

        try:

            response = self.llm.generate(prompt)

            return self.parse_plan(response)

        except Exception:

            return self.default_plan()

    def parse_plan(self, text):

        plan = {
            "sections": [],
            "diagrams": [],
            "tables": [],
            "charts": [],
        }

        current = None

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            if line.startswith("SECTION:"):
                current = "sections"
                plan[current].append(
                    line.replace("SECTION:", "").strip()
                )

            elif line.startswith("DIAGRAM:"):
                current = "diagrams"
                plan[current].append(
                    line.replace("DIAGRAM:", "").strip()
                )

            elif line.startswith("TABLE:"):
                current = "tables"
                plan[current].append(
                    line.replace("TABLE:", "").strip()
                )

            elif line.startswith("CHART:"):
                current = "charts"
                plan[current].append(
                    line.replace("CHART:", "").strip()
                )

        if len(plan["sections"]) == 0:
            return self.default_plan()

        return plan

    def default_plan(self):

        return {
            "sections": [
                "Abstract",
                "Keywords",
                "Introduction",
                "Literature Review",
                "Research Gap",
                "Problem Statement",
                "Proposed Methodology",
                "System Architecture",
                "Workflow",
                "Implementation",
                "Experimental Results",
                "Performance Analysis",
                "Future Scope",
                "Conclusion",
                "References",
            ],
            "diagrams": [
                "Architecture Diagram",
                "Workflow Diagram",
            ],
            "tables": [
                "Literature Comparison",
                "Performance Comparison",
            ],
            "charts": [
                "Publication Year Distribution",
                "Citation Distribution",
            ],
        }