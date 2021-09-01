from api_object import ApiObject


class Pin(ApiObject):
    def __init__(self, pin_id, api_config, access_token):
        super().__init__(api_config, access_token)
        self.pin_id = pin_id

    # https://developers.pinterest.com/docs/api/v5/#operation/pins/get
    def get(self):
        return self.request_data("/v5/pins/{}".format(self.pin_id))

    @classmethod
    def print_summary(cls, pin_data):
        print("--- Pin Summary ---")
        print("Pin ID:", pin_data["id"])
        print("Description:", pin_data["description"])
        print("Link:", pin_data["link"])
        print("Section ID:", pin_data["board_section_id"])
        print("Domain:", pin_data.get("domain"))
        # print('Native format type: ' + pin_data['native_format_type'])
        print("--------------------")

    # https://developers.pinterest.com/docs/api/v5/#operation/pins/create
    def create(self, pin_data, board_id, section=None):
        OPTIONAL_ATTRIBUTES = [
            "link",
            "title",
            "description",
            "alt_text",
        ]
        create_data = {
            "board_id": board_id,
            "media_source": {
                "source_type": "image_url",
                "url": pin_data["media"]["images"]["originals"]["url"],
            },
        }
        if section:
            create_data["board_section_id"] = section

        for key in OPTIONAL_ATTRIBUTES:
            value = pin_data.get(key)
            if value:
                create_data[key] = value

        pin_data = self.post_data("/v5/pins", create_data)
        self.pin_id = pin_data["id"]
        return pin_data
