#!/usr/bin/env python3

import unittest
import os

from lib.common.hamactivity import HamActivity

class TestActivity(unittest.TestCase):

    def setUp(self):
        self.adif1 = 'test/fixtures/adif1.adif'

    def test_adif_import(self):
        self.assertTrue(os.path.isfile(self.adif1), "Check if %s exists." % self.adif1)
        act1 = HamActivity(adif_file=self.adif1)
        self.assertIsInstance(act1, HamActivity, 'Initiate a new HamActivity from an ADIF file')

    def test_saving(self):
        act1 = HamActivity(adif_file=self.adif1)

        act1_id = act1.store()
        self.assertIsInstance(act1_id, str, 'Application stored as a hash')
        act2 = HamActivity(id=act1_id)


        self.assertIsInstance(act2, HamActivity, 'Retrieve a HamActivity from storage')
        self.assertDictEqual(act1.meta, act2.meta)
        self.assertEqual(len(act1.qsos), len(act2.qsos))

        for (q1, q2) in zip(act1.qsos, act2.qsos):
            self.assertDictEqual(vars(q1), vars(q2), 'comparing individual QSOs')

        self.assertIsInstance(act2.id, str)

        id = act2.id
        id_new = act2.store()

        self.assertEqual(id, act2.id, "ID stays the same after storing")
        self.assertEqual(id_new, id, "Store of an existing activity with an ID returns the same ID")

