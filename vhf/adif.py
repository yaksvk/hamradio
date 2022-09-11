#!/usr/bin/env python3
import sys
import re

from .logfile_processor import LogfileProcessor

class Adif(LogfileProcessor):
    @staticmethod
    def can_process(text):
        # returns true if this can parse a text, false if not, should return true for ADIF file contents
        variables = re.findall('<(\w+):(\d+)>([^<]+)', text)
        eors = re.findall('(<eor>)', text, flags=re.IGNORECASE)
        return len(variables) > 0 and len(eors) > 0

    @staticmethod
    def process_adif_variables(text):
        # ADIF = <variable_name:length>value\s - and substring the value according to
        # length. This should probably be read sequentially, not as a regexp. (value with < will probably suck)
        variables = re.findall('<(\w+):(\d+)(:\w)?>([^<]+)', text)
        adif_vars = dict((var[0].upper(), var[3][:int(var[1])]) for var in variables)
        return adif_vars

    @staticmethod
    def process_header_comments(text):
        variables = re.findall('((\w+)=(\w+))\n', text)
        comments = dict((var[1].upper(), var[2]) for var in variables)
        return comments

    def init_from_string(self, adif_string):
        # process header 
        res = re.findall("^(.*?)<EOH>", adif_string, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
        if res:
            header = res[0]
            # attempt to populate header values using standard adif variable parsing from header
            self.header = self.process_adif_variables(header)
            # try also the var=val method
            self.comments = self.process_header_comments(header)


        # ignore header
        data = re.sub("^.*<EOH>", "", adif_string, flags=re.IGNORECASE)
        items = [ item.strip() for item in re.split("<EOR>", data, flags=re.IGNORECASE) ]

        # process QSOs
        for item in items:
            # process QSO variables
            adif_vars = self.process_adif_variables(item)
            
            # variable postprocessing
            # 1. some software puts SRX and STX to _STRING variables. Attempt to extract these.
            if ('SRX' not in adif_vars 
                and 'STX' not in adif_vars
                and 'SRX_STRING' in adif_vars
                and 'STX_STRING' in adif_vars):

                stx = re.findall('^(\d+)', adif_vars['STX_STRING'])
                srx = re.findall('^(\d+)', adif_vars['SRX_STRING'])

                if stx and srx:
                    adif_vars['STX'] = stx[0]
                    adif_vars['SRX'] = srx[0]

            if 'CALL' in adif_vars:
                self.qsos.append({'adif_vars': adif_vars})


if __name__ == '__main__':
    if len(sys.argv) > 1:
        adif = Adif(from_file=sys.argv[1])

        for qso in adif.qsos:
            print(qso['adif_vars'].get('CALL'))
            
    else:
        print("Please supply filename as an argument")

    
    
