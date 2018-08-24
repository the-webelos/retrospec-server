import logging
from flask import Blueprint, request
from .blueprint_helpers import make_response_json

_logger = logging.getLogger(__name__)


def build_blueprint(group_engine):
    blueprint = Blueprint('group_api', __name__)

    @blueprint.errorhandler(Exception)
    def _unhandled_exception(_ex):
        _logger.exception("Unhandled exception from groups API request.")
        return "Unhandled exception. Check logs for details", 500

    @blueprint.route("/api/v1/groups", methods=["GET"])
    def get_all_groups():
        groups = group_engine.get_groups()
        return make_response_json({"groups": [g.to_dict() for g in groups]})

    @blueprint.route("/api/v1/groups", methods=["POST"])
    def create_group():
        group = group_engine.create_group(request.get_json()['name'])
        return make_response_json({"group": group.to_dict()})

    @blueprint.route("/api/v1/groups/<group_id>", methods=["GET"])
    def get_group(group_id):
        group = group_engine.get_group(group_id)
        return make_response_json(group.to_dict())

    @blueprint.route("/api/v1/groups/<group_id>", methods=["DELETE"])
    def delete_group(group_id):
        result = group_engine.remove_group(group_id)
        return make_response_json({"success": result})

    @blueprint.route("/api/v1/groups/<group_id>", methods=["PUT"])
    def update_group(group_id):
        name = None
        if request.is_json:
            name = request.json.get('name')

        if not name:
            name = request.args.get('name')

        if not name:
            raise Exception("Must provide 'name' parameter")

        group = group_engine.update_group(group_id, name)
        return make_response_json(group.to_dict())

    return blueprint
