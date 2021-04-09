import requests

def download_file(url, path):
    """
    Use streaming HTTP request to download a file.
    """
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(path, 'wb') as output:
            # use typical disk block size as chunk_size
            for chunk in response.iter_content(chunk_size=4096):
                output.write(chunk)
