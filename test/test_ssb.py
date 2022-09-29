#!/usr/bin/env python3

import unittest
import os

from lib.ssb_liga.ssbliga import SsbLiga

class TestSsb(unittest.TestCase):

    def setUp(self):
        self.adif1 = 'test/fixtures/adif_ssb.adif'

    def test_scores(self):
        act1 = SsbLiga(adif_file=self.adif1)
        act1.meta['district_code'] = 'BAA'
        act1.pre_process()

        expected = 'DST BAE PRI BAE'.split(' ')

        self.assertEqual(len(expected), len(act1.qsos), 'Expected number of QSOs')
        for (i, j) in zip(act1.qsos, expected):
            self.assertEqual(i.srx_string, j, 'QSO district code parsed successfully.')
