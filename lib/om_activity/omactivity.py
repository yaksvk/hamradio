from ..common.hamactivity import HamActivity
import re

class OmActivity(HamActivity):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def pre_process(self):
        for qso in self.qsos:
            if qso.srx and qso.stx:
                continue

            if qso.srx_string and qso.stx_string:
                if re.match('^\d{3}$', getattr(qso, 'srx_string', '')) and re.match('^\d{3}$', getattr(qso, 'stx_string', '')):
                    qso.srx, qso.stx = qso.srx_string, qso.stx_string
                    continue

            # support nums in qso comments like "001 123 blah blah" => STX:001 SRX:123
            match = re.findall('^((\d+) (\d+))\s?', getattr(qso, 'comment',''))
            if match and len(match[0]) == 3:
                qso.srx, qso.stx = match[0][2], match[0][1]
