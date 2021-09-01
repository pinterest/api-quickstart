import json

from api_object import ApiObject


class Pin(ApiObject):
    def __init__(self, pin_id, api_config, access_token):
        super().__init__(api_config, access_token)
        self.pin_id = pin_id

    # https://developers.pinterest.com/docs/redoc/#operation/v3_get_pin_GET
    def get(self):
        if not self.pin_id:
            raise ValueError("pin_id must be set to get a pin")
        return self.request_data("/v3/pins/{}/".format(self.pin_id))

    @classmethod
    def print_summary(cls, pin_data):
        print("--- Pin Summary ---")
        print(f"Pin ID: {pin_data['id']}")
        print(f"Type: {pin_data['type']}")
        if pin_data["type"] == "pin":
            print(f"Description: {pin_data.get('description')}")
            print(f"Domain: {pin_data.get('domain')}")
            print(f"Native format type: {pin_data.get('native_format_type')}")
        elif pin_data["type"] == "story":
            print(f"Story type: {pin_data.get('story_type')}")
        print("--------------------")

    # https://developers.pinterest.com/docs/redoc/#operation/v3_create_pin_handler_PUT
    def create(self, pin_data, board_id, section=None):
        OPTIONAL_ATTRIBUTES = [
            "alt_text",
            "description",
            "title",
        ]
        create_data = {"board_id": board_id, "image_url": pin_data["image_large_url"]}
        if section:
            create_data["section"] = section
        link = pin_data.get("link")
        if link:
            create_data["source_url"] = link
        carousel_data = pin_data.get("carousel_data")
        if carousel_data:
            create_data["carousel_data_json"] = json.dumps(
                carousel_data, separators=(",", ":")
            )

        for key in OPTIONAL_ATTRIBUTES:
            value = pin_data.get(key)
            if value:
                create_data[key] = value

        pin_data = self.put_data("/v3/pins/", create_data)
        self.pin_id = pin_data["id"]
        return pin_data
