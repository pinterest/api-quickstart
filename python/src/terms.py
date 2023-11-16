from api_object import ApiObject


class Terms(ApiObject):
    def __init__(self, api_config, access_token):
        super().__init__(api_config, access_token)

    # https://developers.pinterest.com/docs/api/v5/#tag/terms

    def get_related(self, terms):
        path = super().add_query("/v5/terms/related", {"terms": terms})
        return super().request_data(path)

    @classmethod
    def print_related_terms(cls, related_terms):
        print("--- Related Terms ---")
        print("First Input Term:", related_terms["id"])
        print("Count:", related_terms["related_term_count"])
        for entry in related_terms["related_terms_list"]:
            print("Term:", entry["term"])
            for related_term in entry["related_terms"]:
                print("  Related Term:", related_term)
        print("---------------------")

    def get_suggested(self, terms, limit=None):
        query = {"term": terms}
        if limit:
            query["limit"] = limit
        path = super().add_query("/v5/terms/suggested", query)
        return super().request_data(path)

    @classmethod
    def print_suggested_terms(cls, suggested_terms):
        print("--- Suggested Terms ---")
        for term in suggested_terms:
            print("Term:", term)
        print("-----------------------")
