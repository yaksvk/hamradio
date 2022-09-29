#!/usr/bin/env python

import re

from .tmpstorage import TmpStorage
from .adif import Adif
from .gridsquare import gridsquare2latlng, small_square_distance, is_gridsquare,\
    extract_gridsquare, dist_ham, gridsquare2latlngedges

class Qso:
    def __init__(self, adif_vars=None, qso_dict=None):
        self.distance = 0
        self.points = 0
        self.top_distance = False
        self.gridsquare = None
        self.rst_rcvd = None
        self.rst_sent = None
        self.stx = None
        self.srx = None
        self.latlng = None

        if qso_dict is not None:
            for key, value in qso_dict.items():
                setattr(self, key, value)
        elif adif_vars is not None:
            # init qso object from adif_vars (dictionary)
            for key, value in adif_vars.items():
                setattr(self, key.lower(), value)

            # try to probe a gridsqure for this QSO with various priorities
            self.gridsquare = self._probe_gridsquare(adif_vars)

            # process ADIF vars and set gridsquares, etc.
            if hasattr(self, 'gridsquare') and self.gridsquare:
                self.latlng = gridsquare2latlng(self.gridsquare)

    def _probe_gridsquare(self, adif_vars):
            gridsquare = self.gridsquare
            # try to extract gridsquare from the qso
            srx_grid = extract_gridsquare(adif_vars.get('SRX_STRING', ''))
            if srx_grid:
                gridsquare = srx_grid

            # if we still don't have the gridsquare, try to guess it from qth
            if  not gridsquare and hasattr(self, 'qth'):
                if is_gridsquare(self.qth):
                    gridsquare = self.qth

                # if we still have nothing, try to extract gridsquare from QTH
                else:
                    guess = extract_gridsquare(self.qth)
                    if guess is not None:
                        gridsquare = guess

            if not gridsquare and hasattr(self, 'comment'):
                # fall back to guessing gridsquare from comment
                if self.comment:
                    guess = extract_gridsquare(self.comment)
                    if guess is not None:
                        gridsquare = guess

            # final check
            if not is_gridsquare(gridsquare):
                gridsquare = None

            return gridsquare


class HamActivity:

    def __init__(self, adif_file=None, id=None):
        self.meta = {}
        self.qsos = []
        self.storage = TmpStorage()

        if adif_file is not None:
            self.init_from_adif(adif_file)
        elif id is not None:
            self.init_from_storage(id)

    def init_from_adif(self, adif_file):

        adif = Adif(from_file=adif_file)
        for item in adif.qsos:
            qso = Qso(item['adif_vars'])
            self.qsos.append(qso)


    def init_from_gui(self):
        ...


    def init_from_storage(self, id) -> None:
        data = self.storage.load(id)

        self.meta = data['meta']
        self.qsos = [ Qso(qso_dict=item) for item in data['qsos'] ]


    def store(self) -> str:
        return self.storage.save(
            self.__dict__()
        )

    def __dict__(self):
        return { 'meta': self.meta, 'qsos': [ vars(qso) for qso in self.qsos ] }

