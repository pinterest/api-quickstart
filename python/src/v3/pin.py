import json

from api_media_object import ApiMediaObject


class Pin(ApiMediaObject):
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
        pin_type = pin_data.get("type")
        print(f"Type: {pin_type}")
        if not pin_type or pin_type == "pin":
            print(f"Description: {pin_data.get('description')}")
            print(f"Domain: {pin_data.get('domain')}")
            print(f"Native format type: {pin_data.get('native_format_type')}")
        elif pin_type == "story":
            print(f"Story type: {pin_data.get('story_type')}")
        print("--------------------")

    # https://developers.pinterest.com/docs/redoc/#operation/v3_partner_save_handler_POST
    # This method is only for the sake of completeness. In general, it's better to use
    # API version 5. In the v3 API, this endpoint is limited to certain kinds of
    # partners (e.g. the "pinner_app" category).
    def save(self, board_id, section=None):
        if not self.pin_id:
            raise RuntimeError("pin_id must be set to save a pin")

        save_data = {"board_id": board_id}
        if section:
            save_data["board_section_id"] = section

        return self.post_data(f"/v3/partners/pins/{self.pin_id}/save/", save_data)

    # https://developers.pinterest.com/docs/redoc/#operation/v3_create_pin_handler_PUT
    def create(self, pin_data, board_id, section=None, media=None):
        OPTIONAL_ATTRIBUTES = [
            "alt_text",
            "description",
            "title",
        ]
        create_data = {"board_id": board_id, "image_url": pin_data["image_large_url"]}

        # https://developers.pinterest.com/docs/redoc/#section/Using-video-APIs
        media_id = self.media_to_media_id(media)

        if media_id:
            self.check_upload_id(media_id)
            create_data["media_upload_id"] = media_id

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

    # https://developers.pinterest.com/docs/redoc/#operation/register_media_upload_POST
    def upload_media(self, media_path):
        """
        Upload a video from the specified path and return a media_id.
        Called by ApiMediaObject:media_to_media_id().
        """
        media_upload = self.post_data("/v3/media/uploads/register/", {"type": "video"})
        self.upload_file_multipart(
            media_upload["upload_url"], media_path, media_upload["upload_parameters"]
        )
        return media_upload["upload_id"]

    # https://developers.pinterest.com/docs/redoc/#operation/get_media_uploads_GET
    def check_upload_id(self, upload_id):
        """
        Poll for the status of the upload until it is complete.
        """
        self.reset_backoff()
        while True:
            media_response = self.request_data(
                f"/v3/media/uploads/?upload_ids={upload_id}"
            )
            upload_record = media_response.get(upload_id)
            if not upload_record:
                raise RuntimeError(f"upload {upload_id} not found")
            status = upload_record.get("status")
            if not status:
                raise RuntimeError(f"upload {upload_id} has no status")
            if status == "succeeded":
                return
            if status == "failed":
                failure_code = upload_record.get("failure_code", "unknown")
                raise RuntimeError(
                    f"upload {upload_id} failed with code: {failure_code}"
                )
            self.wait_backoff(f"Upload {upload_id} status: {status}.")
