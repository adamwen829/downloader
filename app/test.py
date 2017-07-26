import unittest

from mock import patch

from app.config import WHITE_LIST, RESOURCE_MAX_SIZE
from app.offline import _is_validated_url, _is_validated_response, download


class ObjectDict(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        return None

    def __setattr__(self, key, value):
        self[key] = value


class TestDownloader(unittest.TestCase):
    @patch('app.offline._download')
    @patch('app.offline._is_validated_url')
    def test_download(self, _is_validated_url, _download):
        _is_validated_url.return_value = False
        download('{"url": "http://fan.xyz/a.jpg"}')
        _download.assert_not_called()

    @patch('app.offline.set_task_fail')
    @patch('app.offline.is_duplicated_task')
    @patch('app.offline.is_blacklisted')
    def test__is_validated_url(self, is_blacklisted, is_duplicated_task, set_task_fail):
        url = 'http://fan.com/a.jpg'
        is_blacklisted.return_value = False
        is_duplicated_task.return_value = True
        self.assertFalse(_is_validated_url(url))
        set_task_fail.assert_not_called()
        is_blacklisted.return_value = True
        is_duplicated_task.return_value = False
        self.assertFalse(_is_validated_url(url))
        set_task_fail.assert_called_with(url)
        is_blacklisted.return_value = True
        is_duplicated_task.return_value = True
        self.assertFalse(_is_validated_url(url))
        is_blacklisted.return_value = False
        is_duplicated_task.return_value = False
        self.assertTrue(_is_validated_url(url))

    @patch('app.offline.set_task_fail')
    @patch('app.offline.set_blacklist_domain')
    def test__is_validated_response(self, set_blacklist_domain, set_task_fail):
        url = 'http://fan.com/a.jpg'
        res = ObjectDict({
            'status_code': 403,
            'headers': {
                'Content-Type': WHITE_LIST[0],
                'Content-Length': RESOURCE_MAX_SIZE
            }
        })
        _is_validated_response(url, res)
        set_blacklist_domain.assert_called_with('fan.com')
        set_task_fail.assert_called_with(url)
        res = ObjectDict({
            'status_code': 200,
            'headers': {
                'Content-Type': WHITE_LIST[0],
                'Content-Length': RESOURCE_MAX_SIZE + 1
            }
        })
        self.assertFalse(_is_validated_response(url, res))
        res = ObjectDict({
            'status_code': 200,
            'headers': {
                'Content-Type': 'fake/jpg',
                'Content-Length': RESOURCE_MAX_SIZE
            }
        })
        self.assertFalse(_is_validated_response(url, res))
        res = ObjectDict({
            'status_code': 200,
            'headers': {
                'Content-Type': WHITE_LIST[0],
                'Content-Length': RESOURCE_MAX_SIZE
            }
        })
        self.assertTrue(_is_validated_response(url, res))


if __name__ == '__main__':
    unittest.main()
