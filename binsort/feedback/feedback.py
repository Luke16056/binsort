"""Feedback: saves "Was this right?" answers. The photo itself is never saved.

Interface: report(result: dict, ok: bool) -> None
"""

KEEP_FIELDS = ("name", "material", "condition", "bin")
MAX_FIELD_LENGTH = 100


class Feedback:
    def __init__(self, db):
        self.db = db

    def report(self, result, ok):
        if not isinstance(result, dict):
            raise ValueError("result must be one item's result")
        if not isinstance(ok, bool):
            raise ValueError("ok must be true or false")
        # Only keep the fields needed to improve the rules, nothing personal, and never
        # more than MAX_FIELD_LENGTH characters each (the page sends these, so they can't be trusted).
        slim = {key: None if result.get(key) is None else str(result.get(key))[:MAX_FIELD_LENGTH]
                for key in KEEP_FIELDS}
        self.db.save_feedback(slim, ok)
