#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import string
import csv
import string
import sys

def FilterData(l, column):
    answer = []
    for line in l:
        if len(line) > column:
            if len(line[column]) != 0:
                answer.append(line)

    return answer


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Filtra apenas as 4N produções, que estão marcadas na primeira coluna da entrada')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input CSV file')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output CSV file')
    parser.add_argument('-d', '--delimiter', type=str, required=False, help='CSV delimiter')

    args = parser.parse_args()

    delimiter = ';'
    if (args.delimiter != None):
        delimiter = args.delimiter

    print 'Lendo entrada...', args.input,
    inputData = list(csv.reader(open(args.input), delimiter=delimiter))
    print len(inputData), 'linhas lidas.'

    filteredData = FilterData(inputData, 0)

    print len(filteredData), 'linhas restantes.'

    if len(filteredData) == 0:
        print 'Nenhuma linha restante. Saindo...'
        sys.exit(0)

    print 'Gravando arquivo de saída...',
    csv.writer(open(args.output, 'wt'), delimiter=delimiter).writerows(filteredData)
