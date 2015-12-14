#!/usr/bin python
# -*- coding: utf-8 -*-

class BitStreamWriter:
    """ """
    def __init__(self):
        self.nbits  = 0
        self.curbyte = 0
        self.vbytes = ''

    def add(self, bit):
        self.curbyte |= bit << (7 - (self.nbits % 8))
        self.nbits += 1

        if (self.nbits % 8 == 0):
            self.vbytes += chr(self.curbyte)
            self.curbyte = 0

    def getbytes(self):
        if (self.nbits & 7 == 0):
            return self.vbytes
        return self.vbytes + chr(self.curbyte)

    def clean(self):
        self.nbits  = 0
        self.curbyte = 0
        self.vbytes = ''


class BitStreamReader:
    """ """
    def __init__(self, blob):
        self.blob = blob
        self.bit_mask = 1 << 8
        self.curbyte_val = ord(blob[0])
        self.curbyte_pos = 0
        self.pos  = 0

    def get(self):
        self.bit_mask >>= 1
        if  self.bit_mask == 0:
            self.curbyte_pos += 1
            self.curbyte_val = ord(self.blob[self.curbyte_pos])
            self.bit_mask = 1 << 7
        self.pos += 1
        return int((self.curbyte_val & self.bit_mask) != 0)

    def finished(self):
        return self.pos >= len(self.blob) * 8

    def re_init(self, blob):
        self.blob = blob
        self.bit_mask = 1 << 7
        self.curbyte_val = ord(blob[0])
        self.curbyte_pos = 0
        self.pos = 0

