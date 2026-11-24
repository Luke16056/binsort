import pytest

from binsort.bin_rules import BinRules
from binsort.item_detector import FakeDetector, make_item
from binsort.photo_prep import BadPhoto, prepare
from binsort.sorting import Sorter


def make_sorter(db, **fake):
    return Sorter(prepare, FakeDetector(**fake), BinRules(db))


def test_photo_is_sorted_end_to_end(db, photo):
    result = make_sorter(db).sort(photo)
    assert len(result["items"]) == 6
    assert result["ai_down"] is False
    assert "AI" in result["message"]  # results are labelled as AI
    assert "Fanta bottle" in result["by_bin"]["Recycling"]


def test_ai_down_does_not_crash(db, photo):
    result = make_sorter(db, fail=True).sort(photo)
    assert result["ai_down"] is True
    assert result["items"] == []
    assert "Type" in result["message"]


def test_photo_with_no_rubbish(db, photo):
    result = make_sorter(db, items=[]).sort(photo)
    assert result["items"] == []
    assert "No rubbish" in result["message"]


def test_poor_ai_answer_shows_not_sure(db, photo):
    result = make_sorter(db, items=[make_item("Blur", "unknown", "unknown", 0.1)]).sort(photo)
    assert result["items"][0]["bin"] == "Not sure"


def test_bad_photo_is_rejected(db):
    with pytest.raises(BadPhoto):
        make_sorter(db).sort(b"not a photo")


def test_typed_item_uses_ai(db):
    result = make_sorter(db).sort_text("clean yoghurt pot")
    assert result["items"][0]["bin"] == "Recycling"


def test_typed_item_still_works_when_ai_is_down(db):
    result = make_sorter(db, fail=True).sort_text("dirty yoghurt pot")
    assert result["items"][0]["bin"] == "General waste"
    assert "not available" in result["message"]


def test_empty_typed_text(db):
    assert make_sorter(db).sort_text("   ")["items"] == []


class NothingFound:
    def describe(self, text):
        return []


def test_typed_text_with_nothing_found_says_so(db):
    result = Sorter(prepare, NothingFound(), BinRules(db)).sort_text("hello")
    assert result["items"] == []
    assert "could not find" in result["message"]
