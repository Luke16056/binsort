"""Item Detector interface. Everything else in BinSort only knows about this file.

Interface:
    detect(photo: bytes) -> list[DetectedItem]
    describe(text: str)  -> list[DetectedItem]
Both raise AIUnavailable if the AI cannot give a usable answer.
"""
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass

# The AI may only answer with one of these materials. Anything else becomes
# "unknown". This is the prompt-injection mitigation from the D1 risk register:
# text written on an item in the photo cannot make the AI invent a new bin.
MATERIALS = [
    "plastic_bottle", "drinks_can", "food_tin", "plastic_tub", "soft_plastic",
    "paper", "cardboard", "carton", "foil", "glass_bottle", "glass_jar",
    "food_waste", "coffee_cup", "polystyrene", "napkin_tissue", "nappy",
    "battery", "small_electrical", "unknown",
]
CONDITIONS = ["clean", "dirty", "unknown"]


class AIUnavailable(Exception):
    """The AI timed out, errored, or gave an answer BinSort could not use."""


@dataclass
class DetectedItem:
    name: str
    material: str
    condition: str = "unknown"
    confidence: float = 1.0

    def to_dict(self):
        return asdict(self)


def make_item(name, material, condition="unknown", confidence=1.0):
    """Build a DetectedItem, forcing anything unexpected into a safe value."""
    name = str(name or "Unknown item").strip()[:60] or "Unknown item"
    material = str(material or "").strip().lower()
    if material not in MATERIALS:
        material = "unknown"
    condition = str(condition or "").strip().lower()
    if condition not in CONDITIONS:
        condition = "unknown"
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))
    return DetectedItem(name, material, condition, confidence)


class ItemDetector(ABC):
    @abstractmethod
    def detect(self, photo: bytes) -> list:
        """Find every item in a (prepared) photo."""

    @abstractmethod
    def describe(self, text: str) -> list:
        """Turn a typed description such as 'dirty yoghurt pot' into items."""
