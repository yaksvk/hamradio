from ..common.hamactivity import HamActivity
from ..common.gridsquare import gridsquare2latlng, small_square_distance, is_gridsquare,\
    extract_gridsquare, dist_ham, gridsquare2latlngedges

class InvalidUsage(Exception):
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code



class VhfEdiActivity(HamActivity):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def calculate_scores(self):

        # required: self.gridsquare
        if 'gridsquare' not in self.meta or not self.meta['gridsquare']:
            raise InvalidUsage('Gridsquare is required for score calculation', status_code=500)

        for i, qso in enumerate(self.qsos):
            # fix numbers
            if not qso.stx:
                qso.stx = i + 1

            if not qso.srx:
                # if qso.srx_string is a number, use it as srx
                if qso.srx_string and qso.srx_string.isdigit():
                    qso.srx = int(qso.srx_string)

            if qso.gridsquare:
                qso.distance = dist_ham(self.meta['gridsquare'], qso.gridsquare)
            else:
                qso.points = 0
                qso.distance = 0