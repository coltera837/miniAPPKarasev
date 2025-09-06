import pytest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from main import Window
from datetime import date


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_validate_phone_number(qapp):
    """Тест валидации номеров телефона"""
    client = Window()

    assert client.check_input_number() == False

    client.number.setText("89807060972")
    assert client.check_input_number() == True

    client.number.setText("+79807060972")
    assert client.check_input_number() == True

    client.number.setText("1234567890")
    assert client.check_input_number() == False

    client.number.setText("+79807")
    assert client.check_input_number() == False


@patch('main.requests.post')
def test_add_phone_number_success(mock_post, qapp):
    """Тест успешного добавления номера"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1,
        "number": "+79807060972",
        "currentDate": str(date.today()),
        "currentTime": "12:00:00",
        "clickOrder": 1
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    client = Window()
    client.number.setText("89807060972")

    with patch.object(client, 'check_input_number', return_value=True):
        with patch.object(client, 'get_response') as mock_get:
            client.add_phone_number()

            mock_post.assert_called_once()
            call_args = mock_post.call_args[1]['json']
            assert 'data' in call_args
            assert call_args['data']['number'] == '89807060972'
            assert 'currentDate' in call_args['data']
            assert 'currentTime' in call_args['data']


@patch('main.requests.get')
def test_get_response_success(mock_get, qapp):
    """Тест успешного получения записей"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "records": [
            {
                "id": 1,
                "number": "+79807060972",
                "currentDate": "2025-08-27",
                "currentTime": "12:00:00",
                "clickOrder": 1
            }
        ],
        "total": 1,
        "skip": 0,
        "limit": 10,
        "total_pages": 1,
        "current_page": 1
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    client = Window()

    with patch.object(client.model, 'clear'):
        with patch.object(client.model, 'appendRow'):
            client.get_response()

            mock_get.assert_called_once_with(
                'http://127.0.0.1:8000/NumberList',
                params={'skip': 0, 'limit': 10}
            )


@patch('main.requests.post')
def test_add_phone_number_validation_error(mock_post, qapp):
    """Тест обработки ошибки валидации"""
    mock_response = Mock()
    mock_response.status_code = 422
    mock_response.text = 'Validation error'
    mock_response.raise_for_status.side_effect = Exception("422 Error")
    mock_post.return_value = mock_response

    client = Window()
    client.number.setText("89807060972")

    with patch.object(client, 'check_input_number', return_value=True):
        with patch.object(client.status_label, 'setText') as mock_status:
            client.add_phone_number()

            mock_status.assert_called()
            assert any("422" in str(call) for call in mock_status.call_args_list)


@patch('main.requests.get')
def test_get_response_pagination(mock_get, qapp):
    """Тест пагинации при получении записей"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "records": [],
        "total": 15,
        "skip": 10,
        "limit": 5,
        "total_pages": 3,
        "current_page": 3
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    client = Window()
    client.current_skip = 10
    client.current_limit = 5

    with patch.object(client.model, 'clear'):
        with patch.object(client.model, 'appendRow'):
            client.get_response()

            mock_get.assert_called_once_with(
                'http://127.0.0.1:8000/NumberList',
                params={'skip': 10, 'limit': 5}
            )