#!/usr/bin python
# -*- coding: utf-8 -*-

from bisect import bisect
# import zipimport
# importer = zipimport.zipimporter('bs123.zip')
# BitsFlow = importer.load_module('BitsFlow')
from BitsFlow import BitStreamReader, BitStreamWriter


class FibonacciArchiver(object):
    """ """
    def  __init__(self, max=34):
        """ """
        self.fib_series = []
        self.fibonacci_init_series(max)

    def  fibonacci_init_series(self, max):
        """ """
        (first, second, next) = (0, 1, 0)
        while (max >= next):
            next = first + second
            first, second = second, next
            self.fib_series.append(next)

    def  fibonacci_to_upper(self, upper_bound):
        while self.fib_series[-1] <= upper_bound:
            self.fib_series.append(self.fib_series[-1] + self.fib_series[-2])

    def  fibonacci_to_index(self, index):
        while len(self.fib_series) <= index:
            self.fib_series.append(self.fib_series[-1] + self.fib_series[-2])

    def    code(self, data, verbose=False):
        """ Найти max число Фибоначчи
            отнять, найти, отнять...
            получить последовательность 1 и нулей
            развернуть её, записать 1, записать в файл

            data - list
        """
        all_bits = []
        for number in data:

            if number <= 0:
                raise ValueError("Fibonacci archiver: can't " + \
                                 "code non-positive integer " + str(number))

            self.fibonacci_to_upper(number)

            bits = [1]
            if verbose: print "number=%d\n" % number

            index = 0
            while number:
                n_index = bisect(self.fib_series, number) - 1
                if verbose: print number, self.fib_series[n_index]
                number -= self.fib_series[n_index]

                if verbose:
                    print ('index=%d  fib=%d  number=%d' %
                           (n_index, self.fib_series[n_index], number))

                for i in range(index - n_index - 1):
                    bits.append(0)
                bits.append(1)
                index = n_index

            while index:
                bits.append(0)
                index -= 1

            if verbose: print '\n', ''.join(str(b) for b in bits[::-1])
            all_bits += bits[::-1]

        bw = BitStreamWriter()
        for b in all_bits:
            bw.add(b)

        decoded = bw.getbytes()
        bw.clean()
        return decoded

    def  decode(self, data, verbose=False):
        """ Найти 2 единицы, убрать последнюю
            развернуть последовательность,
            получить цифру

            data - binary
        """
        bits, decoded = [], []

        br = BitStreamReader(data)
        while not br.finished():
            bit = br.get()
            
            if bit and bits and bits[-1]:                
                if verbose:
                    bits.append(bit)
                    if verbose: print ''.join(str(int(b)) for b in bits)
                    bits = bits[:-1]

                number = 0
                for i,b in enumerate(bits):
                    self.fibonacci_to_index(i)
                    number += b * self.fib_series[i]

                if verbose: print number
                decoded.append(number)
                bits = []
            else:
                bits.append(bit)

        return map(int,decoded)


def incorr(decoded, numbers):
    for i,j in zip(decoded, numbers):
        if i != j:
            print i, '!=', j

if __name__ == '__main__':

    fib = FibonacciArchiver()

    numbers = [ 1 ] * 28
    # print len(numbers)
    coded   = fib.code(numbers)
    # for byte in coded:
    #     print bin(ord(byte)),
    # print
    incorr(fib.decode(coded), numbers)

    numbers = [1,3] * 7
    # print len(numbers)
    coded   = fib.code(numbers)
    incorr(fib.decode(coded), numbers)

    numbers = [3,5,7] * 3
    # print len(numbers)
    coded   = fib.code(numbers)
    incorr(fib.decode(coded), numbers)

    numbers = [10, 15] * 3 + [15]
    # print len(numbers)
    coded   = fib.code(numbers)
    incorr(fib.decode(coded), numbers)

    numbers = [16, 11, 12, 19, 31] + [16381, 16382] + [ 268435455 ]
    # print len(numbers)
    coded   = fib.code(numbers)
    incorr(fib.decode(coded), numbers)

    with open('data/nums.uniq.txt','r') as file:
        numbers = map(int, file.readlines())

    import time
    start_time = time.time()
    
    coded   = fib.code(numbers)
    decoded = fib.decode(coded)

    print "%.3f sec." % (time.time() - start_time)
    incorr(decoded, numbers)



