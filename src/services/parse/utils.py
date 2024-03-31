from urllib.parse import urlparse, unquote
import os


def get_filename_from_cd(cd):
    """
    Extract filename from content-disposition header if available.
    """
    if not cd or "filename=" not in cd:
        return None
    fname = cd.split("filename=")[1].split(";")[0]
    if fname.lower().startswith(("'", '"')):
        fname = fname[1:-1]
    return unquote(fname)


def generate_filename_from_url(url):
    """
    Extract filename from URL if possible.
    """
    parsed_url = urlparse(url)
    return os.path.basename(parsed_url.path)
