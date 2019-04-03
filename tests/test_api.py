# -*- coding: utf-8 -*-
from gitscribe import app

from . import TestCase, patch


class TestAPI(TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    @patch("gitscribe.release_published")
    @patch("gitscribe.settings")
    @patch("gitscribe.validate_signature")
    def test_webhook(self, mock_validate, mock_settings, mock_release):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 405)

        mock_settings.IS_CONFIGURED = False
        res = self.client.post('/')
        self.assertEqual(res.status_code, 500)

        mock_settings.IS_CONFIGURED = True
        mock_validate.side_effect = ValueError("bad digest")
        res = self.client.post('/')
        self.assertEqual(res.status_code, 403)

        mock_validate.side_effect = None
        res = self.client.post('/')
        self.assertEqual(res.status_code, 400)

        request_headers = {
            "X-GitHub-Delivery": "delivery-id",
            "X-GitHub-Event": "some-event"
        }
        request_body = {
            "release": "some-release",
            "repository": "some-repo"
        }
        res = self.client.post('/', headers=request_headers, json=request_body)
        self.assertEqual(res.status_code, 200)
        mock_release.assert_not_called()

        request_headers["X-GitHub-Event"] = "release"
        res = self.client.post('/', headers=request_headers, json=request_body)
        self.assertEqual(res.status_code, 200)
        mock_release.assert_called_with("some-release", "some-repo")

