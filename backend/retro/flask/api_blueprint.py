import logging
from flask import Blueprint, make_response
from retro.chain.node_chain import NodeChain

_logger = logging.getLogger(__name__)


def build_blueprint(store):
    blueprint = Blueprint('retro_api', __name__)

    @blueprint.errorhandler(Exception)
    def _unhandled_exception(_ex):
        _logger.exception("Unhandled exception from retro API request.")
        return "Unhandled exception. Check logs for details", 500

    @blueprint.route("/api/healthcheck", methods=["GET"])
    def hello():
        return make_response("Success", 200)

    @blueprint.route("/api/boards/<int:board_id>", methods=["GET"])
    def get_board(board_id):
        pass

    @blueprint.route("/api/boards/add", methods=["POST"])
    def add_board():
        node_chain = NodeChain(store, board_id=None)
        pass

    @blueprint.route("/api/boards/<int:board_id>/modify", methods=["PUT"])
    def edit_board(board_id):
        pass

    @blueprint.route("/api/boards/<int:board_id>/delete", methods=["DELETE"])
    def delete_board(board_id):
        pass

    @blueprint.route("/api/nodes/add", methods=["POST"])
    def add_node():
        pass

    return blueprint
