#!/usr/bin python
# -*- coding: utf-8 -*-

# import zipimport
# importer = zipimport.zipimporter('bs123.zip')
# BitsFlow = importer.load_module('BitsFlow')
from BitsFlow import BitStreamReader, BitStreamWriter


class Simple9Archiver(object):
    """ Simple9 - код, выравненный по 32 бита.
            4 бита, 28 бит
        управление, данные
            0     ,    1  - 28-битное   268 435 455
            1     ,    2  - 14-битных    16 383
            2     ,    3  -  9-битных   511  ---------  +1
            3     ,    4  -  7-битных   127
            4     ,    5  -  5-битных   31   ---------  +3
            5     ,    7  -  4-битных   15
            6     ,    9  -  3-битных   7    ---------  +1
            7     ,    14 -  2-битных   3|0|1|2
            8     ,    28 -  1-битных   1|0
        > 28-бит ???
    """
    def __init__(self):
        """ """
        self.n_ctrl = 4
        self.n_data = 28
        self.bw = BitStreamWriter()
        self.borders = ( (28,1), (14,3), (9,7), (7,15), \
                         (5,31), (4,127), (3,511), \
                         (2,16383), (1,268435455) )
        self.counts = ( 1, 2, 3, 4, 5, 7, 9, 14, 28 )
        self.border = [ 1, 3, 7, 15, 31, 127, 511, 16383, 268435455 ]



    @staticmethod
    def bits(n):
        """ Bits of 4byte """
        return [n >> i & 1 for i in range(31,-1,-1)]

    def    code(self, data, verbose=False):
        """ Return coded sequence """
        index = 0
        bw = BitStreamWriter()
        while index < len(data):

            for n,border in zip(xrange(len(self.border),0,-1), self.border):
                data1 = data[index:index + self.counts[n - 1] ]
                if verbose: print n, data1
                if (len(data1) == self.counts[n - 1]) and all([ d <= border for d in data1 ]):
                    if verbose: print ''.join([ str(bit) for bit in self.bits(n - 1)[-self.n_ctrl:] ]), '  ',
                    for bit in self.bits(n - 1)[-self.n_ctrl:]:
                        bw.add(bit)

                    for number in data1:
                        if verbose: print ''.join([ str(b) for b in self.bits(number)[-(self.n_data / self.counts[n - 1]):] ]),
                        for bit in self.bits(number)[-(self.n_data / self.counts[n - 1]):]:
                            bw.add(bit)
                    
                    if n == 7 or n == 3:
                        if verbose:  print '0'
                        bw.add(0)
                    elif n == 5:
                        if verbose:  print '000'
                        for i in xrange(3):
                            bw.add(0)
                    elif verbose: print
                    index += self.counts[n - 1]
                    break

            else: raise ValueError
        return bw.getbytes()

    def    code1(self, data, verbose=False):
        """ Return coded sequence """
        index = 0
        while index < len(data):

            n = (len(self.borders) - 1)
            for count, border in self.borders:

                batch = data[index:index + count]
                if verbose: print n, batch

                if  all([ 0 < d <= border for d in batch ]):
                    if verbose: print ''.join([ str(bit) for bit in self.bits(n)[-self.n_ctrl:] ]), '  ',
                    for bit in self.bits(n)[-self.n_ctrl:]:
                        self.bw.add(bit)

                    for number in batch:
                        if verbose: print ''.join([ str(b) for b in self.bits(number)[-(self.n_data / count):] ]),
                        for bit in self.bits(number)[-(self.n_data / count):]:
                            self.bw.add(bit)
                    
                    if n == 6 or n == 2:
                        if verbose:  print '0'
                        self.bw.add(0)
                    elif n == 4:
                        if verbose:  print '000'
                        for i in xrange(3):
                            self.bw.add(0)
                    elif verbose: print
                    index += count
                    break
                n -= 1

            else: raise ValueError("Simple9 archiver: number is too big")
        coded = self.bw.getbytes()
        self.bw.clean()
        return coded

    def  decode1(self, data, verbose=False):
        """ Return decoded sequence """
        decoded = []
        if verbose: print

        coded, j, k, control = [0] * self.n_data, 0, 0, 0
        br = BitStreamReader(data)
        while not br.finished():
            bit = br.get()

            if j < self.n_ctrl:
                control |= (bit << ((self.n_ctrl - 1) - j))
                j += 1
            else:
                coded[k] = bit
                k += 1
            
                if k >= self.n_data:                    
                    n_bits   = (self.borders[control][0] - 1)

                    if verbose:
                        print ''.join([ str(b) for b in self.bits(control)[-self.n_ctrl:]]), '  ',
                        print ''.join([ str(c) for c in coded[:k]])

                    count = self.counts[control]
                    n_packed = (self.n_data / count)

                    for n in xrange(count):
                        number = 0
                        for m in xrange(n_packed):
                            index = n * n_packed + m
                            number |= ((1 if coded[index] else 0) << (n_bits - m))
                        decoded.append(number)

                    if verbose: print decoded[-count:]
                    j, k, control = 0, 0, 0

        return decoded

    def  decode(self, data, verbose=False):
        """ Return decoded sequence """
        decoded = []
        if verbose: print

        coded, j, k, control = [0] * self.n_data, 0, 0, 0
        br = BitStreamReader(data)
        while not br.finished():
            bit = br.get()

            if j < self.n_ctrl:
                control |= (bit << ((self.n_ctrl - 1) - j))
                j += 1
            else:
                coded[k] = bit
                k += 1
            
                if k >= self.n_data:                    
                    n_bits   = (self.counts[::-1][control] - 1)

                    if verbose:
                        print ''.join([ str(b) for b in self.bits(control)[-self.n_ctrl:]]), '  ',
                        print ''.join([ str(c) for c in coded[:k]])

                    n_packed = (self.n_data / (self.counts[control]))
                    for n in xrange(self.counts[control]):
                        number = 0
                        for m in xrange(n_packed):
                            index = n * n_packed + m
                            number |= ((1 if coded[index] else 0) << (n_bits - m))
                        decoded.append(number)

                    if verbose: print decoded[-self.counts[control]:]
                    j, k, control = 0, 0, 0

        return decoded



def incorr(decoded, numbers):
    for i,j in zip(decoded, numbers):
        if i != j:
            print i, '!=', j

if __name__ == '__main__':

    s9 = Simple9Archiver()
    
    numbers = [ 1 ] * 28
    # print len(numbers)
    coded   = s9.code(numbers) #, verbose=True)
    # print s9.decode(coded)
    incorr (s9.decode(coded), numbers)

    numbers = [1,3] * 7
    # print len(numbers)
    coded   = s9.code(numbers) #, verbose=True)
    # print s9.decode(coded)
    incorr (s9.decode(coded), numbers)

    numbers = [3,5,7] * 3
    # print len(numbers)
    coded   = s9.code(numbers) #, verbose=True)
    # print s9.decode(coded)
    incorr (s9.decode(coded), numbers)

    numbers = [10, 15] * 3 + [15]
    # print len(numbers)
    coded   = s9.code(numbers) #, verbose=True)
    # print s9.decode(coded)
    incorr (s9.decode(coded), numbers)

    numbers = [16, 11, 12, 19, 31] + [16381, 16382] + [ 268435455 ]
    # print len(numbers)
    coded   = s9.code(numbers) #, verbose=True)
    # print s9.decode(coded)
    incorr (s9.decode(coded), numbers)

    # br = BitStreamReader(coded)
    # Bits = []
    # while not br.finished():
    #     Bits.append(str(br.get()))
    # print ''.join(Bits)

    with open('data/nums.uniq.txt','r') as file:
        numbers = map(int, file.readlines())

    print len(numbers)
    import time
    start_time = time.time()
    coded   = s9.code(numbers) #, verbose=True)
    decoded = s9.decode(coded)

    print "%.3f sec." % (time.time() - start_time)
    # print decoded

    incorr (s9.decode(coded), numbers)
