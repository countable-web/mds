import json
from ..constants import *


def test_get_mines_no_auth(test_client_with_data):
    get_resp = test_client_with_data.get('/mines', headers={})
    assert get_resp.status_code == 401


def test_get_mines_view_only(test_client_with_data, auth_headers):
    get_resp = test_client_with_data.get('/mines', headers=auth_headers['view_only_auth_header'])
    assert get_resp.status_code == 200


def test_get_mines_full_auth(test_client_with_data, auth_headers):
    get_resp = test_client_with_data.get('/mines', headers=auth_headers['full_auth_header'])
    assert get_resp.status_code == 200


def test_get_mines(test_client_with_data, auth_headers):
    get_resp = test_client_with_data.get('/mines', headers=auth_headers['full_auth_header'])
    get_data = json.loads(get_resp.data.decode())
    assert get_resp.status_code == 200
    assert get_data['mines'][0]['guid'] == TEST_MINE_GUID