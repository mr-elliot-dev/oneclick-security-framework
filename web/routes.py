from flask import Blueprint, render_template, request, abort, jsonify
import json
bp=Blueprint("web",__name__)
def init_routes(db, sim):
    @bp.get("/")
    def dashboard(): return render_template("dashboard.html", simulations=db.all_simulations())
    @bp.get("/lab/<sim_id>")
    def lab_landing(sim_id):
        record=db.get_simulation(sim_id)
        if not record: abort(404)
        sim.record(sim_id,"landing_view",{"purpose":"consented training simulation"})
        return render_template("lab_landing.html",sim_id=sim_id)
    @bp.post("/lab/<sim_id>/consent")
    def consent(sim_id):
        if not db.get_simulation(sim_id): abort(404)
        sim.record(sim_id,"consent_click",{"consented":True})
        sim.record(sim_id,"simulation_complete",{"result":"safe simulation stage complete"})
        return jsonify({"message":"Consent recorded. No exploit or payload was executed."})
    return bp
