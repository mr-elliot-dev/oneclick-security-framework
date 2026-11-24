from pathlib import Path
import sqlite3
from contextlib import contextmanager


class Database:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.init()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA foreign_keys=ON")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init(self):
        with self.connect() as c:
            c.executescript('''
            CREATE TABLE IF NOT EXISTS simulations (
              id TEXT PRIMARY KEY, created_at TEXT NOT NULL, label TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'created'
            );
            CREATE TABLE IF NOT EXISTS events (
              id INTEGER PRIMARY KEY AUTOINCREMENT, simulation_id TEXT NOT NULL,
              event_type TEXT NOT NULL, timestamp TEXT NOT NULL, details TEXT NOT NULL,
              FOREIGN KEY(simulation_id) REFERENCES simulations(id)
            );
            CREATE TABLE IF NOT EXISTS network_events (
              id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL,
              method TEXT NOT NULL, url TEXT NOT NULL, status INTEGER, note TEXT NOT NULL
            );
            ''')

    def create_simulation(self, sim_id, label, created):
        with self.connect() as c:
            c.execute("INSERT INTO simulations(id,created_at,label) VALUES(?,?,?)", (sim_id, created, label))

    def event(self, sim_id, event_type, timestamp, details):
        with self.connect() as c:
            c.execute("INSERT INTO events(simulation_id,event_type,timestamp,details) VALUES(?,?,?,?)", (sim_id,event_type,timestamp,details))

    def get_simulation(self, sim_id):
        with self.connect() as c:
            sim = c.execute("SELECT * FROM simulations WHERE id=?", (sim_id,)).fetchone()
            if not sim: return None
            events = c.execute("SELECT * FROM events WHERE simulation_id=? ORDER BY id", (sim_id,)).fetchall()
            return {"simulation": dict(sim), "events": [dict(x) for x in events]}

    def all_simulations(self):
        with self.connect() as c:
            return [dict(x) for x in c.execute("SELECT * FROM simulations ORDER BY created_at DESC").fetchall()]

    def log_network_event(self, timestamp, method, url, status, note):
        with self.connect() as c:
            c.execute("INSERT INTO network_events(timestamp,method,url,status,note) VALUES(?,?,?,?,?)", (timestamp,method,url,status,note))

    def network_events(self):
        with self.connect() as c:
            return [dict(x) for x in c.execute("SELECT * FROM network_events ORDER BY id DESC").fetchall()]
