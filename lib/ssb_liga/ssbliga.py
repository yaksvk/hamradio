from ..common.hamactivity import HamActivity
from ..common.gridsquare import gridsquare2latlng, small_square_distance, is_gridsquare,\
    extract_gridsquare, dist_ham, gridsquare2latlngedges
import re

class SsbLiga(HamActivity):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def pre_process(self):
        for qso in self.qsos:
            if qso.srx_string:
                qso.srx_string = qso.srx_string.upper()
                continue

            if re.match('^[A-Za-z]{3}$', str(getattr(qso, 'srx', ''))):
                qso.srx_string = qso.srx.upper()
                continue

            if re.match('^[A-Za-z]{3}$', getattr(qso, 'qth', '')):
                qso.srx_string = qso.qth.upper()
                continue

            match = re.findall('^([A-Za-z]{3})\s?', getattr(qso, 'comment',''))
            if match:
                qso.srx_string = match[0].upper()
