class ReportBuilder:

    def __init__(self):

        self.report = {
            "title": "",
            "abstract": "",
            "keywords": [],
            "sections": [],
            "figures": [],
            "tables": [],
            "references": []
        }

    def set_title(self, title):

        self.report["title"] = title

    def set_abstract(self, text):

        self.report["abstract"] = text

    def set_keywords(self, keywords):
        """
        Bulk-assign keywords. Use this instead of setting `builder.keywords`
        directly — that would create a stray attribute on the builder
        object itself rather than updating self.report["keywords"], which
        is what build() actually returns.
        """
        self.report["keywords"] = list(keywords or [])

    def add_keyword(self, keyword):

        self.report["keywords"].append(keyword)

    def add_section(self, title, content):

        self.report["sections"].append({
            "title": title,
            "content": content
        })

    def add_figure(self, title, image):

        self.report["figures"].append({
            "title": title,
            "image": image
        })

    def add_table(self, title, rows):

        self.report["tables"].append({
            "title": title,
            "rows": rows
        })

    def add_reference(self, ref):

        self.report["references"].append(ref)

    def build(self):

        return self.report