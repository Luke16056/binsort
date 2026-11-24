"""Picks which AI BinSort uses. This is the ONE place to change to swap the fake AI for the real one.

BINSORT_AI=fake    -> FakeDetector (default)
BINSORT_AI=gemini  -> GeminiDetector (needs GEMINI_API_KEY)
BINSORT_AI=down    -> FakeDetector that always fails, to demo the "AI is down" fallback
"""
import os

from .base import MATERIALS, AIUnavailable, DetectedItem, ItemDetector, make_item
from .fake import FakeDetector
from .gemini import GeminiDetector


def get_detector():
    choice = os.environ.get("BINSORT_AI", "fake").lower()
    if choice == "gemini":
        return GeminiDetector(os.environ.get("GEMINI_API_KEY"), os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite"))
    if choice == "down":
        return FakeDetector(fail=True)
    return FakeDetector()


__all__ = ["AIUnavailable", "DetectedItem", "FakeDetector", "GeminiDetector",
           "ItemDetector", "MATERIALS", "get_detector", "make_item"]
