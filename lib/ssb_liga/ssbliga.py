from ..common.hamactivity import HamActivity
from ..common.gridsquare import gridsquare2latlng, small_square_distance, is_gridsquare,\
    extract_gridsquare, dist_ham, gridsquare2latlngedges

class SsbActivity(HamActivity):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
