""""""
import requests
from unittest.mock import patch
from app.views import get_table_link
#
#
# class TestDuplicateVideo:
#     @patch('app.views.get_table_link', return_value={'table': 'test'})
#     def test_post_201_created(self, mock_get_table_link):
#         response = requests.get('http://localhost:5000/video-duplicate/processing', data={'id': 'test'})
#
#         mock_get_table_link.assert_called_once()
#         assert response.json() == {'table': 'test'}


class TestClass:
    @patch('app.views.get_table_link', return_value='test')
    def test_func(self, mock):
        assert get_table_link() == 'test'
