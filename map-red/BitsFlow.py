#!/usr/bin/env python
# -*- coding: utf-8 -*-

class BitStreamWriter:
    """ """
    def __init__(self):
        self.nbits  = 0
        self.curbyte = 0
        self.vbytes = []

    def add(self, bit):
        self.curbyte |= bit << (8-1 - (self.nbits % 8))
        self.nbits += 1

        if (self.nbits % 8 == 0):
            self.vbytes.append(chr(self.curbyte))
            self.curbyte = 0

    def getbytes(self):
        if (self.nbits & 7 == 0):
            return "".join(self.vbytes)
        return "".join(self.vbytes) + chr(self.curbyte)


class BitStreamReader:
    """ """
    def __init__(self, blob):
        self.blob = blob
        self.pos  = 0

    def get(self):
        ibyte = self.pos / 8
        ibit  = self.pos & 7

        self.pos += 1
        return (ord(self.blob[ibyte]) & (1 << (7 - ibit))) >> (7 - ibit)

    def finished(self):
        return self.pos >= len(self.blob) * 8

