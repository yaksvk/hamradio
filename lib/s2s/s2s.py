from ..common.hamactivity import HamActivity, Qso
from ..common.tmpstorage import TmpStorage
import csv

class S2s(HamActivity):

    def __init__(self, csv_file=None, id=None):
        self.id = None
        self.meta = {}
        self.qsos = []
        self.storage = TmpStorage()

        if csv_file is not None:
            self.init_from_csv(csv_file=csv_file)
        elif id is not None:
            self.init_from_storage(id)

    def init_from_csv(self, csv_file):
        with open(csv_file) as summitfile:
            sota_reader = csv.reader(summitfile, delimiter=';', quotechar='"')
            for row in sota_reader:
                qso = Qso(qso_dict={
                    'at_' + str(i): j for i, j in enumerate(row)
                })
                self.qsos.append(qso)
