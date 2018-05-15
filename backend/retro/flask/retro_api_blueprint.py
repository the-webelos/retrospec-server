import json
import logging
from flask import Blueprint, make_response, request
from .blueprint_helpers import make_response_json

_logger = logging.getLogger(__name__)


def build_blueprint(board_engine):
    blueprint = Blueprint('retro_api', __name__)

    @blueprint.errorhandler(Exception)
    def _unhandled_exception(_ex):
        _logger.exception("Unhandled exception from retro API request.")
        return "Unhandled exception. Check logs for details", 500

    @blueprint.route("/api/v1/healthcheck", methods=["GET"])
    def healthcheck():
        return make_response("Success", 200)

    @blueprint.route("/api/v1/boards", methods=["GET"])
    def get_all_boards():
        boards = board_engine.get_boards()

        return make_response_json({"boards": [node.to_dict() for node in boards]})

    @blueprint.route("/api/v1/boards/<board_id>", methods=["GET"])
    def get_board(board_id):
        board_nodes = board_engine.get_board(board_id)

        return make_response_json({"nodes": [node.to_dict() for node in board_nodes.values()]})

    @blueprint.route("/api/v1/boards", methods=["POST"])
    def create_board():
        args = request.json or {}
        name = args.get("name")
        if not name:
            return make_response("No board name provided!", 400)

        board_node = board_engine.create_board(name)

        return make_response_json(board_node.to_dict())

    @blueprint.route("/api/v1/boards/<board_id>", methods=["PUT"])
    def update_board(board_id):
        return _update_node(board_id, board_id, request.json or {})

    @blueprint.route("/api/v1/boards/<board_id>", methods=["DELETE"])
    def delete_board(board_id):
        # status code is ok
        pass

    @blueprint.route("/api/v1/boards/<board_id>/nodes", methods=["POST"])
    def create_node(board_id):
        args = request.json or {}

        parent_id = args.get("parent_id")
        content = args.get("content", {})

        if not parent_id:
            return make_response("No parent_id provided in request!", 400)

        node = board_engine.add_node(board_id, parent_id, content)

        return make_response_json(node.to_dict())

    @blueprint.route("/api/v1/boards/<board_id>/nodes/<node_id>", methods=["PUT"])
    def update_node(board_id, node_id):
        return _update_node(board_id, node_id, request.json or {})

    def _update_node(board_id, node_id, args):
        valid_args = ["parent_id", "field", "value", "op"]

        parent_id = args.get("parent_id")
        field = args.get("field")
        value = args.get("value")
        op = args.get("operation", "SET")

        if parent_id:
            node = board_engine.move_node(board_id, node_id, parent_id)
        elif field:
            node = board_engine.edit_node(board_id, node_id, field, value, op)
        else:
            return make_response("No valid arguments provided. Must send at least one of [%s]" % valid_args, 400)

        return make_response_json(node.to_dict())

    @blueprint.route("/api/v1/boards/<board_id>/nodes/<node_id>", methods=["DELETE"])
    def delete_node(board_id, node_id):
        node = board_engine.remove_node(board_id, node_id)

        return make_response_json(node.to_dict())

    return blueprint
