import requests

def download_file(url, path):
    """
    Use streaming HTTP request to download a file.
    """
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(path, "wb") as output:
            # use typical disk block size as chunk_size
            for chunk in response.iter_content(chunk_size=4096):
                output.write(chunk)

def upload_file_multipart(url, path, file_parameter, data):
    """
    Upload a file in a form. For example, use this function
    for uploading a file to Amazon S3 with the parameters
    returned from the Pinterest media API.
    """
    with open(path, "rb") as file_object:
        response = requests.post(
            url,
            data=data,
            files={file_parameter: (None, file_object)})

