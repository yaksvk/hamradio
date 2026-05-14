#!/usr/bin/env python3

import csv
from ctyparser import BigCty
from pathlib import Path

current_dir = Path(__file__).resolve().parent

class DXCC:
    def __init__(self):
        self.cty = BigCty()
        self.cty.import_dat(current_dir / "data/cty.dat")
        self.entity_code_map = {}

        with open(current_dir / "data/cty.csv", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) < 2:
                    continue
                entity = row[1].strip()
                code = row[2].strip()
                if entity and code:
                    self.entity_code_map[entity.lower()] = code

    def lookup_callsign(self, call):
        call = call.upper()

        best_match = None
        best_prefix = ""

        for prefix in self.cty.keys():
            if call.startswith(prefix):
                if len(prefix) > len(best_prefix):
                    best_prefix = prefix
                    best_match = self.cty[prefix]

        return best_match
    
    def entity_or_na(self, callsign):
        result = self.lookup_callsign(callsign)
        return result['entity'] if result else 'N/A'
    
    def entity_to_code(self, entity):
        if not entity:
            return None
        return self.entity_code_map.get(entity.strip().lower())
    