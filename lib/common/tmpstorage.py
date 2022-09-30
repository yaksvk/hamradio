#!/usr/bin/env python

"""
A primitive storage handler that saves and loads
dictionaries as tmpfiles.
"""

import os
import pickle
import re
import tempfile

DIR='/tmp'
PREFIX='log_'

class TmpStorage:

    def __init__(self, dir=None, prefix=None) -> None:
        self.dir = dir if dir else DIR
        self.prefix = prefix if prefix else PREFIX


    def save(self, input_data, id=None) -> str:

        file = None;
        if id is not None:
            file = open(os.path.join(
                self.dir,
                f'{self.prefix}{id}',
            ), "wb")
        else:
            file = tempfile.NamedTemporaryFile(
                delete=False,
                prefix=self.prefix,
                dir=self.dir
            )

        pickle.dump(input_data, file)

        if file is not None:
            file.close()

        return re.sub(
            rf'^{self.prefix}',
            '',
            os.path.basename(file.name)
        )


    def load(self, id) -> dict:
        if re.match('^\w+$', id):
            with (open(os.path.join(
                self.dir,
                f'{self.prefix}{id}'
            ),"rb")) as picklefile:
                return pickle.load(picklefile)
