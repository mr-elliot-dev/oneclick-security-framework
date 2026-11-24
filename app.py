from flask import Flask
from core.config import load_config
from core.database import Database
from core.logging_config import setup_logging
from modules.click_simulator import ClickSimulator
from web.routes import init_routes

def create_app(config_path="config.yaml"):
    cfg=load_config(config_path); setup_logging(cfg["log_file"])
    db=Database(cfg["database"]); simulator=ClickSimulator(db,cfg["lab_base_url"])
    app=Flask(__name__); app.config["FRAMEWORK_CONFIG"]=cfg; app.config["DB"]=db; app.config["SIMULATOR"]=simulator
    app.register_blueprint(init_routes(db,simulator))
    return app
if __name__=="__main__":
    app=create_app(); cfg=app.config["FRAMEWORK_CONFIG"]
    app.run(host=cfg["host"],port=cfg["port"],debug=False)
