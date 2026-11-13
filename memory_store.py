import sqlite3
import time

DB = "interview.db"


def _conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS turns(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT, role TEXT, question TEXT, answer TEXT,
            tech_score REAL, feedback TEXT,
            fillers INTEGER, wpm INTEGER, pauses INTEGER, comm_score REAL,
            presence REAL, created REAL)""")


def save_turn(session_id, role, question, answer, tech_score, feedback,
              metrics=None, presence=None):
    m = metrics or {}
    with _conn() as c:
        c.execute("""INSERT INTO turns(session_id, role, question, answer, tech_score,
            feedback, fillers, wpm, pauses, comm_score, presence, created)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (session_id, role, question, answer, tech_score, feedback,
                   m.get("fillers"), m.get("wpm"), m.get("pauses"),
                   m.get("comm_score"), presence, time.time()))


def get_turns(session_id):
    with _conn() as c:
        rows = c.execute("SELECT * FROM turns WHERE session_id=? ORDER BY id",
                         (session_id,)).fetchall()
    return [dict(r) for r in rows]


def get_averages(session_id):
    with _conn() as c:
        r = c.execute("""SELECT AVG(tech_score) tech, AVG(comm_score) comm,
            AVG(presence) presence, AVG(wpm) wpm, SUM(fillers) fillers,
            COUNT(*) answers FROM turns WHERE session_id=?""", (session_id,)).fetchone()
    return {k: (round(v, 1) if isinstance(v, float) else v) for k, v in dict(r).items()}
