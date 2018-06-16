from pprint import pprint
import requests
import unittest
from backend.retro.utils.config import Config


class TestRetroApi(unittest.TestCase):
    def setUp(self):
        self.cfg = Config()
        self.base_url = "http://%s:%s" % (self.cfg.retro_api_host, self.cfg.retro_api_port)
        self.import_board_json = {
            "e8fad57d-e2fd-4145-9586-21b404117dcc": {
                "board_node": {
                    "type": "Board",
                    "id": "e8fad57d-e2fd-4145-9586-21b404117dcc",
                    "content": {
                        "name": "test"
                    },
                    "version": 12,
                    "orig_version": 2,
                    "children": ["e8fad57d-e2fd-4145-9586-21b404117dcc|a600a5ef-1d32-458f-80af-6f0b7ccdce39", "e8fad57d-e2fd-4145-9586-21b404117dcc|12a7114d-b7fe-4832-bbfb-f84bde2a9c84", "e8fad57d-e2fd-4145-9586-21b404117dcc|cb86d576-1ee9-427e-bcee-4d90c46c9189", "e8fad57d-e2fd-4145-9586-21b404117dcc|6b6958df-6c1b-49e5-804b-c3547e935579"]
                },
                "child_nodes": [{
                    "type": "ColumnHeader",
                    "id": "e8fad57d-e2fd-4145-9586-21b404117dcc|a600a5ef-1d32-458f-80af-6f0b7ccdce39",
                    "content": {
                        "name": "Is Not"
                    },
                    "version": 6,
                    "orig_version": 5,
                    "parent": "e8fad57d-e2fd-4145-9586-21b404117dcc",
                    "child": "e8fad57d-e2fd-4145-9586-21b404117dcc|ecec8fb0-8984-4ac3-8e2b-c9680c1a119c"
                }, {
                    "type": "Content",
                    "id": "e8fad57d-e2fd-4145-9586-21b404117dcc|ecec8fb0-8984-4ac3-8e2b-c9680c1a119c",
                    "content": {
                        "text": "Bad stuff"
                    },
                    "version": 7,
                    "orig_version": 6,
                    "parent": "e8fad57d-e2fd-4145-9586-21b404117dcc|a600a5ef-1d32-458f-80af-6f0b7ccdce39",
                    "child": "e8fad57d-e2fd-4145-9586-21b404117dcc|eb0ae90f-82e2-41cb-9a68-8e4ae532a801",
                    "column_header": "e8fad57d-e2fd-4145-9586-21b404117dcc|a600a5ef-1d32-458f-80af-6f0b7ccdce39"
                }, {
                    "type": "Content",
                    "id": "e8fad57d-e2fd-4145-9586-21b404117dcc|eb0ae90f-82e2-41cb-9a68-8e4ae532a801",
                    "content": {
                        "text": "Other bad stuff"
                    },
                    "version": 8,
                    "orig_version": 7,
                    "parent": "e8fad57d-e2fd-4145-9586-21b404117dcc|ecec8fb0-8984-4ac3-8e2b-c9680c1a119c",
                    "child": "e8fad57d-e2fd-4145-9586-21b404117dcc|08f2a6a4-00df-423d-bded-223581bfd40f",
                    "column_header": "e8fad57d-e2fd-4145-9586-21b404117dcc|a600a5ef-1d32-458f-80af-6f0b7ccdce39"
                }, {
                    "type": "Content",
                    "id": "e8fad57d-e2fd-4145-9586-21b404117dcc|08f2a6a4-00df-423d-bded-223581bfd40f",
                    "content": {
                        "text": "More bad stuff"
                    },
                    "version": 8,
                    "orig_version": 8,
                    "parent": "e8fad57d-e2fd-4145-9586-21b404117dcc|eb0ae90f-82e2-41cb-9a68-8e4ae532a801",
                    "child": None,
                    "column_header": "e8fad57d-e2fd-4145-9586-21b404117dcc|a600a5ef-1d32-458f-80af-6f0b7ccdce39"
                }, {
                    "type": "ColumnHeader",
                    "id": "e8fad57d-e2fd-4145-9586-21b404117dcc|12a7114d-b7fe-4832-bbfb-f84bde2a9c84",
                    "content": {
                        "name": "Does"
                    },
                    "version": 10,
                    "orig_version": 9,
                    "parent": "e8fad57d-e2fd-4145-9586-21b404117dcc",
                    "child": "e8fad57d-e2fd-4145-9586-21b404117dcc|821ecd19-8667-4894-a2fc-fb0943157080"
                }, {
                    "type": "Content",
                    "id": "e8fad57d-e2fd-4145-9586-21b404117dcc|821ecd19-8667-4894-a2fc-fb0943157080",
                    "content": {
                        "text": "Did some great work"
                    },
                    "version": 11,
                    "orig_version": 10,
                    "parent": "e8fad57d-e2fd-4145-9586-21b404117dcc|12a7114d-b7fe-4832-bbfb-f84bde2a9c84",
                    "child": "e8fad57d-e2fd-4145-9586-21b404117dcc|9dd0da4f-f7e5-4d5c-9cdf-7aa8ec014a12",
                    "column_header": "e8fad57d-e2fd-4145-9586-21b404117dcc|12a7114d-b7fe-4832-bbfb-f84bde2a9c84"
                }, {
                    "type": "Content",
                    "id": "e8fad57d-e2fd-4145-9586-21b404117dcc|9dd0da4f-f7e5-4d5c-9cdf-7aa8ec014a12",
                    "content": {
                        "text": "Did the best work",
                        "votes": 3
                    },
                    "version": 11,
                    "orig_version": 11,
                    "parent": "e8fad57d-e2fd-4145-9586-21b404117dcc|821ecd19-8667-4894-a2fc-fb0943157080",
                    "child": None,
                    "column_header": "e8fad57d-e2fd-4145-9586-21b404117dcc|12a7114d-b7fe-4832-bbfb-f84bde2a9c84"
                }, {
                    "type": "ColumnHeader",
                    "id": "e8fad57d-e2fd-4145-9586-21b404117dcc|cb86d576-1ee9-427e-bcee-4d90c46c9189",
                    "content": {
                        "name": "Does Not"
                    },
                    "version": 12,
                    "orig_version": 12,
                    "parent": "e8fad57d-e2fd-4145-9586-21b404117dcc",
                    "child": None
                }, {
                    "type": "ColumnHeader",
                    "id": "e8fad57d-e2fd-4145-9586-21b404117dcc|6b6958df-6c1b-49e5-804b-c3547e935579",
                    "content": {
                        "name": "Is"
                    },
                    "version": 3,
                    "orig_version": 2,
                    "parent": "e8fad57d-e2fd-4145-9586-21b404117dcc",
                    "child": "e8fad57d-e2fd-4145-9586-21b404117dcc|46884492-d2aa-4013-94a9-a2901aeb406c"
                }, {
                    "type": "Content",
                    "id": "e8fad57d-e2fd-4145-9586-21b404117dcc|46884492-d2aa-4013-94a9-a2901aeb406c",
                    "content": {
                        "text": "Good stuff",
                        "votes": 1
                    },
                    "version": 4,
                    "orig_version": 3,
                    "parent": "e8fad57d-e2fd-4145-9586-21b404117dcc|6b6958df-6c1b-49e5-804b-c3547e935579",
                    "child": "e8fad57d-e2fd-4145-9586-21b404117dcc|b583c4db-0b8e-47ed-8628-9c62af959fef",
                    "column_header": "e8fad57d-e2fd-4145-9586-21b404117dcc|6b6958df-6c1b-49e5-804b-c3547e935579"
                }, {
                    "type": "Content",
                    "id": "e8fad57d-e2fd-4145-9586-21b404117dcc|b583c4db-0b8e-47ed-8628-9c62af959fef",
                    "content": {
                        "text": "Other good stuff"
                    },
                    "version": 4,
                    "orig_version": 4,
                    "parent": "e8fad57d-e2fd-4145-9586-21b404117dcc|46884492-d2aa-4013-94a9-a2901aeb406c",
                    "child": None,
                    "column_header": "e8fad57d-e2fd-4145-9586-21b404117dcc|6b6958df-6c1b-49e5-804b-c3547e935579"
                }]
            }
        }

    def test_create_node(self):
        board_id = self._create_simple_board()
        get_board_response = self._get_board(board_id)
        pprint(get_board_response)

        return get_board_response

    def test_edit_node(self):
        board_id = self._create_simple_board()
        get_board_response = self._get_board(board_id)
        pprint(get_board_response)

    def test_import_board(self):
        # NOTE: I don't like this test, but wanted to at least get some API level import coverage. We should consider
        # augmenting this possibly after we finalize our decision on how to deal with column ordering. - JL
        board_id = "e8fad57d-e2fd-4145-9586-21b404117dcc"
        self._import_board(self.import_board_json, copy=False, force=True)
        board_nodes = self._get_board(board_id).get("nodes")
        expected_nodes_json = self.import_board_json.get(board_id)
        expected_nodes = [expected_nodes_json.get("board_node")] + expected_nodes_json.get("child_nodes")

        self.assertEqual(len(expected_nodes), len(board_nodes))

        expected_node_ids = []
        actual_node_ids = []
        for i, node in enumerate(board_nodes):
            expected_node_ids.append(expected_nodes[i]["id"])
            actual_node_ids.append(node["id"])

        self.assertListEqual(sorted(expected_node_ids), sorted(actual_node_ids))

    def _create_simple_board(self):
        create_board_response = self._create_board()
        board_id = create_board_response.get("id")

        create_column1_response = self._create_node(board_id, board_id)
        column1_id = create_column1_response.get("id")

        create_column2_response = self._create_node(board_id, board_id)
        column2_id = create_column2_response.get("id")

        create_column1_node1_response = self._create_node(board_id, column1_id)
        column1_node1_id = create_column1_node1_response.get("id")
        create_column2_node1_response = self._create_node(board_id, column2_id)
        column2_node1_id = create_column2_node1_response.get("id")

        self._create_node(board_id, column1_node1_id)
        self._create_node(board_id, column2_node1_id)

        return board_id

    def _get_board(self, board_id):
        route = "/api/v1/boards/%s" % board_id
        req = requests.get(self._build_url(route))
        req.raise_for_status()

        return req.json()

    def _import_board(self, import_board_json, copy=False, force=False):
        route = "/api/v1/boards/import"
        data = {"boards": import_board_json.copy()}
        if copy:
            data["copy"] = "true"
        if force:
            data["force"] = "true"

        req = requests.post(self._build_url(route), json=data)
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

        return response.get("nodes")[0]

    def _build_url(self, route):
        return "%s%s" % (self.base_url, route)

    def _do_post(self, route, **kwargs):
        req = requests.post(self._build_url(route), **kwargs)
        req.raise_for_status()
        return req.json()
