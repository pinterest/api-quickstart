from api_media_object import ApiMediaObject


class Pin(ApiMediaObject):
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
        print("Title:", pin_data["title"])
        print("Description:", pin_data["description"])
        print("Link:", pin_data["link"])
        print("Section ID:", pin_data["board_section_id"])
        print("Domain:", pin_data.get("domain"))
        # print('Native format type: ' + pin_data['native_format_type'])
        print("--------------------")

    # https://developers.pinterest.com/docs/api/v5/#operation/pins/save
    def save(self, board_id, section=None):
        if not self.pin_id:
            raise RuntimeError("pin_id must be set to save a pin")

        save_data = {"board_id": board_id}
        if section:
            save_data["board_section_id"] = section

        return self.post_data(f"/v5/pins/{self.pin_id}/save", save_data)

    @classmethod
    def max_resolution_image_url(cls, pin_data):
        max_res = 0
        url = None
        for image in pin_data["media"]["images"].values():
            if image["width"] > max_res:
                max_res = image["width"]
                url = image["url"]
            if image["height"] > max_res:
                max_res = image["height"]
                url = image["url"]
        return url

    # https://developers.pinterest.com/docs/api/v5/#operation/pins/create
    def create(self, pin_data, board_id, section=None, media=None):
        """
        Create a pin from a pin_data structure that is returned by GET.
        Use the board_id and (optional) section arguments to indicate
        where the pin should be created. Use the media argument (either
        a media identifier or the file name of a video file) to create
        a Video Pin.
        """
        OPTIONAL_ATTRIBUTES = [
            "link",
            "title",
            "description",
            "alt_text",
        ]
        create_data = {
            "board_id": board_id,
        }

        # https://developers.pinterest.com/docs/solutions/content-apps/#creatingvideopins
        media_id = self.media_to_media_id(media)

        image_url = self.max_resolution_image_url(pin_data)
        if media_id:
            self.check_media_id(media_id)
            create_data["media_source"] = {
                "source_type": "video_id",
                "cover_image_url": image_url,
                "media_id": media_id,
            }
        else:
            create_data["media_source"] = {"source_type": "image_url", "url": image_url}

        if section:
            create_data["board_section_id"] = section

        for key in OPTIONAL_ATTRIBUTES:
            value = pin_data.get(key)
            if value:
                create_data[key] = value

        pin_data = self.post_data("/v5/pins", create_data)
        self.pin_id = pin_data["id"]
        return pin_data

    # https://developers.pinterest.com/docs/api/v5/#operation/media/create
    def upload_media(self, media_path):
        """
        Upload a video from the specified path and return a media_id.
        Called by ApiMediaObject:media_to_media_id().
        """
        media_upload = self.post_data("/v5/media", {"media_type": "video"})
        self.upload_file_multipart(
            media_upload["upload_url"], media_path, media_upload["upload_parameters"]
        )
        return media_upload["media_id"]

    # https://developers.pinterest.com/docs/api/v5/#operation/media/get
    def check_media_id(self, media_id):
        """
        Poll for the status of the media until it is complete.
        """
        self.reset_backoff()
        while True:
            media_response = self.request_data(f"/v5/media/{media_id}")
            status = media_response.get("status")
            if not status:
                raise RuntimeError(f"media upload {media_id} not found")
            if status == "succeeded":
                return
            if status == "failed":
                raise RuntimeError(f"media upload {media_id} failed")

            self.wait_backoff(f"Media id {media_id} status: {status}.")
