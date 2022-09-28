#!/usr/bin/env python3

import unittest
from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_index(self):
        res_index = self.app.get('/')
        self.assertEqual(res_index.status_code, 200)
