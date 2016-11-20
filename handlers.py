#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# when resource is both readable and writable
# then specify optional argument for a method to distinguish between reads and writes
# writable handler MUST return True or False in order to tell if it completed successfully or not


def read_manufacturer():
    return "Lenovo"

def handle_disable(params_list=None):
    print('elooooooooooooo')

_timezone = 'Europe/Warsaw'

def handle_timezone(arg=None):
    if arg is None:
        # handle read
        return _timezone
    else:
        # handle write
        global _timezone
        _timezone = arg
        return True

