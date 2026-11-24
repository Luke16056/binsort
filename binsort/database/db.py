"""Data layer. A local SQLite file stands in for the cloud database in the target design.

Only this module runs SQL. Bin Rules and Feedback talk to the data through the
methods on Database, never by writing SQL themselves.
"""
import csv
import json
import sqlite3
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path

RULES_CSV = Path(__file__).with_name("bin_rules.csv")


class Database:
    def __init__(self, path):
        self.path = str(path)
        self._create_tables()

    @contextmanager
    def _connect(self):
        # closing() shuts the file (Windows keeps it locked otherwise); "with conn" commits or rolls back.
        with closing(sqlite3.connect(self.path)) as conn:
            conn.row_factory = sqlite3.Row
            with conn:
                yield conn

    def _create_tables(self):
        with self._connect() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS rules (
                       material TEXT PRIMARY KEY,
                       label TEXT NOT NULL,
                       if_clean TEXT NOT NULL,
                       if_dirty TEXT NOT NULL,
                       keywords TEXT NOT NULL,
                       tip TEXT NOT NULL)"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS feedback (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       created TEXT NOT NULL,
                       result TEXT NOT NULL,
                       ok INTEGER NOT NULL)"""
            )
            # Reload the rules on every start so edits to bin_rules.csv always take effect.
            # Feedback rows are left alone.
            conn.execute("DELETE FROM rules")
            self._load_rules(conn)

    def _load_rules(self, conn):
        with open(RULES_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                conn.execute(
                    "INSERT INTO rules VALUES (:material, :label, :if_clean, :if_dirty, :keywords, :tip)",
                    row,
                )

    # ---- rules ----
    def get_rule(self, material):
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM rules WHERE material = ?", (material,)).fetchone()
        return dict(row) if row else None

    def all_rules(self):
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM rules ORDER BY material").fetchall()
        return [dict(r) for r in rows]

    # ---- feedback ----
    def save_feedback(self, result, ok):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO feedback (created, result, ok) VALUES (?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), json.dumps(result), int(bool(ok))),
            )

    def all_feedback(self):
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM feedback ORDER BY id").fetchall()
        return [{"id": r["id"], "created": r["created"], "result": json.loads(r["result"]), "ok": bool(r["ok"])} for r in rows]
