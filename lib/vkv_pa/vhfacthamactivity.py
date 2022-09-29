from ..common.adif import Adif
from ..common.hamactivity import HamActivity
from ..common.gridsquare import gridsquare2latlng, small_square_distance, is_gridsquare,\
    extract_gridsquare, dist_ham, gridsquare2latlngedges

class VhfActHamActivity(HamActivity):

    @staticmethod
    def points(point_distance):
        return 2 + point_distance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def calculate_scores(self):
        self.meta['comments'] = {}
        self.meta['scores'] = {}

        if self.meta.get('gridsquare'):
            self.meta['latlng'] = gridsquare2latlng(self.meta['gridsquare'])
            self.meta['latlng_edges'] = gridsquare2latlngedges(self.meta['gridsquare'])
            self.meta['latlng_large_edges'] = gridsquare2latlngedges(self.meta['gridsquare'][0:4])
        else:
            print('there is no gridsquare in meta')

        # calculate distances
        for qso in self.qsos:
            if self.meta['latlng'] and qso.latlng:
                qso.distance = dist_ham(self.meta['latlng'], qso.latlng)

            if self.meta['gridsquare'] and qso.gridsquare:
                qso.points = self.points(small_square_distance(self.meta['gridsquare'], qso.gridsquare))

        # pick qsos with max 3 distances
        top_qsos = sorted(self.qsos,key=lambda x: -x.distance)[:3]
        for qso in self.qsos:
            if qso in top_qsos:
                qso.top_distance = True

        orig_qsos = {}
        orig_gridsquares = {}
        orig_large_gridsquares = {}

        # my own gridsquare is a natural multiplier
        orig_gridsquares[self.meta['gridsquare']] = 1
        orig_large_gridsquares[self.meta['gridsquare'][0:4].upper()] = 1

        for qso in self.qsos:
            ident = qso.call + getattr(qso, 'band', getattr(qso, 'freq', ''))
            if qso.gridsquare:
                orig_qsos[ident] = qso.gridsquare
                orig_gridsquares[qso.gridsquare] = orig_gridsquares.get(qso.gridsquare, 0) + 1
                orig_large_gridsquares[qso.gridsquare[0:4].upper()] = orig_large_gridsquares.get(qso.gridsquare[0:4].upper(), 0) + 1

        # compute scores
        score = 0
        max_dist = 0
        locator_max = ''

        for qth in orig_qsos.values():
            if (self.meta.get('gridsquare', None) and qth):
                dist = small_square_distance(self.meta['gridsquare'], qth)
                score += self.points(dist)
                if dist > max_dist:
                    max_dist = dist
                    locator_max = qth

        self.meta['scores'] = {
            'original_qso_count' : len(orig_qsos.values()),
            'multiplier_count' : len(orig_large_gridsquares.keys()),
            'score' : score,
            'score_multiplied': score*len(orig_large_gridsquares.keys()),
            'max_gridsquare' : locator_max,
            'multipliers' : orig_large_gridsquares.keys(),
            'paint_squares' : list(map(lambda x: gridsquare2latlngedges(x), orig_large_gridsquares.keys())),
            'max_dist' : max_dist
        }
