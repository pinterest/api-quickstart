import re
import time

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

        media_id = self.media_to_media_id(media)
        self.check_media_id(media_id)

        image_url = pin_data["media"]["images"]["originals"]["url"]
        if media_id:
            create_data["media_source"] = {
                "source_type": "video_id",
                "cover_image_url": image_url,
                "media_id": media_id
            }
        else:
            create_data["media_source"] = {
                "source_type": "image_url",
                "url": image_url
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

    # https://developers.pinterest.com/docs/solutions/content-apps/#creatingvideopins
    def media_to_media_id(self, media):
        """
        This function translates the media argument into a media_id, which may be one of:
           <falsy>     => no video creation is required
           <file path> => create a media_id from the video in the file path
           media_id    => an existing media identifier
        """
        if not media:
            return media

        try: # check whether media is a readable file path
            open(media, "r").close()
        except OSError:
            # media is not a readable file path. check whether it is a valid media_id
            if re.match(r"^\w*\d+$", media):
                return media
            raise ValueError(f"invalid media: {media}")

        # valid file found
        return self.upload_video(media)

    # https://developers.pinterest.com/docs/api/v5/#operation/media/create
    def upload_video(self, media_path):
        """
        Upload a video from the specified path and return a media_id.
        """
        media_upload = self.post_data("/v5/media", {"media_type": "video"})
        self.upload_file_multipart(media_upload["upload_url"],
                                   media_path,
                                   media_upload["upload_parameters"])
        return media_upload['media_id']

    def check_media_id(self, media_id):
        # poll for successful status (TODO: refactor with async_report delay loop)
        delay = 1 # for backoff algorithm
        while True:
            media_response = self.request_data(f"/v5/media/{media_id}")
            status = media_response["status"]
            if status == "succeeded":
                return
            if status == "failed":
                raise RuntimeError(f"upload to {media_path} failed with status: {status}")
            time.sleep(delay)
            delay = min(delay * 2, 10)
