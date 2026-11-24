"""Bin Rules: plain code (no AI) that gives the Irish bin for an item.

Interface: bin_for(item: DetectedItem) -> dict
"""
import re

from binsort.item_detector import make_item

NOT_SURE = "Not sure"
MIN_CONFIDENCE = 0.6  # below this the AI's guess is not shown as an answer


class BinRules:
    def __init__(self, db):
        self.db = db

    def bin_for(self, item):
        result = {
            "name": item.name,
            "material": item.material,
            "condition": item.condition,
            "confidence": item.confidence,
            "bin": NOT_SURE,
            "if_clean": None,
            "if_dirty": None,
            "tip": "BinSort is not sure what this is. Type what it is and try again.",
        }
        rule = self.db.get_rule(item.material)
        if rule is None or item.confidence < MIN_CONFIDENCE:
            return result

        result["tip"] = rule["tip"]
        if rule["if_clean"] == rule["if_dirty"]:
            result["bin"] = rule["if_clean"]
        elif item.condition == "clean":
            result["bin"] = rule["if_clean"]
        elif item.condition == "dirty":
            result["bin"] = rule["if_dirty"]
        else:
            # The main thing BinSort adds: say what to do either way.
            result["bin"] = "Depends"
            result["if_clean"] = rule["if_clean"]
            result["if_dirty"] = rule["if_dirty"]
        return result

    def find_by_text(self, text):
        """Backup used when the AI is down: match typed words against each rule's keywords."""
        words = text.lower()
        condition = "dirty" if "dirty" in words else "clean" if "clean" in words else "unknown"
        best, best_len = None, 0
        for rule in self.db.all_rules():
            for keyword in rule["keywords"].split(";"):
                keyword = keyword.strip().lower()
                # Whole words only ("can" must not match "scan"); a plural s/es still counts.
                if keyword and re.search(rf"\b{re.escape(keyword)}(e?s)?\b", words) and len(keyword) > best_len:
                    best, best_len = rule["material"], len(keyword)
        return make_item(text, best or "unknown", condition, 1.0 if best else 0.0)
