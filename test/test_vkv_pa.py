#!/usr/bin/env python3

import unittest
import os

from lib.vkv_pa.vhfacthamactivity import VhfActHamActivity

class TestVhfActivity(unittest.TestCase):

    def setUp(self):
        self.adif1 = 'test/fixtures/adif1.adif'

    def test_scores(self):
        act1 = VhfActHamActivity(adif_file=self.adif1)
        act1.meta['gridsquare'] = 'JN88nc'
        act1.calculate_scores()
        self.assertEqual(act1.meta['scores']['multiplier_count'], 5)
        self.assertEqual(act1.meta['scores']['score'], 17)
        self.assertEqual(act1.meta['scores']['score_multiplied'], 85)
