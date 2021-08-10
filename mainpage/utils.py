from pathlib import Path
from django.conf import settings


def get_banner_upload_path(instance, filename):
    return str(Path(settings.BANNER_FOLDER, filename))
