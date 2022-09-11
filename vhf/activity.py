#!/usr/bin/env python3
import re
import sys

from .adif import Adif
from .gridsquare import gridsquare2latlng, small_square_distance, is_gridsquare, extract_gridsquare, dist_ham, gridsquare2latlngedges

class Qso:
    def __init__(self, adif_vars):
        self.distance = 0
        self.points = 0
        self.top_distance = False
        self.gridsquare = None
        self.rst_rcvd = None
        self.rst_sent = None
        self.stx = None
        self.srx = None
        self.latlng = None

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

class Log:
    @staticmethod
    def points(point_distance):
        return 2 + point_distance

    def __init__(self, gridsquare=None, adif_file=None, dictionary=None):
        self.qsos = []
        self.comments = {}
        self.scores = {}
        self.gridsquare = None
        self.latlng = None
        self.latlng_edges = None
        self.latlng_large_edges = None

        if adif_file is not None:
            self.init_from_adif(adif_file)

        if dictionary is not None:
            self.init_from_dictionary(dictionary)

        # init my gridsquare from self qsos
        for qso in self.qsos:
            if hasattr(qso, 'my_gridsquare'):
                self.gridsquare = qso.my_gridsquare
                break

        # try to get gridsquare from comments
        if not self.gridsquare and 'PWWLO' in self.comments:
            self.gridsquare = self.comments['PWWLO']

        # override gridsquare if given in argument instead of looking
        # for it in the adif 
        if gridsquare is not None and is_gridsquare(gridsquare):
            self.gridsquare = gridsquare

        if self.gridsquare:
            self.latlng = gridsquare2latlng(self.gridsquare)
            self.latlng_edges = gridsquare2latlngedges(self.gridsquare)
            self.latlng_large_edges = gridsquare2latlngedges(self.gridsquare[0:4])

        # calculate distances
        for qso in self.qsos:
            if self.latlng and qso.latlng:
                qso.distance = dist_ham(self.latlng, qso.latlng)

            if self.gridsquare and qso.gridsquare:
                qso.points = self.points(small_square_distance(self.gridsquare, qso.gridsquare))

        # pick qsos with max 3 distances
        top_qsos = sorted(self.qsos,key=lambda x: -x.distance)[:3]
        for qso in self.qsos:
            if qso in top_qsos:
                qso.top_distance = True

        self.compute_scores()


    def init_from_adif(self, adif_file):
        adif = Adif(from_file=adif_file)

        for item in adif.qsos:
            qso = Qso(item['adif_vars'])
            self.qsos.append(qso)

        self.qsos.sort(key = lambda x: (x.qso_date, x.time_on))
        self.comments = adif.comments

    def init_from_dictionary(self, dictionary):
        self.comments = dictionary.get('comments', None)
        self.gridsquare = dictionary.get('gridsquare', None)

        # qsos
        for item in dictionary.get('qsos', []):
            self.qsos.append(Qso(item))

    def compute_scores(self):
        # return all the scores

        orig_qsos = {}
        orig_gridsquares = {}
        orig_large_gridsquares = {}

        # my own gridsquare is a natural multiplier
        orig_gridsquares[self.gridsquare] = 1

        for qso in self.qsos:
            ident = qso.call + getattr(qso, 'band', getattr(qso, 'freq', ''))
            if qso.gridsquare:
                orig_qsos[ident] = qso.gridsquare
                orig_gridsquares[qso.gridsquare] = orig_gridsquares.get(qso.gridsquare, 0) + 1
                orig_large_gridsquares[qso.gridsquare[0:4]] = orig_large_gridsquares.get(qso.gridsquare[0:4], 0) + 1

        # compute scores
        score = 0
        max_dist = 0
        locator_max = ''

        for qth in orig_qsos.values():
            if (self.gridsquare and qth):
                dist = small_square_distance(self.gridsquare, qth)
                score += self.points(dist)
                if dist > max_dist:
                    max_dist = dist
                    locator_max = qth

        self.scores = {
            'original_qso_count' : len(orig_qsos.values()),
            'multiplier_count' : len(orig_large_gridsquares.keys()),
            'score' : score,
            'score_multiplied': score*len(orig_large_gridsquares.keys()),
            'max_gridsquare' : locator_max,
            'multipliers' : orig_large_gridsquares.keys(),
            'paint_squares' : list(map(lambda x: gridsquare2latlngedges(x), orig_large_gridsquares.keys())),
            'max_dist' : max_dist
        }
        return self.scores

    def export_dictionary(self):
        return {
            'comments': self.comments,
            'gridsquare': self.gridsquare,
            'qsos': [ dict(vars(qso).items()) for qso in self.qsos ]
        }

if __name__ == '__main__':
    if len(sys.argv) > 1:
        log = Log('JN88le', sys.argv[1])
        print('My square: %s' % log.gridsquare)
        for qso in log.qsos:
            print(qso.call)
