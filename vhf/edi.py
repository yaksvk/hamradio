#!/usr/bin/env python3
import sys
import re

from .logfile_processor import LogfileProcessor

class Edi(LogfileProcessor):
    @staticmethod
    def can_process(text):
        return False
