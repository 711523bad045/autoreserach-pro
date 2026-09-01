# AutoResearch Pro

### AI-Powered Research Report Generator

AutoResearch Pro is a full-stack AI research assistant designed to automate the process of discovering relevant research papers, analyzing research information, and generating structured research reports.

The system provides a workspace where users can create research projects, enter a research topic and objective, generate reports, inspect research sources, view individual sections, and preview the generated report in an IEEE-style format.

---

## Overview

Research work normally requires searching through multiple academic sources, reading papers, identifying important findings, organizing information, and preparing a structured report.

AutoResearch Pro aims to simplify this workflow by combining:

- Academic research discovery
- Semantic research retrieval
- Research-paper ranking
- Evidence extraction
- Knowledge-base processing
- AI-assisted report generation
- Research gap analysis
- Tables and diagrams
- IEEE-style report formatting
- PDF and Word export
- Report-based AI assistance

---

## Key Features

### Research Discovery

The system searches for research papers related to the user's topic using academic research APIs.

Primary research sources include:

- Semantic Scholar
- OpenAlex

The system is designed with a fallback mechanism so that OpenAlex can be used when the primary research provider is unavailable.

---

### Research Paper Ranking

Retrieved papers can be processed and ranked according to research relevance and other available paper information.

This helps the system prioritize useful research sources before generating the final report.

---

###  Evidence-Based Research Processing

Research information is processed into structured evidence such as:

- Research problem
- Methodology
- Dataset
- Results
- Limitations
- Future work
- Keywords

This structured information can then be used as context for AI-assisted report generation.

---

### Knowledge Base

AutoResearch Pro organizes extracted research information into a knowledge base.

The knowledge base can contain information related to:

- Problems
- Methods
- Datasets
- Results
- Limitations
- Future research
- Keywords

This provides structured research context for downstream report generation.

---

###  AI Research Agent

The project uses an AI agent workflow to process research information and generate academic content.

The LLM layer is separated from the rest of the application, making the architecture easier to maintain and extend.

---

###  AI-Generated Tables, Charts and Diagrams

The backend contains dedicated services and agents for research visuals, including:

- Tables
- Charts
- Mermaid diagrams
- Research workflow diagrams
- Architecture diagrams
- Figures

These components are designed to make generated research reports more informative and structured.

---

###  IEEE Report Preview

Generated research can be displayed in an IEEE-style report interface.

The application provides an IEEE preview containing:

- Research title
- Author information
- Abstract
- Keywords
- Structured research content
- Multi-column academic layout

---

###  Ask About the Report

The report interface includes an AI assistant that allows users to ask questions about the generated report.

Users can ask about:

- Findings
- Methods
- Research sections
- Report content

The assistant is designed to ground responses in the generated research content.

---

###  Export

The application provides export options for generated reports.

Supported formats include:

- Word
- PDF

---

## <img width="1917" height="1045" alt="Screenshot 2026-09-01 093344" src="https://github.com/user-attachments/assets/7f3008c6-8204-4337-ba51-2eb47af834dd" />
<img width="1917" height="1017" alt="Screenshot 2026-09-01 093352" src="https://github.com/user-attachments/assets/f6ad737a-e21b-451d-bcf2-ad301153ae26" />
<img width="1906" height="905" alt="Screenshot 2026-09-01 093530" src="https://github.com/user-attachments/assets/d1e883cd-a46b-4728-831c-af3cd5c244a8" />
<img width="1917" height="942" alt="Screenshot 2026-09-01 093540" src="https://github.com/user-attachments/assets/b5bb5947-fda9-41cd-9d4d-2c28d60ebf3d" />
<img width="1917" height="951" alt="Screenshot 2026-09-01 093606" src="https://github.com/user-attachments/assets/5de4b5ed-8329-4613-9719-e91da8ecb5b2" />
Application Workflow

```text
                    User
                     │
                     ▼
             Create Research Project
                     │
                     ▼
              Enter Research Topic
                     │
                     ▼
             Define Research Objective
                     │
                     ▼
            Specify Report Requirements
                     │
                     ▼
             Research Discovery
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
   Semantic Scholar           OpenAlex
          │                     │
          └──────────┬──────────┘
                     ▼
              Paper Ranking
                     │
                     ▼
             Evidence Extraction
                     │
                     ▼
              Knowledge Base
                     │
                     ▼
              Research Gap
                     │
                     ▼
             Report Planning
                     │
                     ▼
                AI Agent
                     │
                     ▼
             Report Generation
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Sections    Tables     Figures
          │          │          │
          └──────────┼──────────┘
                     ▼
             IEEE Formatting
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
     Web Report             IEEE Preview
          │
          ├──────────► Word
          │
          └──────────► PDF
