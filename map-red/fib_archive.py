#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bisect import bisect
import zipimport
importer = zipimport.zipimporter('bs123.zip')
BitsFlow = importer.load_module('BitsFlow')
from BitsFlow import BitStreamReader, BitStreamWriter


# Fibonacci Series
class FibonacciArchiver(object):
    """ """
    def  __init__(self, max):
        """ """
        self.fib_series = []
        FibonacciArchiver.fibonacci_series(self.fib_series, max)

    @staticmethod
    def  fibonacci_series(fib_series, max):
        """ """
        (first, second, next) = (0, 1, 0)
        while (max >= next):
            next = first + second
            first, second = second, next
            fib_series.append(next)

    def    code(self, data, verbose=False):
        """ Найти max число Фибоначчи
            отнять, найти, отнять...
            получить последовательность 1 и нулей
            развернуть её, записать 1, записать в файл

            data - list
        """
        all_bits = []
        for number in data:
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

            if verbose:
                print '\n', ''.join(str(b) for b in bits[::-1])
            all_bits += bits[::-1]

        bw = BitStreamWriter()
        for b in all_bits:
            bw.add(b)
        return bw.getbytes()

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
                    if verbose: print ''.join(str(b) for b in bits)
                    bits = bits[:-1]

                number = 0
                for i,b in enumerate(bits):
                    number += b * self.fib_series[i]

                if verbose: print number
                decoded.append(number)
                bits = []
            else:
                bits.append(bit)

        return decoded


if __name__ == '__main__':
    with open('data/nums.uniq.txt','r') as file:
        numbers = map(int, file.readlines())

    fib = FibonacciArchiver( numbers[-1] + 7 )
    coded = fib.code(numbers)
    decoded = fib.decode(coded)

    for i,j in zip(decoded, numbers):
        if i != j:
            print i,j



