import json
import os
import pytest
from retro.flask import app as retro_app


@pytest.fixture
def client():
    retro_app.app.config["TESTING"] = True
    _client = retro_app.app.test_client()

    yield _client


def test_healthcheck(client):
    rv = client.get('/api/v1/healthcheck')
    assert 200 == rv.status_code
    assert b'Success' in rv.data


def test_create_node(client):
    board_id = _create_simple_board(client)
    get_board_response = _get_board(client, board_id)
    assert get_board_response


def test_edit_node(client):
    edit_data = {"operations": [{"operation": "SET", "field": "foo", "value": "bar"}]}

    # Create board
    board_id = _create_board(client).get("id")
    create_column_response = _create_node(client, board_id, board_id)
    column_id = create_column_response.get("id")
    create_node_response = _create_node(client, board_id, column_id)
    node_id = create_node_response.get("id")

    # Edit the node
    _edit_node(client, board_id, node_id, edit_data)

    # Retrieve the node and ensure expected content is present
    get_node_response = _get_node(client, board_id, node_id)
    assert "bar" == get_node_response.get("content").get("foo")


def test_import_board(client):
    # NOTE: I don't like this test, but wanted to at least get some API level import coverage. We should consider
    # augmenting this possibly after we finalize our decision on how to deal with column ordering. - JL
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/import_board.json")
    with open(data_path) as f:
        import_board_json = json.load(f)

    board_id = "e8fad57d-e2fd-4145-9586-21b404117dcc"
    _import_board(client, import_board_json, copy=False, force=True)
    board_nodes = _get_board(client, board_id).get("nodes")
    expected_nodes_json = import_board_json.get(board_id)
    expected_nodes = [expected_nodes_json.get("board_node")] + expected_nodes_json.get("child_nodes")

    assert len(expected_nodes) == len(board_nodes)

    expected_node_ids = []
    actual_node_ids = []
    for i, node in enumerate(board_nodes):
        expected_node_ids.append(expected_nodes[i]["id"])
        actual_node_ids.append(node["id"])

    assert sorted(expected_node_ids) == sorted(actual_node_ids)


def _create_simple_board(client):
    create_board_response = _create_board(client)
    board_id = create_board_response.get("id")

    create_column1_response = _create_node(client, board_id, board_id)
    column1_id = create_column1_response.get("id")

    create_column2_response = _create_node(client, board_id, board_id)
    column2_id = create_column2_response.get("id")

    create_column1_node1_response = _create_node(client, board_id, column1_id)
    column1_node1_id = create_column1_node1_response.get("id")
    create_column2_node1_response = _create_node(client, board_id, column2_id)
    column2_node1_id = create_column2_node1_response.get("id")

    _create_node(client, board_id, column1_node1_id)
    _create_node(client, board_id, column2_node1_id)

    return board_id


def _import_board(client, import_board_json, copy=False, force=False):
    route = "/api/v1/boards/import"
    data = {"boards": import_board_json.copy()}
    if copy:
        data["copy"] = "true"
    if force:
        data["force"] = "true"

    rv = client.post(route, json=data)
    assert 200 == rv.status_code

    return rv.json


def _get_board(client, board_id):
    route = "/api/v1/boards/%s" % board_id
    rv = client.get(route)
    assert 200 == rv.status_code

    return rv.json


def _create_node(client, board_id, parent_id):
    route = "/api/v1/boards/%s/nodes" % board_id
    data = {"parent_id": parent_id}

    rv = client.post(route, json=data)
    assert 200 == rv.status_code

    return rv.json


def _create_board(client, name="my test board"):
    route = "/api/v1/boards"
    data = {"name": name}

    rv = client.post(route, json=data)
    assert 200 == rv.status_code

    return rv.json.get("nodes")[0]


def _get_node(client, board_id, node_id):
    route = "/api/v1/boards/%s/nodes/%s" % (board_id, node_id)

    rv = client.get(route)
    assert 200 == rv.status_code

    return rv.json


def _edit_node(client, board_id, node_id, data):
    route = "/api/v1/boards/%s/nodes/%s" % (board_id, node_id)

    rv = client.put(route, json=data)
    assert 200 == rv.status_code

    return rv.json
