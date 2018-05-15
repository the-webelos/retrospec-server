from pprint import pprint
import requests
import unittest
from retro.utils.config import Config


class TestRetroApi(unittest.TestCase):
    def setUp(self):
        self.cfg = Config()
        self.base_url = "http://%s:%s" % (self.cfg.RetroApiHost, self.cfg.RetroApiPort)

    def test_create_node(self):
        create_board_response = self._create_board()
        pprint(create_board_response)

        board_id = create_board_response.get("id")
        create_column_response = self._create_node(board_id, board_id)
        pprint(create_column_response)

        column_id = create_column_response.get("id")
        create_node_response = self._create_node(board_id, column_id)
        pprint(create_node_response)

        get_board_response = self._get_board(board_id)
        print()
        pprint(get_board_response)

        return get_board_response

    def _get_board(self, board_id):
        route = "/api/v1/boards/%s" % board_id
        req = requests.get(self._build_url(route))
        req.raise_for_status()

        return req.json()

    def _create_node(self, board_id, parent_id):
        route = "/api/v1/boards/%s/nodes" % board_id
        data = {"parent_id": parent_id}

        req = requests.post(self._build_url(route), json=data)
        req.raise_for_status()
        response = req.json()

        return response

    def _create_board(self, name="my test board"):
        route = "/api/v1/boards"
        data = {"name": name}

        req = requests.post(self.base_url + route, json=data)
        req.raise_for_status()
        response = req.json()

        return response

    def _build_url(self, route):
        return "%s%s" % (self.base_url, route)

    def _do_post(self, route, **kwargs):
        req = requests.post(self._build_url(route), **kwargs)
        req.raise_for_status()
        return req.json()
