class KnowledgeBaseService:

    @staticmethod
    def build(evidence):

        kb = {

            "problems": [],

            "methods": [],

            "datasets": [],

            "results": [],

            "limitations": [],

            "future_work": [],

            "keywords": []
        }

        for item in evidence:

            if item.get("problem"):
                kb["problems"].append(item["problem"])

            if item.get("method"):
                kb["methods"].append(item["method"])

            if item.get("dataset"):
                kb["datasets"].append(item["dataset"])

            if item.get("result"):
                kb["results"].append(item["result"])

            if item.get("limitation"):
                kb["limitations"].append(item["limitation"])

            if item.get("future_work"):
                kb["future_work"].append(item["future_work"])

            kb["keywords"].extend(
                item.get("keywords", [])
            )

        kb["keywords"] = list(
            set(kb["keywords"])
        )

        return kb