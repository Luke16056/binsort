import pytest

from binsort.feedback import Feedback


def test_feedback_is_saved(db):
    Feedback(db).report({"name": "Fanta bottle", "material": "plastic_bottle", "condition": "clean", "bin": "Recycling"}, True)
    saved = db.all_feedback()
    assert len(saved) == 1
    assert saved[0]["ok"] is True
    assert saved[0]["result"]["bin"] == "Recycling"


def test_only_needed_fields_are_kept(db):
    Feedback(db).report({"name": "Can", "bin": "Recycling", "photo": "abc123", "email": "x@y.ie"}, False)
    saved = db.all_feedback()[0]["result"]
    assert "photo" not in saved and "email" not in saved


def test_bad_feedback_is_rejected(db):
    with pytest.raises(ValueError):
        Feedback(db).report(None, True)


def test_long_fields_are_cut_short(db):
    Feedback(db).report({"name": "x" * 5000, "bin": "Recycling"}, True)
    saved = db.all_feedback()[0]["result"]
    assert len(saved["name"]) == 100
    assert saved["bin"] == "Recycling"
    assert saved["material"] is None  # missing fields stay empty


def test_ok_must_be_true_or_false(db):
    with pytest.raises(ValueError):
        Feedback(db).report({"name": "Can"}, "yes")
