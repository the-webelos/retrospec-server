import logging
import simplejson
from flask import Blueprint, make_response, request
from .blueprint_helpers import make_response_json

_logger = logging.getLogger(__name__)


def build_blueprint(board_engine):
    blueprint = Blueprint('retro_api', __name__)

    @blueprint.errorhandler(Exception)
    def _unhandled_exception(_ex):
        _logger.exception("Unhandled exception from retro API request.")
        return "Unhandled exception. Check logs for details", 500

    @blueprint.route("/api/healthcheck", methods=["GET"])
    def healthcheck():
        return make_response("Success", 200)

    @blueprint.route("/api/boards", methods=["GET"])
    def get_all_boards():
        boards = board_engine.get_all_boards()

        return make_response_json(boards)

    @blueprint.route("/api/boards/<board_id>", methods=["GET"])
    def get_board(board_id):
        board_nodes = board_engine.get_board(board_id)

        return make_response_json({"nodes": [node.to_dict() for node in board_nodes.values()]})

    @blueprint.route("/api/boards/create", methods=["POST"])
    def create_board():
        args = simplejson.loads(request.data)
        name = args.get("name")
        if not name:
            return make_response("No board name provided!", 400)

        board_node = board_engine.create_board(name)

        return make_response_json(board_node.to_dict())

    @blueprint.route("/api/boards/<board_id>/modify", methods=["PUT"])
    def modify_board(board_id):
        pass

    @blueprint.route("/api/boards/<board_id>/delete", methods=["DELETE"])
    def delete_board(board_id):
        pass

    @blueprint.route("/api/boards/<board_id>/nodes/create", methods=["POST"])
    def add_node(board_id):
        args = simplejson.loads(request.data)
        parent_id = args.get("parent_id")
        content = args.get("content", {})

        node = board_engine.add_node(board_id, parent_id, content)

        return make_response_json(node.to_dict())

    @blueprint.route("/api/boards/<board_id>/nodes/<node_id>/move", methods=["PUT"])
    def move_node(board_id, node_id):
        args = simplejson.loads(request.data)
        parent_id = args.get("parent_id")

        node = board_engine.move_node(board_id, node_id, parent_id)

        return make_response_json(node.to_dict())

    @blueprint.route("/api/boards/<board_id>/nodes/<node_id>/update", methods=["PUT"])
    def edit_node(board_id, node_id):
        args = simplejson.loads(request.data)
        content = args.get("content")

        node = board_engine.edit_node(board_id, node_id, content)

        return make_response_json(node.to_dict())

    @blueprint.route("/api/boards/<board_id>/nodes/<node_id>/delete", methods=["DELETE"])
    def delete_node(board_id, node_id):
        node = board_engine.remove_node(board_id, node_id)

        return make_response_json(node.to_dict())

    return blueprint
