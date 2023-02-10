#!/usr/bin/env python

import re

from typing import Optional

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
        self.srx_string = None
        self.stx_string = None
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

    def _probe_gridsquare(self, adif_vars: dict) -> Optional[str]:
            gridsquare = self.gridsquare
            # try to extract gridsquare from the qso
            srx_grid = extract_gridsquare(adif_vars.get('SRX_STRING', ''))
            if srx_grid:
                gridsquare = srx_grid

            # if we still don't have the gridsquare, try to guess it from qth
            if  not gridsquare and hasattr(self, 'qth'):
                qth = getattr(self, 'qth')
                if is_gridsquare(qth):
                    gridsquare = qth

                # if we still have nothing, try to extract gridsquare from QTH
                else:
                    guess = extract_gridsquare(qth)
                    if guess is not None:
                        gridsquare = guess

            if not gridsquare and hasattr(self, 'comment'):
                # fall back to guessing gridsquare from comment
                if hasattr(self, 'comment'):
                    guess = extract_gridsquare(getattr(self, 'comment'))
                    if guess is not None:
                        gridsquare = guess

            # final check
            if not is_gridsquare(gridsquare):
                gridsquare = None

            return gridsquare


class HamActivity:

    def __init__(self, adif_file=None, id=None):
        self.id = None
        self.meta = {}
        self.qsos = []
        self.storage = TmpStorage()

        if adif_file is not None:
            self.init_from_adif(adif_file)
        elif id is not None:
            self.init_from_storage(id)

    def init_from_adif(self, adif_file: str) -> None:

        adif = Adif(from_file=adif_file)
        for item in adif.qsos:
            qso = Qso(item['adif_vars'])
            self.qsos.append(qso)


    def init_from_gui(self) -> None:
        ...


    def init_from_storage(self, id: str) -> None:
        data = self.storage.load(id)

        self.id = id
        self.meta = data['meta']
        self.qsos = [ Qso(qso_dict=item) for item in data['qsos'] ]


    def store(self) -> str:
        self.id = self.storage.save(
            self.__dict__(),
            self.id
        )
        return self.id

    def __dict__(self):
        return { 'meta': self.meta, 'qsos': [ vars(qso) for qso in self.qsos ] }

