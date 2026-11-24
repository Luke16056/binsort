from binsort.bin_rules import NOT_SURE, BinRules
from binsort.item_detector import MATERIALS, make_item


def test_every_ai_material_has_a_rule(db):
    materials_with_rules = {rule["material"] for rule in db.all_rules()}
    assert set(MATERIALS) - {"unknown"} <= materials_with_rules


def test_clean_bottle_goes_in_recycling(db):
    assert BinRules(db).bin_for(make_item("Fanta bottle", "plastic_bottle", "clean", 0.9))["bin"] == "Recycling"


def test_dirty_pot_goes_in_general_waste(db):
    assert BinRules(db).bin_for(make_item("Yoghurt pot", "plastic_tub", "dirty", 0.9))["bin"] == "General waste"


def test_unknown_condition_gives_both_answers(db):
    result = BinRules(db).bin_for(make_item("Yoghurt pot", "plastic_tub", "unknown", 0.9))
    assert result["bin"] == "Depends"
    assert (result["if_clean"], result["if_dirty"]) == ("Recycling", "General waste")


def test_glass_goes_to_bottle_bank_either_way(db):
    assert BinRules(db).bin_for(make_item("Wine bottle", "glass_bottle", "dirty", 0.9))["bin"] == "Bottle bank"


def test_low_confidence_is_not_sure(db):
    assert BinRules(db).bin_for(make_item("Bottle?", "plastic_bottle", "clean", 0.4))["bin"] == NOT_SURE


def test_unknown_material_is_not_sure(db):
    assert BinRules(db).bin_for(make_item("Thing", "unknown", "clean", 0.99))["bin"] == NOT_SURE


def test_typed_text_matches_longest_keyword(db):
    item = BinRules(db).find_by_text("greasy pizza box")
    assert item.material == "cardboard"


def test_typed_text_with_no_match_is_unknown(db):
    assert BinRules(db).find_by_text("mystery object").material == "unknown"


def test_typed_keyword_must_be_a_whole_word(db):
    rules = BinRules(db)
    assert rules.find_by_text("scan").material == "unknown"  # not "can"
    assert rules.find_by_text("beer can").material == "drinks_can"
    assert rules.find_by_text("two empty beer cans").material == "drinks_can"  # plurals still match


def test_csv_edits_reach_an_existing_database(tmp_path):
    from binsort.database import Database
    db = Database(tmp_path / "old.db")
    db.save_feedback({"name": "Can"}, True)
    with db._connect() as conn:
        conn.execute("UPDATE rules SET if_clean = 'Wrong bin' WHERE material = 'drinks_can'")

    db = Database(tmp_path / "old.db")  # app restarts
    assert db.get_rule("drinks_can")["if_clean"] == "Recycling"  # reloaded from the CSV
    assert len(db.all_feedback()) == 1  # feedback is kept
