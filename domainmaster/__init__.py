from domainmaster.log_manager import logger
from domainmaster.config import load_config
from domainmaster.domain_master import DomainMaster
from typing import Dict
from flask import Flask, g


def main():
    app = Flask(__name__)

    config = load_config()

    try:
        with app.app_context():
            if "master" not in g:
                g.master = get_domain_master(config)
            from domainmaster.routes import home

            app.register_blueprint(home.bp)

    except Exception:
        logger.exception("could not get zone links")

    return app


def get_domain_master(config: Dict[str, str]) -> DomainMaster:
    username = config["icann.account.username"]
    password = config["icann.account.password"]
    authen_base_url = config["authentication.base.url"]
    czds_base_url = config["czds.base.url"]
    working_directory = config.get("working.directory", ".")

    return DomainMaster(
        credentials={"username": username, "password": password, "authen_base_url": authen_base_url},
        czds_base_url=czds_base_url,
        working_directory=working_directory,
    )


app = main()
