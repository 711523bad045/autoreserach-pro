class IEEEFormatter:

    @staticmethod
    def format(builder):

        report = builder.build()

        text = ""

        # Title
        text += f"# {report['title']}\n\n"

        # Abstract
        text += "## Abstract\n\n"
        text += report["abstract"] + "\n\n"

        # Keywords
        text += "## Keywords\n\n"
        text += ", ".join(report["keywords"]) + "\n\n"

        # Sections
        for section in report["sections"]:

            text += f"## {section['title']}\n\n"
            text += section["content"] + "\n\n"

        # Figures
        for i, figure in enumerate(report["figures"], 1):

            text += f"Figure {i}. {figure['title']}\n"
            text += f"[[IMAGE:{figure['image']}]]\n\n"

        # Tables
        for i, table in enumerate(report["tables"], 1):

            text += f"Table {i}. {table['title']}\n\n"

        # References
        text += "## References\n\n"

        for i, ref in enumerate(report["references"], 1):

            text += f"[{i}] {ref}\n"

        return text