import requests

from api_object import ApiObject


class ApiMediaObject(ApiObject):
    """
    Subclass of an ApiObject with media functionality.
    """

    def __init__(self, api_config, access_token):
        super().__init__(api_config, access_token)

    def upload_media(self, media):
        """
        The implementation of this function depends on the API version,
        so it must be overridden in the subclass for each version of the API.
        """
        raise RuntimeError("upload_media() must be overridden")

    def media_to_media_id(self, media):
        """
        This function translates the media argument into a media_id,
        which may be one of:
          <falsy>     => no video creation is required
          <file path> => create a media_id from the video in the file path
          media_id    => an existing media identifier

        Reference:
          https://developers.pinterest.com/docs/solutions/content-apps/#creatingvideopins
        """  # noqa: E501 because the long URL is okay
        if not media:
            return media

        try:  # check whether media is a readable file path
            open(media, "r").close()
        except OSError:
            # media is not a readable file path. check whether it is a valid media_id
            if media.isdigit():
                return media
            raise ValueError(f"invalid media: {media}") from None

        # valid file found
        return self.upload_media(media)

    def upload_file_multipart(self, url, file_path, post_data):
        """
        Upload a file in a form. For example, use this function
        for uploading a file to Amazon S3 with the parameters
        returned from the Pinterest media API.
        """
        if self.api_config.verbosity >= 2:
            print(f"POST {url} from {file_path}")

        if self.api_config.verbosity >= 3:
            self.api_config.credentials_warning()
            print(post_data)

        with open(file_path, "rb") as file_object:
            response = requests.post(
                url, data=post_data, files={"file": (None, file_object)}
            )
            self.check(response)
