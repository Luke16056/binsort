"""Photo Prep: checks the upload, shrinks it and strips its metadata (including GPS location).

Interface: prepare(photo: bytes) -> bytes
"""
import io

from PIL import Image, ImageOps, UnidentifiedImageError
from pillow_heif import register_heif_opener

register_heif_opener()  # lets Pillow open iPhone HEIC/HEIF photos

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_SIDE = 1024  # pixels; plenty for the AI and keeps the request small
# MPO = the multi-picture JPEG many phones save; HEIF = iPhone .heic photos
ALLOWED_FORMATS = {"JPEG", "MPO", "PNG", "WEBP", "HEIF"}


class BadPhoto(ValueError):
    """The upload is not a photo BinSort can use."""


def prepare(photo: bytes) -> bytes:
    if not photo:
        raise BadPhoto("No photo was uploaded.")
    if len(photo) > MAX_UPLOAD_BYTES:
        raise BadPhoto("The photo is too big. Please use one under 10 MB.")

    try:
        image = Image.open(io.BytesIO(photo))
        image.load()
    except Image.DecompressionBombError:
        raise BadPhoto("That photo is too large to process. Please use a normal phone photo.")
    except (UnidentifiedImageError, OSError):
        raise BadPhoto("That file is not a photo. Please upload a JPG or PNG.")

    if image.format not in ALLOWED_FORMATS:
        raise BadPhoto("Please upload a JPG, PNG or HEIC photo.")

    # Turn the photo the right way up first, because the rotation info is
    # stored in the metadata we are about to throw away.
    image = ImageOps.exif_transpose(image)
    image = image.convert("RGB")
    image.thumbnail((MAX_SIDE, MAX_SIDE))

    # Copying only the pixels into a brand new image leaves all metadata
    # (GPS location, camera model, date taken) behind.
    clean = Image.new("RGB", image.size)
    clean.paste(image)

    out = io.BytesIO()
    clean.save(out, format="JPEG", quality=85)
    return out.getvalue()
