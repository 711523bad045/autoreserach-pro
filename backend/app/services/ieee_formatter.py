class IEEEFormatter:

    @staticmethod
    def format(builder):

        report = builder.build()

        text = ""

        # Title
        text += f"# {report['title']}\n\n"

        # Abstract — IEEE convention is a single unlabeled paragraph
        # prefixed with a bold "Abstract—", not its own heading. Skipped
        # entirely if empty so we never render a blank "Abstract" header.
        abstract = (report.get("abstract") or "").strip()
        if abstract:
            text += f"**Abstract—** {abstract}\n\n"

        # Keywords — same convention: inline, not a heading. Skipped if
        # empty for the same reason.
        keywords = report.get("keywords") or []
        if keywords:
            text += f"**Keywords—** {', '.join(keywords)}\n\n"

        # Sections — numbered, IEEE-style uppercase headings (e.g.
        # "1. INTRODUCTION"). Defensively strips any stray leading '#'
        # characters in case upstream parsing ever leaks raw markdown into
        # a title.
        for i, section in enumerate(report["sections"], 1):
            title = (section.get("title") or "").lstrip("#").strip()
            content = (section.get("content") or "").strip()

            if not title:
                continue

            text += f"## {i}. {title.upper()}\n\n"
            if content:
                text += f"{content}\n\n"

        # Figures
        for i, figure in enumerate(report["figures"], 1):
            text += f"Figure {i}. {figure['title']}\n"
            text += f"[[IMAGE:{figure['image']}]]\n\n"

        # Tables
        for i, table in enumerate(report["tables"], 1):
            text += f"Table {i}. {table['title']}\n\n"

        # References — only render the heading if there's actually
        # something to list, matching the sample report's structure.
        references = report.get("references") or []
        if references:
            text += "## References\n\n"
            for i, ref in enumerate(references, 1):
                text += f"[{i}] {ref}\n"

        return text