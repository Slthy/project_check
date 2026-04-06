import pytest
from unittest.mock import MagicMock
from create_instance import instance

@pytest.fixture
def app():
    app = instance()
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "secret"
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_db(mocker):

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mocker.patch('utils.functions.pymysql.connect', return_value=mock_conn)
    
    return mock_cursor