from pprint import pprint
import requests
import json
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
        route = "/api/boards/%s/nodes/create" % board_id
        data = {"parent_id": board_id}

        req = requests.post(self._get_url(route), data=json.dumps(data))
        req.raise_for_status()
        create_node_response = req.json()

        pprint(create_node_response)

        return create_node_response

    def _create_board(self, name="my test board"):
        route = "/api/boards/create"
        data = {"name": name}

        req = requests.post(self.base_url + route, data=json.dumps(data))
        req.raise_for_status()
        response = req.json()

        return response

    def _get_url(self, route):
        return "%s%s" % (self.base_url, route)
