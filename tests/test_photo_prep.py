import io

import pytest
from PIL import Image

from binsort.photo_prep import BadPhoto, prepare
from tests.conftest import make_photo


def test_location_data_is_removed():
    before = make_photo(gps=True)
    assert Image.open(io.BytesIO(before)).getexif().get(0x8825)  # GPS is there to start with

    after = Image.open(io.BytesIO(prepare(before)))
    assert not after.getexif()  # no GPS, no camera model, nothing


def test_big_photo_is_shrunk():
    after = Image.open(io.BytesIO(prepare(make_photo(size=(4000, 3000)))))
    assert max(after.size) == 1024


def test_png_is_accepted():
    after = Image.open(io.BytesIO(prepare(make_photo(fmt="PNG"))))
    assert after.format == "JPEG"


def test_phone_mpo_jpeg_is_accepted():
    buf = io.BytesIO()
    Image.new("RGB", (64, 48)).save(buf, "MPO", save_all=True, append_images=[Image.new("RGB", (64, 48))])
    assert Image.open(io.BytesIO(buf.getvalue())).format == "MPO"
    after = Image.open(io.BytesIO(prepare(buf.getvalue())))
    assert after.format == "JPEG"


def test_text_file_is_rejected():
    with pytest.raises(BadPhoto):
        prepare(b"this is not a photo")


def test_empty_upload_is_rejected():
    with pytest.raises(BadPhoto):
        prepare(b"")


def test_huge_file_is_rejected():
    with pytest.raises(BadPhoto):
        prepare(b"0" * (11 * 1024 * 1024))


def test_decompression_bomb_is_rejected(monkeypatch):
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 100)  # a 200x150 photo is now "too many pixels"
    with pytest.raises(BadPhoto, match="too large"):
        prepare(make_photo())


def test_iphone_heic_is_accepted():
    pytest.importorskip("pillow_heif")
    buf = io.BytesIO()
    Image.new("RGB", (64, 48), (120, 160, 90)).save(buf, "HEIF")
    after = Image.open(io.BytesIO(prepare(buf.getvalue())))
    assert after.format == "JPEG"
