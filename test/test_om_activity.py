#!/usr/bin/env python3

import unittest
import os
from pprint import pprint

from lib.om_activity.omactivity import OmActivity

class TestOMA(unittest.TestCase):

    def setUp(self):
        self.adif1 = 'test/fixtures/adif_omact.adif'

    def test_scores(self):
        act1 = OmActivity(adif_file=self.adif1)
        act1.pre_process()

        expected_exchanges = (
            ('001','011'),
            ('002','200'),
            ('003','223'),
            ('004','1241'),
            ('005','010'),
        )

        self.assertEqual(len(act1.qsos), len(expected_exchanges), 'The log should have 5 QSOs')

        for exch, qso in zip(expected_exchanges, act1.qsos):
            self.assertEqual(
                (exch[0], exch[1]), (qso.stx, qso.srx),
                'QSO analyzed exchanges should match.'
            )
