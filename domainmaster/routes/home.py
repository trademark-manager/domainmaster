from flask import jsonify, Blueprint, g, request


bp = Blueprint("home", __name__)
master = g.master


@bp.route("/")
def home():
    return jsonify(msg="DomainMaster Ready"), 200


@bp.route("/zones")
def get_zones():
    domains = request.args.get("domains", None)
    filters = request.args.get("filters", None)
    downloaded_zones = master.get_zones_from_domains(master, domains, filters)
    master.download_zones(downloaded_zones, master.working_directory)
