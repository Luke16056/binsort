"""Fake AI used for tests, for the D2 demo, and when no API key is set up.

It returns realistic answers through exactly the same interface as the real one.
"""
from .base import AIUnavailable, ItemDetector, make_item

# What the fake "sees" in any photo: a typical kitchen-counter pile.
SAMPLE_PILE = [
    make_item("Fanta bottle", "plastic_bottle", "clean", 0.94),
    make_item("Yoghurt pot", "plastic_tub", "unknown", 0.88),
    make_item("Pizza box", "cardboard", "dirty", 0.81),
    make_item("Banana peel", "food_waste", "unknown", 0.97),
    make_item("Takeaway coffee cup", "coffee_cup", "unknown", 0.76),
    make_item("Something shiny", "unknown", "unknown", 0.35),
]

# Very small word list so typed items also work with the fake.
TYPED_WORDS = {
    "bottle": "plastic_bottle", "can": "drinks_can", "tin": "food_tin",
    "yoghurt": "plastic_tub", "yogurt": "plastic_tub", "wrapper": "soft_plastic",
    "bag": "soft_plastic", "paper": "paper", "box": "cardboard", "carton": "carton",
    "foil": "foil", "jar": "glass_jar", "banana": "food_waste", "peel": "food_waste",
    "cup": "coffee_cup", "battery": "battery",
}


class FakeDetector(ItemDetector):
    def __init__(self, items=None, fail=False):
        self.items = list(SAMPLE_PILE if items is None else items)
        self.fail = fail

    def detect(self, photo):
        if self.fail:
            raise AIUnavailable("The AI service is switched off (fake failure).")
        return list(self.items)

    def describe(self, text):
        if self.fail:
            raise AIUnavailable("The AI service is switched off (fake failure).")
        words = text.lower()
        condition = "dirty" if "dirty" in words else "clean" if "clean" in words else "unknown"
        for word, material in TYPED_WORDS.items():
            if word in words:
                return [make_item(text, material, condition, 0.9)]
        return [make_item(text, "unknown", condition, 0.3)]
