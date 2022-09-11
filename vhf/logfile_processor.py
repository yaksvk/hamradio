#!/usr/bin/env python3
import sys
import re

class LogfileProcessor:
    @staticmethod
    def get_processor(file_name):
        pass

    def __init__(self, from_file=None, from_string=None):

        self.qsos = []
        self.header = {}
        self.comments = {}

        if from_string is not None:
            self.init_from_string(from_string)
        elif from_file is not None:
            self.init_from_file(from_file)

    def init_from_file(self, log_file):
        with open(log_file) as f:
            data = f.read()
        self.init_from_string(data)

