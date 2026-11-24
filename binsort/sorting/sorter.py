"""Sorting: runs each step in order (prepare photo, find items, apply bin rules).

Interface:
    sort(photo: bytes) -> dict
    sort_text(text: str) -> dict
It only talks to the other components through their interfaces, which are
passed in when the app starts. That is what lets tests pass in a fake AI.
"""
from binsort.item_detector import AIUnavailable

AI_LABEL = "Found by AI. Check before you bin it."


class Sorter:
    def __init__(self, prepare, detector, rules):
        self.prepare = prepare      # photo_prep.prepare
        self.detector = detector    # any ItemDetector
        self.rules = rules          # BinRules

    def sort(self, photo):
        clean_photo = self.prepare(photo)  # raises BadPhoto for bad uploads
        try:
            items = self.detector.detect(clean_photo)
        except AIUnavailable as error:
            return self._result([], ai_down=True,
                                message=f"{error} Type your items in the box instead.")
        if not items:
            return self._result([], message="No rubbish found in that photo. Try a clearer photo or type the item.")
        return self._result([self.rules.bin_for(item) for item in items], message=AI_LABEL)

    def sort_text(self, text):
        text = (text or "").strip()
        if not text:
            return self._result([], message="Type what the item is, e.g. 'dirty yoghurt pot'.")
        try:
            items = self.detector.describe(text)
            message = AI_LABEL
        except AIUnavailable:
            # AI is down: typed items go straight to the bin rules (D1 risk mitigation).
            items = [self.rules.find_by_text(text)]
            message = "The AI is not available, so this answer comes from BinSort's own word list."
        if not items:
            return self._result([], message="BinSort could not find an item in that. Try e.g. 'dirty yoghurt pot'.")
        return self._result([self.rules.bin_for(item) for item in items], message=message)

    @staticmethod
    def _result(items, ai_down=False, message=""):
        by_bin = {}
        for item in items:
            by_bin.setdefault(item["bin"], []).append(item["name"])
        return {"items": items, "by_bin": by_bin, "ai_down": ai_down, "message": message}
