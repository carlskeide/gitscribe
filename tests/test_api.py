# -*- coding: utf-8 -*-
from gitscribe import app

from . import TestCase, skip


class TestAPI(TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    @skip("Not implemented")
    def test_webhook(self):
        pass
