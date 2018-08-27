import logging

from retro.image.card_reader import CardReader

_logger = logging.getLogger(__name__)


class ImageEngine(object):
    def __init__(self, board_engine):
        self.board_engine = board_engine

    def import_cards(self, board_id: str, parent_id: str, creator: str, image_bytes: str):
        card_reader = CardReader(image_bytes)
        cards = card_reader.get_cards_content()

        nodes = []
        for card in cards:
            nodes.append(self.board_engine.add_node(board_id, parent_id, creator, content=card))

        return nodes
