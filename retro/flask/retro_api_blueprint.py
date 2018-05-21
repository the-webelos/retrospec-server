import logging
from flask import Blueprint, make_response, request
from retro.chain.operations import OperationFactory
from retro.store.exceptions import NodeLockedError, UnlockFailureError
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
        try:
            start = int(request.args.get("start", 0))
            rows = int(request.args.get("rows", 20))

            boards = board_engine.get_boards(start=start, rows=rows)
            response = make_response_json({"boards": [node.to_dict() for node in boards]})
        except (ValueError, TypeError) as ver:
            _logger.exception(ver)
            response = make_response("Invalid request parameters.", 400)

        return response

    @blueprint.route("/api/v1/boards/<board_id>", methods=["GET"])
    def get_board(board_id):
        board_nodes = board_engine.get_board(board_id)

        return make_response_json({"nodes": [node.to_dict() for node in board_nodes]})

    @blueprint.route("/api/v1/boards", methods=["POST"])
    def create_board():
        args = request.json or {}
        name = args.get("name")
        template = args.get("template")
        if not name:
            return make_response("No board name provided!", 400)

        board_nodes = board_engine.create_board(name, template)

        return make_response_json({"nodes": [node.to_dict() for node in board_nodes]})

    @blueprint.route("/api/v1/boards/<board_id>", methods=["PUT"])
    def update_board(board_id):
        return _update_node(board_id, board_id, request.json or {})

    @blueprint.route("/api/v1/boards/<board_id>", methods=["DELETE"])
    def delete_board(board_id):
        deleted_nodes = board_engine.delete_board(board_id)

        return "Deleted %s nodes" % len(deleted_nodes)

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
        valid_args = ["parent_id", "operations", "lock", "unlock"]

        parent_id = args.get("parent_id")
        operations = args.get("operations")
        lock = args.get("lock")
        unlock = args.get("unlock")

        try:
            if parent_id:
                nodes = board_engine.move_node(board_id, node_id, parent_id)
            elif operations or lock or unlock:
                if lock and unlock:
                    return make_response("Cannot provide lock and unlock in the same request.", 400)
                nodes = [board_engine.edit_node(
                    board_id, node_id,
                    [OperationFactory().build_operation(o.get("operation", "SET"), o.get("field"), o.get("value")) for o in operations],
                    lock, unlock)]
            else:
                return make_response("No valid arguments provided. Must send at least one of [%s]" % valid_args, 400)

            return make_response_json({"nodes": [node.to_dict() for node in nodes]})
        except NodeLockedError as nle:
            _logger.exception(nle)
            return make_response("Cannot edit locked node!", 400)
        except UnlockFailureError as ufe:
            _logger.exception(ufe)
            return make_response("Failed to unlock node '%s'. See logs for details.", node_id, 400)

    @blueprint.route("/api/v1/boards/<board_id>/nodes/<node_id>", methods=["DELETE"])
    def delete_node(board_id, node_id):
        cascade = request.args.get("cascade", "false").lower() == "true"
        nodes = board_engine.remove_node(board_id, node_id, cascade)

        return make_response_json({"deleted": [node.to_dict() for node in nodes]})

    @blueprint.route("/api/v1/templates", methods=["GET"])
    def get_board_templates():
        return make_response_json({"templates": board_engine.get_templates()})

    return blueprint
