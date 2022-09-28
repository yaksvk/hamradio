#!/usr/bin/env python3

import unittest
import os

from lib.common_libs.hamactivity import HamActivity
from lib.vkv_pa import VhfActHamActivity

class TestActivity(unittest.TestCase):

    def setUp(self):
        self.adif1 = 'test/examples/adif1.adif'

    def test_adif_import(self):
        self.assertTrue(os.path.isfile(self.adif1), "Check if %s exists." % self.adif1)
        act1 = HamActivity(adif_file=self.adif1)
        self.assertIsInstance(act1, HamActivity, 'Initiate a new HamActivity from an ADIF file')

    def test_saving(self):
        act1 = VhfActHamActivity(adif_file=self.adif1)
        act1.meta['gridsquare'] = 'JN88nc'

        act1_id = act1.store()
        self.assertIsInstance(act1_id, str, 'Application stored as a hash')
        act2 = VhfActHamActivity(id=act1_id)


        self.assertIsInstance(act2, VhfActHamActivity, 'Retrieve a HamActivity from storage')
        self.assertDictEqual(act1.meta, act2.meta)
        self.assertEqual(len(act1.qsos), len(act2.qsos))

        for (q1, q2) in zip(act1.qsos, act2.qsos):
            self.assertDictEqual(vars(q1), vars(q2), 'comparing individual QSOs')




