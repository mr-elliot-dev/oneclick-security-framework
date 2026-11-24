from core.database import Database
from modules.click_simulator import ClickSimulator
def test_create_sim_and_events(tmp_path):
    db=Database(tmp_path/"t.db"); sim=ClickSimulator(db,"http://localhost:5000")
    made=sim.create("pytest")
    assert made["id"] and made["url"].endswith(made["id"])
    sim.record(made["id"],"landing_view",{})
    assert len(db.get_simulation(made["id"])["events"])==2
def test_bad_event(tmp_path):
    db=Database(tmp_path/"t.db"); sim=ClickSimulator(db,"http://localhost")
    made=sim.create()
    try: sim.record(made["id"],"payload_executed")
    except ValueError: pass
    else: assert False
