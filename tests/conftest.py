import io

import pytest
from PIL import Image

from binsort.database import Database


def make_photo(size=(200, 150), fmt="JPEG", gps=False):
    """Make a small test photo in memory, optionally with GPS location in its metadata."""
    image = Image.new("RGB", size, (120, 160, 90))
    out = io.BytesIO()
    if gps:
        exif = Image.Exif()
        exif[0x8825] = {1: "N", 2: (51.0, 53.0, 41.0), 3: "W", 4: (8.0, 28.0, 30.0)}  # Cork
        exif[0x0110] = "Test Phone"  # camera model
        image.save(out, format=fmt, exif=exif)
    else:
        image.save(out, format=fmt)
    return out.getvalue()


@pytest.fixture
def photo():
    return make_photo()


@pytest.fixture
def db(tmp_path):
    return Database(tmp_path / "test.db")
